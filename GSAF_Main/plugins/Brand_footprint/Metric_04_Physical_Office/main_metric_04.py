'''
Physical Brick-and-Mortar Office Checker:
Detects whether a website provides a physical office address.
'''

import re
import requests
from bs4 import BeautifulSoup


# Function: checks for a physical office address
def check_physical_brick_and_mortar_office(context):

    # Get website URL from shared context
    page_url = context["url"]

    try:
        # Send HTTP request
        response = requests.get(
            page_url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )

        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract all visible text
        page_text = soup.get_text(" ", strip=True)

        # Common address-related keywords
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

        # Simple street address pattern
        address_pattern = re.compile(
            r"\d{1,6}\s+[A-Za-z0-9\s,.-]+"
        )

        address_found = bool(address_pattern.search(page_text))

        if keyword_found or address_found:
            status = "Found"
            score = 100
        else:
            status = "Not Found"
            score = 0

    except Exception as e:
        return {
            "factor": "Physical Brick-and-Mortar Office",
            "status": "Error",
            "score": 0,
            "error": str(e)
        }

    return {
        "factor": "Physical Brick-and-Mortar Office",
        "status": status,
        "score": score
    }

def run(context):
    return check_physical_brick_and_mortar_office(context)
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