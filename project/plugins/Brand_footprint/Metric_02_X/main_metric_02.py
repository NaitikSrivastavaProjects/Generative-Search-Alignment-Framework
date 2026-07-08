'''
X (Twitter) Presence Checker:
Detects whether a website contains links to an official X (Twitter) profile.
'''

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


# Function: checks X (Twitter) presence on a website
def check_x_profile(context):

    # Get website URL from shared context (from main.py)
    page_url = context["url"]

    try:
        # Send request to fetch website HTML content
        response = requests.get(
            page_url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )

        # Raise exception if request fails (404, 403, etc.)
        response.raise_for_status()

        # Parse HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Flag to track X (Twitter) presence
        x_found = False

        # Loop through all anchor tags (<a href="...">)
        for link in soup.find_all("a", href=True):

            # Convert relative URLs to absolute URLs
            href = urljoin(page_url, link["href"])

            # Detect X (Twitter) links
            if "twitter.com" in href.lower() or "x.com" in href.lower():
                x_found = True
                break

        # Decide final status
        if x_found:
            status = "Found"
            score = 100
        else:
            status = "Not Found"
            score = 0

    except Exception as e:
        # Handle errors like network issues or invalid URL
        return {
            "factor": "Official X (Twitter) Profile",
            "status": "Error",
            "score": 0,
            "error": str(e)
        }

    # Return final structured result
    return {
        "factor": "Official X (Twitter) Profile",
        "status": status,
        "score": score
    }

def run(context):
    return check_x_profile(context)
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