'''
Inverted Pyramid Checker:
Detects whether the most important answer/information appears at the
top of the page rather than buried after long intros or filler.
'''
import requests
from bs4 import BeautifulSoup

def check_inverted_pyramid(context):
    page_url = context["url"]
    try:
        response = requests.get(page_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        paragraphs = soup.find_all("p")
        if not paragraphs:
            return {
                "factor": "Inverted Pyramid Writing",
                "status": "Not Found",
                "score": 0,
                "details": {"reason": "No paragraph content found"},
                "recommendations": ["Add body paragraphs with the key answer stated early."]
            }

        first_para_words = len(paragraphs[0].get_text(strip=True).split())
        is_substantive = first_para_words >= 15
        is_concise = first_para_words <= 80

        if is_substantive and is_concise:
            score, status, recommendations = 100, "Good", []
        elif not is_substantive:
            score, status = 30, "Needs Improvement"
            recommendations = ["First paragraph is too short/thin — lead with a substantive answer, not filler text."]
        else:
            score, status = 50, "Needs Improvement"
            recommendations = ["First paragraph is too long — state the core answer within the first 80 words."]

        return {
            "factor": "Inverted Pyramid Writing",
            "status": status,
            "score": score,
            "details": {"first_paragraph_word_count": first_para_words},
            "recommendations": recommendations
        }

    except Exception as e:
        return {"factor": "Inverted Pyramid Writing", "status": "Error", "score": 0, "details": {}, "recommendations": [], "error": str(e)}

def run(context):
    return check_inverted_pyramid(context)

if __name__ == "__main__":
    print("\n===== INVERTED PYRAMID CHECKER =====\n")
    url = input("Enter Website URL: ").strip()
    result = check_inverted_pyramid({"url": url})
    print("\n========== RESULT ==========")
    print(f"Factor : {result['factor']}")
    print(f"Status : {result['status']}")
    print(f"Score  : {result['score']}")
    if result.get("recommendations"):
        for rec in result["recommendations"]:
            print(f"  → {rec}")
    if "error" in result:
        print("\nError:", result["error"])