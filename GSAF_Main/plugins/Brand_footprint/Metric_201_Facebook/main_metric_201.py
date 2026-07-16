'''
Facebook Presence Checker:
Detects whether a website contains links to an official Facebook page.
'''

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from models.metric_result import MetricResult


# Function: checks Facebook presence on a website
def check_facebook_page(site_data):
    page_url = site_data.url
    result = MetricResult(factor="Facebook Presence")

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
        fb_found = False

        for link in soup.find_all("a", href=True):
            href = urljoin(page_url, link["href"])
            if "facebook.com" in href.lower():
                fb_found = True
                break

        if fb_found:
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
    return check_facebook_page(site_data)

# ---------------------------------------------------
# Individual Testing (run this file directly)
# ---------------------------------------------------
if __name__ == "__main__":

    print("\n===== FACEBOOK PRESENCE CHECKER =====\n")

    # Take user input for website URL
    url = input("Enter Website URL: ").strip()

    # Create context dictionary for plugin system
    context = {
        "url": url
    }

    # Run checker function
    result = check_facebook_page(context)

    # Display output in clean format
    print("\n========== RESULT ==========")
    print(f"Factor : {result['factor']}")
    print(f"Status : {result['status']}")
    print(f"Score  : {result['score']}")

    # Print error only if something went wrong
    if "error" in result:
        print("\nError:", result["error"])