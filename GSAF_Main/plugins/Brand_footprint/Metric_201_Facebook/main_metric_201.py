'''
Facebook Presence Checker:
Detects whether a website contains links to an official Facebook page.
'''

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


# Function: checks Facebook presence on a website
def check_facebook_page(context):

    # Get website URL from shared context (passed from main.py)
    page_url = context["url"]

    try:
        # Send HTTP request to fetch website HTML
        response = requests.get(
            page_url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )

        # Raise error if request failed (like 404, 403, etc.)
        response.raise_for_status()

        # Parse HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Flag to track Facebook presence
        fb_found = False

        # Loop through all anchor tags (<a href="...">)
        for link in soup.find_all("a", href=True):

            # Convert relative URLs to absolute URLs
            href = urljoin(page_url, link["href"])

            # Check if link contains Facebook domain
            if "facebook.com" in href.lower():
                fb_found = True
                break

        # Decide final status based on detection
        if fb_found:
            status = "Found"
            score = 100
        else:
            status = "Not Found"
            score = 0

    except Exception as e:
        # Handle errors like network failure or invalid URL
        return {
            "factor": "Facebook Presence",
            "status": "Error",
            "score": 0,
            "error": str(e)
        }

    # Return final result to main system
    return {
        "factor": "Facebook Presence",
        "status": status,
        "score": score
    }

def run(context):
    return check_facebook_page(context)

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