import re
from models.metric_result import MetricResult
from utils.helpers import get_status


def run(site_data):
    result = MetricResult(factor="196 - AI Footprints")

    try:
        soup = site_data.soup
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) > 30]

        if not paragraphs:
            result.error = "Not enough content to analyze"
            return result.to_dict()

        sentences = []
        for para in paragraphs[:10]:
            sentences.extend(re.split(r'(?<=[.!?])\s+', para))
        sentences = [s for s in sentences if len(s) > 10]

        lengths = [len(s.split()) for s in sentences]
        avg = sum(lengths) / len(lengths) if lengths else 0
        variance = sum((l - avg) ** 2 for l in lengths) / len(lengths) if lengths else 0
        full_text = " ".join(paragraphs[:10]).lower()
        pronouns = len(re.findall(r'\b(i|we|my|our|i\'ve|we\'ve)\b', full_text))
        anecdotes = len(re.findall(r'\b(i found|we found|i tested|we tested|in my experience)\b', full_text))

        result.details["avg_sentence_length"] = round(avg, 1)
        result.details["sentence_length_variance"] = round(variance, 1)
        result.details["personal_pronoun_count"] = pronouns
        result.details["first_person_anecdotes"] = anecdotes

        ai_data = site_data.ai_results.get("metric_196", {})

        if not ai_data:
            result.details["note"] = "AI batch result not available — using signal-based heuristic only."
            if variance > 20 and pronouns > 5:
                result.score = 80
            elif variance > 10 or pronouns > 2:
                result.score = 50
            else:
                result.score = 20
        else:
            likelihood = ai_data.get("ai_likelihood", "medium").lower()
            result.details["ai_likelihood"] = likelihood
            result.details["ai_reasoning"] = ai_data.get("reasoning", "")
            result.score = {"low": 100, "medium": 60, "high": 20}.get(likelihood, 50)

            if likelihood == "high":
                result.recommendations.append(
                    "Content shows strong AI-generation patterns. "
                    "Add original insights, personal experience, and varied sentence structure."
                )
            elif likelihood == "medium":
                result.recommendations.append(
                    "Content shows some AI-generation signals. "
                    "Consider adding more personal perspective and varied writing style."
                )

        result.status = get_status(result.score)

    except Exception as e:
        result.error = str(e)

    return result.to_dict()