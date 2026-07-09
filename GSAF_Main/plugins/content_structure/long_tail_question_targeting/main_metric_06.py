'''
Long-Tail Question Targeting Checker:
Detects whether headings are long-tail, specific questions (5-10 words)
rather than short 1-2 word keyword-style headings.
'''
import requests
from bs4 import BeautifulSoup

def check_long_tail_targeting(context):
    page_url = context["url"]
    try:
        response = requests.get(page_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        headings = soup.find_all(["h1", "h2"])
        if not headings:
            return {
                "factor": "Long-Tail Question Targeting",
                "status": "Not Found",
                "score": 0,
                "details": {"total_headings": 0},
                "recommendations": ["Add H1/H2 headings phrased as specific, longer questions."]
            }

        long_tail_count = 0
        checked = []
        for heading in headings:
            text = heading.get_text(strip=True)
            word_count = len(text.split())
            is_long_tail = 5 <= word_count <= 10
            if is_long_tail:
                long_tail_count += 1
            checked.append({"heading": text, "word_count": word_count, "is_long_tail": is_long_tail})

        ratio = long_tail_count / len(headings)
        score = round(ratio * 100)
        status = "Good" if score >= 60 else "Needs Improvement" if score >= 25 else "Poor"

        recommendations = []
        if score < 60:
            recommendations.append("Expand short keyword-style headings into full 5-10 word questions matching how users actually ask AI.")

        return {
            "factor": "Long-Tail Question Targeting",
            "status": status,
            "score": score,
            "details": {"total_headings": len(headings), "long_tail_headings": long_tail_count, "checked": checked},
            "recommendations": recommendations
        }

    except Exception as e:
        return {"factor": "Long-Tail Question Targeting", "status": "Error", "score": 0, "details": {}, "recommendations": [], "error": str(e)}

def run(context):
    return check_long_tail_targeting(context)

if __name__ == "__main__":
    print("\n===== LONG-TAIL QUESTION TARGETING CHECKER =====\n")
    url = input("Enter Website URL: ").strip()
    result = check_long_tail_targeting({"url": url})
    print("\n========== RESULT ==========")
    print(f"Factor : {result['factor']}")
    print(f"Status : {result['status']}")
    print(f"Score  : {result['score']}")
    if result.get("recommendations"):
        for rec in result["recommendations"]:
            print(f"  → {rec}")
    if "error" in result:
        print("\nError:", result["error"])