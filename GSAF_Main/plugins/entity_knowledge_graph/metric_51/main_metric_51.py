import spacy
from models.metric_result import MetricResult
from utils.helpers import get_status


nlp = spacy.load("en_core_web_sm")

PRIORITY_ENTITY_TYPES = ["ORG", "PERSON", "PRODUCT", "GPE", "EVENT", "WORK_OF_ART"]


def run(site_data):
    result = MetricResult(factor="51 - Entity Recognition")

    try:
        soup = site_data.soup

        title = soup.find("title")
        h1 = soup.find("h1")
        first_para = soup.find("p")

        priority_text = " ".join(filter(None, [
            title.get_text(strip=True) if title else "",
            h1.get_text(strip=True) if h1 else "",
            first_para.get_text(strip=True) if first_para else ""
        ]))

        paragraphs = soup.find_all("p")
        body_text = " ".join(p.get_text(strip=True) for p in paragraphs[:20])

        priority_doc = nlp(priority_text)
        body_doc = nlp(body_text[:5000])

        priority_entities = [
            (ent.text, ent.label_) for ent in priority_doc.ents
            if ent.label_ in PRIORITY_ENTITY_TYPES
        ]

        all_entities = [
            (ent.text, ent.label_) for ent in body_doc.ents
            if ent.label_ in PRIORITY_ENTITY_TYPES
        ]

        unique_entities = list(set(all_entities))
        unique_types = list(set(label for _, label in unique_entities))

        result.details["priority_zone_entities"] = priority_entities
        result.details["total_unique_entities"] = len(unique_entities)
        result.details["entity_types_found"] = unique_types
        result.details["entities_sample"] = unique_entities[:10]

        entity_score = min(40, len(unique_entities) * 2)
        priority_score = min(40, len(priority_entities) * 5)
        diversity_score = min(20, len(unique_types) * 3)

        result.score = entity_score + priority_score + diversity_score
        result.score = min(100, result.score)
        result.status = get_status(result.score)

        if not priority_entities:
            result.recommendations.append(
                "No recognized entities found in title, H1, or first paragraph. "
                "Use canonical entity names in key positions to improve Knowledge Graph recognition."
            )

        if len(unique_types) < 2:
            result.recommendations.append(
                "Low entity type diversity — mention related entities (organizations, people, places) "
                "to build stronger topical context."
            )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()