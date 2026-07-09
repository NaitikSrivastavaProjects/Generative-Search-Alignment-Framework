'''
Immediate Answer Placement Checker:
Detects whether question-style headings are answered in a 40-60 word
paragraph immediately below them, rather than after long intros.
'''
import requests
from bs4 import BeautifulSoup

QUESTION_STARTERS = ("what", "why", "how", "when", "where", "who", "can", "does", "is", "are")

def _is_question_heading(text):
    text = text.strip().lower()
    return text.endswith("?") or text.startswith(QUESTION_STARTERS)

def check_immediate_answer_placement(context):
    page_url = context["url"]
    try:
        response = requests.get(page_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        question_headings = [h for h in soup.find_all(["h1", "h2"]) if _is_question_heading(h.get_text(strip=True))]

        if not question_headings:
            return {
                "factor": "Immediate Answer Below Heading",
                "status": "Not Found",
                "score": 0,
                "details": {"reason": "No question-style headings found to check"},
                "recommendations": ["Add question-style H1/H2 headings first, then place a direct answer below each."]
            }

        good_placements = 0
        recommendations = []
        checked = []

        for heading in question_headings:
            heading_text = heading.get_text(strip=True)
            next_para = heading.find_next_sibling("p")
            if next_para:
                word_count = len(next_para.get_text(strip=True).split())
                in_range = 40 <= word_count <= 60
                if in_range:
                    good_placements += 1
                else:
                    recommendations.append(f"Answer under \"{heading_text}\" is {word_count} words — tighten to 40-60 words.")
                checked.append({"heading": heading_text, "word_count": word_count, "in_range": in_range})
            else:
                recommendations.append(f"No paragraph directly follows heading: \"{heading_text}\"")
                checked.append({"heading": heading_text, "word_count": 0, "in_range": False})

        score = round((good_placements / len(question_headings)) * 100)
        status = "Good" if score >= 70 else "Needs Improvement" if score >= 30 else "Poor"

        return {
            "factor": "Immediate Answer Below Heading",
            "status": status,
            "score": score,
            "details": {"checked_headings": checked},
            "recommendations": recommendations
        }

    except Exception as e:
        return {
            "factor": "Immediate Answer Below Heading",
            "status": "Error",
            "score": 0,
            "details": {},
            "recommendations": [],
            "error": str(e)
        }

def run(context):
    return check_immediate_answer_placement(context)

if __name__ == "__main__":
    print("\n===== IMMEDIATE ANSWER PLACEMENT CHECKER =====\n")
    url = input("Enter Website URL: ").strip()
    context = {"url": url}
    result = check_immediate_answer_placement(context)
    print("\n========== RESULT ==========")
    print(f"Factor : {result['factor']}")
    print(f"Status : {result['status']}")
    print(f"Score  : {result['score']}")
    if result.get("recommendations"):
        for rec in result["recommendations"]:
            print(f"  → {rec}")
    if "error" in result:
        print("\nError:", result["error"])