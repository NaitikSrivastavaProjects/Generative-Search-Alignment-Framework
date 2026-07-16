'''
Verified Authorship Checker:
Detects whether a website ties its content to trusted expert
profiles across the web.
'''

import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from models.metric_result import MetricResult


# Function: checks verified authorship
def check_verified_authorship(site_data):
    page_url = site_data.url
    result = MetricResult(factor="Verified Authorship")

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

        authorship_found = False

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

        for link in soup.find_all("a", href=True):
            href = urljoin(page_url, link["href"]).lower()

            for domain in trusted_profiles:
                if domain in href:
                    authorship_found = True
                    break

            if authorship_found:
                break

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

        if authorship_found:
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


# Required by main.py
def run(site_data):
    return check_verified_authorship(site_data)


# ---------------------------------------------------
# Individual Testing
# ---------------------------------------------------
if __name__ == "__main__":
    print("\n===== VERIFIED AUTHORSHIP CHECKER =====\n")

    url = input("Enter Website URL: ").strip()

    site_data = type("SiteData", (), {"url": url})()

    result = check_verified_authorship(site_data)

    print("\n========== RESULT ==========")
    print(f"Factor : {result['factor']}")
    print(f"Status : {result['status']}")
    print(f"Score  : {result['score']}")

    if "error" in result:
        print("\nError:", result["error"])
