import re
import os
import requests
from models.metric_result import MetricResult
from utils.helpers import get_status
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


def extract_content_signals(soup):
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) > 30]

    if not paragraphs:
        return None

    sentences = []
    for para in paragraphs[:10]:
        sentences.extend(re.split(r'(?<=[.!?])\s+', para))

    sentences = [s for s in sentences if len(s) > 10]
    if not sentences:
        return None

    sentence_lengths = [len(s.split()) for s in sentences]
    avg_length = sum(sentence_lengths) / len(sentence_lengths)
    variance = sum((l - avg_length) ** 2 for l in sentence_lengths) / len(sentence_lengths)

    full_text = " ".join(paragraphs[:10]).lower()
    personal_pronouns = len(re.findall(r'\b(i|we|my|our|i\'ve|we\'ve|i\'m)\b', full_text))
    first_person_anecdotes = len(re.findall(r'\b(i found|we found|i tested|we tested|in my experience|in our experience)\b', full_text))

    return {
        "avg_sentence_length": round(avg_length, 1),
        "sentence_length_variance": round(variance, 1),
        "personal_pronoun_frequency": personal_pronouns,
        "first_person_anecdotes": first_person_anecdotes,
        "paragraphs_analyzed": len(paragraphs[:10])
    }


def call_ai(signals):
    if not ANTHROPIC_API_KEY:
        return None

    prompt = f"""Based on these content pattern signals from a webpage, rate the likelihood this is mass-produced AI-generated content.

Signals:
- Average sentence length: {signals['avg_sentence_length']} words
- Sentence length variance: {signals['sentence_length_variance']} (low = uniform = AI signal)
- Personal pronoun count: {signals['personal_pronoun_frequency']} (low = AI signal)
- First person anecdotes: {signals['first_person_anecdotes']} (low = AI signal)

Rate as: High / Medium / Low
Then one line of reasoning.
Format: RATING: <rating> | REASON: <reason>"""

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 100,
            "messages": [{"role": "user", "content": prompt}]
        },
        timeout=15
    )
    return response.json()["content"][0]["text"].strip()


def run(site_data):
    result = MetricResult(factor="196 - AI Footprints")

    try:
        signals = extract_content_signals(site_data.soup)

        if not signals:
            result.error = "Not enough content to analyze"
            return result.to_dict()

        result.details["signals"] = signals

        ai_response = call_ai(signals)

        if not ai_response:
            result.error = "Anthropic API key not configured"
            return result.to_dict()

        result.details["ai_response"] = ai_response

        rating = "medium"
        if "RATING: High" in ai_response:
            rating = "high"
        elif "RATING: Low" in ai_response:
            rating = "low"

        score_map = {"low": 100, "medium": 60, "high": 20}
        result.score = score_map[rating]
        result.status = get_status(result.score)

        if rating == "high":
            result.recommendations.append(
                "Content shows strong AI-generation patterns — low sentence variance, "
                "few personal pronouns, no first-hand anecdotes. "
                "Add original insights, personal experience, and varied sentence structure."
            )
        elif rating == "medium":
            result.recommendations.append(
                "Content shows some AI-generation signals. "
                "Consider adding more personal perspective and varied writing style."
            )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()