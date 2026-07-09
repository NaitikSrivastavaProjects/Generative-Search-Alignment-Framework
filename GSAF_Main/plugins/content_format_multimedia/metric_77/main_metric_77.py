from models.metric_result import MetricResult
from utils.helpers import get_status
from utils.keywords import CALCULATOR_CLASS_KEYWORDS, CALCULATOR_HEADING_KEYWORDS


def run(site_data):
    result = MetricResult(factor="77 - Embedded Calculators and Tools")

    try:
        soup = site_data.soup

        app_schema = [
            b for b in site_data.json_ld
            if b.get("@type") in ("WebApplication", "SoftwareApplication")
        ]

        calc_containers = soup.find_all(
            class_=lambda x: x and any(k in " ".join(x).lower() for k in CALCULATOR_CLASS_KEYWORDS)
        )
        calc_containers += soup.find_all(
            id=lambda x: x and any(k in x.lower() for k in CALCULATOR_CLASS_KEYWORDS)
        )

        number_inputs = soup.find_all("input", type=lambda x: x and x.lower() in ("number", "range"))
        has_button = bool(soup.find("button"))
        has_textarea = bool(soup.find("textarea"))

        calc_headings = soup.find_all(
            ["h2", "h3"],
            string=lambda x: x and any(k in x.lower() for k in CALCULATOR_HEADING_KEYWORDS)
        )

        result.details["app_schema_found"] = len(app_schema)
        result.details["calculator_containers_found"] = len(calc_containers)
        result.details["number_inputs_found"] = len(number_inputs)
        result.details["calculator_headings_found"] = len(calc_headings)

        if app_schema:
            result.score = 100
        elif calc_containers and number_inputs:
            result.score = 80
        elif len(number_inputs) >= 3 and has_button and not has_textarea:
            result.score = 65
        elif calc_headings and number_inputs:
            result.score = 50
        else:
            result.score = 0
            result.status = "Not Applicable"
            result.details["note"] = "No calculator or interactive tool detected on this page."
            return result.to_dict()

        result.status = get_status(result.score)

    except Exception as e:
        result.error = str(e)

    return result.to_dict()