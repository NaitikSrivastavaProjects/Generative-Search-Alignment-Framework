'''
Step-by-Step List Checker:
For "How to" style content, detects whether steps are presented as a
numbered/ordered list with 3+ steps, which AI engines favor over
unstructured paragraphs when answering how-to queries.
'''
import re
import requests
from bs4 import BeautifulSoup

def check_step_by_step_lists(context):
    page_url = context["url"]
    try:
        response = requests.get(page_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        headings = soup.find_all(["h1", "h2"])
        how_to_headings = [h for h in headings if re.match(r"how\s+(to|do|can)\b", h.get_text(strip=True), re.IGNORECASE)]

        if not how_to_headings:
            return {
                "factor": "Step-by-Step Lists for How Queries",
                "status": "Not Found",
                "score": 0,
                "details": {"reason": "No 'How to...' style headings found"},
                "recommendations": ["Add a 'How to...' heading if this page targets instructional queries."]
            }

        good_lists = 0
        checked = []
        for heading in how_to_headings:
            heading_text = heading.get_text(strip=True)
            # look for the nearest following <ol> (ordered list)
            ol = heading.find_next("ol")
            step_count = len(ol.find_all("li")) if ol else 0
            has_steps = step_count >= 3
            if has_steps:
                good_lists += 1
            checked.append({"heading": heading_text, "step_count": step_count, "has_ordered_list": has_steps})

        score = round((good_lists / len(how_to_headings)) * 100)
        status = "Good" if score >= 70 else "Needs Improvement" if score >= 30 else "Poor"

        recommendations = []
        if score < 100:
            recommendations.append("Convert how-to content into a numbered <ol> list with at least 3 clear steps.")

        return {
            "factor": "Step-by-Step Lists for How Queries",
            "status": status,
            "score": score,
            "details": {"checked": checked},
            "recommendations": recommendations
        }

    except Exception as e:
        return {"factor": "Step-by-Step Lists for How Queries", "status": "Error", "score": 0, "details": {}, "recommendations": [], "error": str(e)}

def run(context):
    return check_step_by_step_lists(context)

if __name__ == "__main__":
    print("\n===== STEP-BY-STEP LIST CHECKER =====\n")
    url = input("Enter Website URL: ").strip()
    result = check_step_by_step_lists({"url": url})
    print("\n========== RESULT ==========")
    print(f"Factor : {result['factor']}")
    print(f"Status : {result['status']}")
    print(f"Score  : {result['score']}")
    if result.get("recommendations"):
        for rec in result["recommendations"]:
            print(f"  → {rec}")
    if "error" in result:
        print("\nError:", result["error"])