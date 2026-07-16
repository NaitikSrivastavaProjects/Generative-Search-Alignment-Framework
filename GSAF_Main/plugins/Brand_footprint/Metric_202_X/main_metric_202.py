'''
X (Twitter) Presence Checker:
Detects whether a website contains links to an official X (Twitter) profile.
'''

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from models.metric_result import MetricResult


# Function: checks X (Twitter) presence on a website
def check_x_profile(site_data):
    page_url = site_data.url
    result = MetricResult(factor="Official X (Twitter) Profile")

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
        x_found = False

        for link in soup.find_all("a", href=True):
            href = urljoin(page_url, link["href"])
            if "twitter.com" in href.lower() or "x.com" in href.lower():
                x_found = True
                break

        if x_found:
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
    return check_x_profile(site_data)
# ---------------------------------------------------
# Individual Testing (run file directly)
# ---------------------------------------------------
if __name__ == "__main__":

    print("\n===== X (TWITTER) PRESENCE CHECKER =====\n")

    # Take website URL input from user
    url = input("Enter Website URL: ").strip()

    # Create context for plugin system
    context = {
        "url": url
    }

    # Run the checker function
    result = check_x_profile(context)

    # Print clean output
    print("\n========== RESULT ==========")
    print(f"Factor : {result['factor']}")
    print(f"Status : {result['status']}")
    print(f"Score  : {result['score']}")

    # Show error only if something went wrong
    if "error" in result:
        print("\nError:", result["error"])