'''
Physical Brick-and-Mortar Office Checker:
Detects whether a website provides a physical office address.
'''

import re
import requests
from bs4 import BeautifulSoup

from models.metric_result import MetricResult


# Function: checks for a physical office address
def check_physical_brick_and_mortar_office(site_data):
    page_url = site_data.url
    result = MetricResult(factor="Physical Brick-and-Mortar Office")

    if not page_url:
        result.status = "Error"
        result.score = 0
        result.error = "URL missing"
        return result.to_dict()

    try:
        response = requests.get(
            page_url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )

        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        page_text = soup.get_text(" ", strip=True)

        keywords = [
            "address",
            "office",
            "head office",
            "headquarters",
            "location",
            "visit us",
            "contact us"
        ]

        keyword_found = any(
            keyword.lower() in page_text.lower()
            for keyword in keywords
        )

        address_pattern = re.compile(
            r"\d{1,6}\s+[A-Za-z0-9\s,.-]+"
        )

        address_found = bool(address_pattern.search(page_text))

        if keyword_found or address_found:
            result.status = "Found"
            result.score = 100
        else:
            result.status = "Not Found"
            result.score = 0

    except Exception as e:
        result.status = "Error"
        result.score = 0
        result.error = str(e)

    return result.to_dict()


def run(site_data):
    return check_physical_brick_and_mortar_office(site_data)
# ---------------------------------------------------
# Individual Testing
# ---------------------------------------------------
if __name__ == "__main__":

    print("\n===== PHYSICAL OFFICE CHECKER =====\n")

    url = input("Enter Website URL: ").strip()

    context = {
        "url": url
    }

    result = check_physical_brick_and_mortar_office(context)

    print("\n========== RESULT ==========")
    print(f"Factor : {result['factor']}")
    print(f"Status : {result['status']}")
    print(f"Score  : {result['score']}")

    if "error" in result:
        print("\nError:", result["error"])