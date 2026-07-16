"""
NAP Consistency Checker:
Checks if Name, Address, and Phone number exist on a website page.
"""

import re
import requests
from bs4 import BeautifulSoup

from models.metric_result import MetricResult


# -----------------------------
# Phone number pattern (global formats)
# -----------------------------
PHONE_PATTERN = re.compile(
    r"(\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3,5}[-.\s]?\d{3,9}"
)


# -----------------------------
# Simple address keywords
# -----------------------------
ADDRESS_KEYWORDS = [
    "address", "street", "road", "lane", "city", "state",
    "india", "usa", "uk", "pincode", "zip", "location"
]


# -----------------------------
# Checker function
# -----------------------------
def check_nap_consistency(site_data):
    page_url = site_data.url
    result = MetricResult(factor="NAP Consistency")

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
        text = soup.get_text(" ", strip=True).lower()

        phone_match = PHONE_PATTERN.search(text)
        phone_found = bool(phone_match)

        address_found = any(
            keyword in text
            for keyword in ADDRESS_KEYWORDS
        )

        title = soup.title.string.strip().lower() if soup.title else ""
        name_found = bool(title)

        score = 0
        if name_found:
            score += 30
        if address_found:
            score += 35
        if phone_found:
            score += 35

        status = "Incomplete"

        if score == 100:
            status = "Perfect NAP"
        elif score >= 60:
            status = "Partial NAP"
        else:
            status = "Weak NAP"

        result.status = status
        result.score = score
        result.details["name_found"] = name_found
        result.details["address_found"] = address_found
        result.details["phone_found"] = phone_found

    except Exception as e:
        result.status = "Error"
        result.score = 0
        result.error = str(e)

    return result.to_dict()


def run(site_data):
    return check_nap_consistency(site_data)
# -----------------------------
# Independent testing
# -----------------------------
if __name__ == "__main__":

    print("\n===== NAP CONSISTENCY CHECKER =====\n")

    url = input("Enter Website URL: ").strip()

    context = {"url": url}

    result = check_nap_consistency(context)

    print("\n========== RESULT ==========")
    for k, v in result.items():
        print(f"{k.capitalize()} : {v}")