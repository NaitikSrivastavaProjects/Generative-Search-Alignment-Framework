'''
Direct Question Heading Checker:
Detects whether a page's H1/H2 headings are phrased as direct questions,
since AI search engines favor content clearly structured to answer a query.
'''
import requests
from bs4 import BeautifulSoup

QUESTION_STARTERS = ("what", "why", "how", "when", "where", "who", "can", "does", "is", "are")

def check_direct_question_heading(context):
    page_url = context["url"]
    try:
        response = requests.get(page_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        headings = soup.find_all(["h1", "h2"])
        if not headings:
            return {
                "factor": "Direct Question in H1/H2",
                "status": "Not Found",
                "score": 0,
                "details": {"total_headings": 0},
                "recommendations": ["Add at least one H1/H2 heading."]
            }

        question_headings = []
        for heading in headings:
            text = heading.get_text(strip=True).lower()
            if text.endswith("?") or text.startswith(QUESTION_STARTERS):
                question_headings.append(heading.get_text(strip=True))

        ratio = len(question_headings) / len(headings)
        score = round(ratio * 100)
        status = "Found" if question_headings else "Not Found"

        recommendations = []
        if not question_headings:
            recommendations.append("Phrase at least one H1/H2 as a direct question, e.g. 'What is Machine Learning?'")
        elif ratio < 0.5:
            recommendations.append("Phrase more of your headings as direct questions to improve AI answer targeting.")

        return {
            "factor": "Direct Question in H1/H2",
            "status": status,
            "score": score,
            "details": {
                "total_headings": len(headings),
                "question_headings_found": len(question_headings),
                "examples": question_headings[:5]
            },
            "recommendations": recommendations
        }

    except Exception as e:
        return {
            "factor": "Direct Question in H1/H2",
            "status": "Error",
            "score": 0,
            "details": {},
            "recommendations": [],
            "error": str(e)
        }

def run(context):
    return check_direct_question_heading(context)

if __name__ == "__main__":
    print("\n===== DIRECT QUESTION HEADING CHECKER =====\n")
    url = input("Enter Website URL: ").strip()
    context = {"url": url}
    result = check_direct_question_heading(context)
    print("\n========== RESULT ==========")
    print(f"Factor : {result['factor']}")
    print(f"Status : {result['status']}")
    print(f"Score  : {result['score']}")
    if result.get("recommendations"):
        for rec in result["recommendations"]:
            print(f"  → {rec}")
    if "error" in result:
        print("\nError:", result["error"])