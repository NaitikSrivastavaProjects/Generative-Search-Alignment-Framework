import os
import json
import re
import requests
import spacy
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

nlp = spacy.load("en_core_web_sm")


# --- data extraction helpers ---

def extract_entities(soup):
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")[:15]]
    text = " ".join(paragraphs)[:5000]
    doc = nlp(text)
    entities = list(set(ent.text for ent in doc.ents if ent.label_ in ["ORG", "PERSON", "PRODUCT", "GPE"]))
    return entities[:20]


def extract_citation_urls(soup):
    authoritative_hints = [".gov", ".edu", "pubmed", "who.int", "nature.com", "researchgate"]
    links = [
        a["href"] for a in soup.find_all("a", href=True)
        if a["href"].startswith("http")
    ]
    # prioritize authoritative-looking links
    priority = [l for l in links if any(h in l for h in authoritative_hints)]
    others = [l for l in links if l not in priority]
    return (priority + others)[:5]


def extract_originality_signals(soup):
    ORIGINALITY_PHRASES = [
        "our study", "our research", "we found", "we surveyed",
        "our data shows", "in our analysis", "our findings"
    ]
    text = soup.get_text().lower()
    signals_found = [p for p in ORIGINALITY_PHRASES if p in text]
    stat_matches = re.findall(r'\b\d+\.?\d*\s*(%|percent|respondents|participants)\b', soup.get_text(), re.IGNORECASE)

    title_tag = soup.find("title")
    meta_tag = soup.find("meta", attrs={"name": "description"})
    return {
        "originality_phrases": signals_found,
        "statistics_found": stat_matches[:3],
        "title": title_tag.get_text(strip=True) if title_tag else "",
        "meta": meta_tag["content"] if meta_tag and meta_tag.get("content") else ""
    }


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

    lengths = [len(s.split()) for s in sentences]
    avg = sum(lengths) / len(lengths)
    variance = sum((l - avg) ** 2 for l in lengths) / len(lengths)
    full_text = " ".join(paragraphs[:10]).lower()

    return {
        "avg_sentence_length": round(avg, 1),
        "sentence_length_variance": round(variance, 1),
        "personal_pronoun_count": len(re.findall(r'\b(i|we|my|our|i\'ve|we\'ve)\b', full_text)),
        "first_person_anecdotes": len(re.findall(r'\b(i found|we found|i tested|we tested|in my experience)\b', full_text))
    }


def extract_page_intro(soup):
    title = soup.find("title")
    h1 = soup.find("h1")
    first_para = soup.find("p")
    return " ".join(filter(None, [
        title.get_text(strip=True) if title else "",
        h1.get_text(strip=True) if h1 else "",
        first_para.get_text(strip=True)[:200] if first_para else ""
    ]))


# --- main batch function ---

def run_ai_batch(site_data):
    if not GEMINI_API_KEY:
        return {}

    soup = site_data.soup

    entities = extract_entities(soup)
    citation_urls = extract_citation_urls(soup)
    originality_signals = extract_originality_signals(soup)
    content_signals = extract_content_signals(soup)
    page_intro = extract_page_intro(soup)

    prompt = f"""You are an SEO and content quality analyzer. Analyze the following data from a webpage and answer ALL questions below. Respond ONLY in valid JSON with no extra text, preamble, or markdown.

WEBPAGE DATA:
- Entities found: {entities}
- Citation URLs: {citation_urls}
- Originality signals: {originality_signals}
- Content pattern signals: {content_signals}
- Page intro (title + H1 + first paragraph): {page_intro[:300]}

ANSWER ALL QUESTIONS:

1. metric_56 (Entity Authority): From the entities list, which ones are widely recognized as authoritative sources (major organizations, institutions, known public figures)? List them.

2. metric_60 (Disambiguation): Based on the page intro, does the content explicitly clarify which specific entity or meaning it refers to, in case the name could be ambiguous? Answer YES or NO with one line of reasoning.

3. metric_63 (Citation Quality): Based on the citation URLs provided, rate the overall citation quality as High, Medium, or Low with one line of reasoning.

4. metric_65 (Original Research): Based on the originality signals, rate the likelihood this contains original research or proprietary data as High, Medium, or Low with one line of reasoning.

5. metric_196 (AI Footprints): Based on the content pattern signals (sentence variance, pronoun frequency, anecdote count), rate the likelihood this is mass-produced AI-generated content as High, Medium, or Low with one line of reasoning.

Respond in this exact JSON format:
{{
  "metric_56": {{"authoritative_entities": [], "reasoning": ""}},
  "metric_60": {{"disambiguates": true, "reasoning": ""}},
  "metric_63": {{"citation_quality": "High/Medium/Low", "reasoning": ""}},
  "metric_65": {{"originality": "High/Medium/Low", "reasoning": ""}},
  "metric_196": {{"ai_likelihood": "High/Medium/Low", "reasoning": ""}}
}}"""

    try:
        response = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30
        )
        raw = response.json()
        text = raw["candidates"][0]["content"]["parts"][0]["text"].strip()

        # strip markdown code fences if Gemini adds them
        text = re.sub(r"```json|```", "", text).strip()
        return json.loads(text)

    except Exception as e:
        print(f"AI batch error: {e}")
        return {}