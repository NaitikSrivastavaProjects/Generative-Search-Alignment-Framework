"""
NAP Consistency Checker:
Checks if Name, Address, and Phone number exist on a website page.
"""

import re
import requests
from bs4 import BeautifulSoup


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
def check_nap_consistency(context):

    url = context.get("url", "")

    if not url:
        return {
            "factor": "NAP Consistency",
            "status": "Error",
            "score": 0,
            "error": "URL missing"
        }

    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(" ", strip=True).lower()

        # -----------------------------
        # Check Phone
        # -----------------------------
        phone_match = PHONE_PATTERN.search(text)
        phone_found = bool(phone_match)

        # -----------------------------
        # Check Address keywords
        # -----------------------------
        address_found = any(
            keyword in text
            for keyword in ADDRESS_KEYWORDS
        )

        # -----------------------------
        # Check Name (basic heuristic)
        # -----------------------------
        title = soup.title.string.strip().lower() if soup.title else ""
        name_found = bool(title)

        # -----------------------------
        # Score calculation
        # -----------------------------
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

        return {
            "factor": "NAP Consistency",
            "status": status,
            "score": score,
            "name_found": name_found,
            "address_found": address_found,
            "phone_found": phone_found
        }

    except Exception as e:
        return {
            "factor": "NAP Consistency",
            "status": "Error",
            "score": 0,
            "error": str(e)
        }

def run(context):
    return check_nap_consistency(context)
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