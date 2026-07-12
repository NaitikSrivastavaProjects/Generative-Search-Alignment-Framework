import spacy
from models.metric_result import MetricResult
from utils.helpers import get_status

nlp = spacy.load("en_core_web_sm")


def run(site_data):
    result = MetricResult(factor="56 - Co-Occurrence with Authoritative Entities")

    try:
        soup = site_data.soup
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")[:15]]
        text = " ".join(paragraphs)[:5000]
        doc = nlp(text)

        all_entities = list(set(
            ent.text for ent in doc.ents
            if ent.label_ in ["ORG", "PERSON", "PRODUCT", "GPE"]
        ))

        result.details["all_entities_found"] = all_entities[:20]

        ai_data = site_data.ai_results.get("metric_56", {})
        authoritative = ai_data.get("authoritative_entities", [])
        reasoning = ai_data.get("reasoning", "")

        result.details["authoritative_entities"] = authoritative
        result.details["ai_reasoning"] = reasoning

        if not all_entities:
            result.score = 0
            result.status = get_status(result.score)
            result.recommendations.append(
                "No named entities detected on this page. "
                "Mention well-known organizations, institutions, or experts to build topical trust."
            )
            return result.to_dict()

        if not ai_data:
            result.details["note"] = "AI batch result not available — falling back to entity count only."
            result.score = min(60, len(all_entities) * 3)
        else:
            ratio = len(authoritative) / len(all_entities) if all_entities else 0
            result.score = min(100, round(ratio * 100) + min(20, len(authoritative) * 5))

        result.status = get_status(result.score)

        if authoritative:
            result.details["note"] = f"Authoritative entities found: {', '.join(authoritative)}"
        else:
            result.recommendations.append(
                "No widely recognized authoritative entities detected. "
                "Co-mentioning trusted organizations or experts improves answer engine trust."
            )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()