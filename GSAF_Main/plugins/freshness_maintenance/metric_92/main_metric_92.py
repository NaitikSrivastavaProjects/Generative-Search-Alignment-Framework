from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.constants import LIVE_DATA_PROVIDERS


LIVE_CLASS_PATTERNS = ["ticker", "live-score", "real-time", "stock-price", "weather-widget"]
LIVE_SCHEMA_TYPES = ["LiveBlogPosting", "Event"]


def run(site_data):
    result = MetricResult(factor="92 - Live Data Embeds")

    try:
        soup = site_data.soup

        provider_embeds = []
        for iframe in soup.find_all("iframe", src=True):
            if any(provider in iframe["src"] for provider in LIVE_DATA_PROVIDERS):
                provider_embeds.append(iframe["src"])

        live_class_elements = soup.find_all(
            class_=lambda x: x and any(p in " ".join(x).lower() for p in LIVE_CLASS_PATTERNS)
        )

        live_schema = []
        for block in site_data.json_ld:
            if block.get("@type") in LIVE_SCHEMA_TYPES:
                live_schema.append(block.get("@type"))

        result.details["provider_embeds_found"] = len(provider_embeds)
        result.details["live_class_elements_found"] = len(live_class_elements)
        result.details["live_schema_types_found"] = live_schema

        if provider_embeds:
            result.score = 100
        elif live_schema:
            result.score = 80
        elif live_class_elements:
            result.score = 70
        else:
            result.score = 0
            result.status = "Not Applicable"
            result.details["note"] = "No live data embeds found — not applicable for all content types."
            return result.to_dict()

        result.status = get_status(result.score)

    except Exception as e:
        result.error = str(e)

    return result.to_dict()