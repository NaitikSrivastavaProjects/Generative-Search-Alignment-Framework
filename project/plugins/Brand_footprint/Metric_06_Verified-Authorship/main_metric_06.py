'''
Verified Authorship Checker:
Detects whether a website ties its content to trusted expert
profiles across the web.
'''

import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


# Function: checks verified authorship
def check_verified_authorship(context):

    # Get website URL
    page_url = context["url"]

    try:

        # Fetch webpage
        response = requests.get(
            page_url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        authorship_found = False

        # Trusted profile domains
        trusted_profiles = [
            "linkedin.com",
            "x.com",
            "twitter.com",
            "github.com",
            "orcid.org",
            "scholar.google.com",
            "researchgate.net",
            "medium.com"
        ]

        # ---------------------------------------
        # Check links to trusted expert profiles
        # ---------------------------------------
        for link in soup.find_all("a", href=True):

            href = urljoin(page_url, link["href"]).lower()

            for domain in trusted_profiles:

                if domain in href:
                    authorship_found = True
                    break

            if authorship_found:
                break

        # ---------------------------------------
        # Check Schema.org Person + sameAs
        # ---------------------------------------
        if not authorship_found:

            scripts = soup.find_all(
                "script",
                type="application/ld+json"
            )

            for script in scripts:

                try:

                    if not script.string:
                        continue

                    data = json.loads(script.string)

                    items = data if isinstance(data, list) else [data]

                    for item in items:

                        if not isinstance(item, dict):
                            continue

                        if item.get("@type") == "Person":

                            same_as = item.get("sameAs", [])

                            if isinstance(same_as, list):

                                for profile in same_as:

                                    for domain in trusted_profiles:

                                        if domain in profile.lower():
                                            authorship_found = True
                                            break

                                    if authorship_found:
                                        break

                            if authorship_found:
                                break

                    if authorship_found:
                        break

                except Exception:
                    continue

        # ---------------------------------------
        # Final Result
        # ---------------------------------------
        if authorship_found:
            status = "Found"
            score = 100
        else:
            status = "Not Found"
            score = 0

    except Exception as e:

        return {
            "factor": "Verified Authorship",
            "status": "Error",
            "score": 0,
            "error": str(e)
        }

    return {
        "factor": "Verified Authorship",
        "status": status,
        "score": score
    }


# Required by main.py
def run(context):
    return check_verified_authorship(context)


# ---------------------------------------------------
# Individual Testing
# ---------------------------------------------------
if __name__ == "__main__":

    print("\n===== VERIFIED AUTHORSHIP CHECKER =====\n")

    url = input("Enter Website URL: ").strip()

    context = {
        "url": url
    }

    result = check_verified_authorship(context)

    print("\n========== RESULT ==========")
    print(f"Factor : {result['factor']}")
    print(f"Status : {result['status']}")
    print(f"Score  : {result['score']}")

    if "error" in result:
        print("\nError:", result["error"])