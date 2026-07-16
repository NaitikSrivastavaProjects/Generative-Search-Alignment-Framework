from models.metric_result import MetricResult
from utils.helpers import get_status


def run(site_data):
    soup = site_data.soup
    response = site_data.response

    score = 0
    details = {}
    recommendations = []

    # -----------------------------
    # 1. HTTP Status (15)
    # -----------------------------
    if response and response.status_code == 200:
        score += 15
        details["http_status"] = "200 OK"
    else:
        details["http_status"] = (
            response.status_code if response else "No Response"
        )
        recommendations.append(
            "Return HTTP 200 so AI crawlers can access the page."
        )

    # -----------------------------
    # 2. HTML Document Exists (10)
    # -----------------------------
    if site_data.html:
        score += 10
    else:
        recommendations.append("No HTML document found.")

    # -----------------------------
    # 3. HTML Tag (10)
    # -----------------------------
    html_tag = soup.find("html")
    if html_tag:
        score += 10
    else:
        recommendations.append("Missing <html> tag.")

    # -----------------------------
    # 4. Title Tag (10)
    # -----------------------------
    title = soup.find("title")

    if title and title.get_text(strip=True):
        score += 10
        details["title"] = title.get_text(strip=True)
    else:
        recommendations.append("Add a descriptive <title> tag.")

    # -----------------------------
    # 5. Body Tag (10)
    # -----------------------------
    body = soup.find("body")

    if body:
        score += 10
    else:
        recommendations.append("Missing <body> tag.")

    # -----------------------------
    # 6. Main Content (10)
    # -----------------------------
    main = soup.find("main")

    if main:
        score += 10
    else:
        recommendations.append(
            "Consider wrapping primary content inside a <main> element."
        )

    # -----------------------------
    # 7. Heading Structure (10)
    # -----------------------------
    h1 = soup.find_all("h1")
    h2 = soup.find_all("h2")

    details["h1_count"] = len(h1)
    details["h2_count"] = len(h2)

    if len(h1) >= 1:
        score += 10
    else:
        recommendations.append("Page should contain at least one H1 heading.")

    # -----------------------------
    # 8. Visible Text (15)
    # -----------------------------
    visible_text = soup.get_text(" ", strip=True)

    text_length = len(visible_text)

    details["visible_text_length"] = text_length

    if text_length >= 500:
        score += 15
    elif text_length >= 300:
        score += 8
        recommendations.append(
            "Increase content depth to improve AI understanding."
        )
    else:
        recommendations.append(
            "Very little visible content detected."
        )

    # -----------------------------
    # 9. Images with Alt Text (5)
    # -----------------------------
    images = soup.find_all("img")

    if images:
        alt_images = sum(
            1 for img in images
            if img.get("alt") and img.get("alt").strip()
        )

        details["images"] = len(images)
        details["images_with_alt"] = alt_images

        if alt_images == len(images):
            score += 5
        else:
            recommendations.append(
                "Some images are missing alt text."
            )
    else:
        score += 5
        details["images"] = 0

    # -----------------------------
    # 10. Structured Data Presence (5)
    # -----------------------------
    if site_data.json_ld:
        score += 5
        details["json_ld"] = len(site_data.json_ld)
    else:
        recommendations.append(
            "Consider adding Schema.org JSON-LD markup."
        )

    return MetricResult(
        factor="Metric 161 - Clean Crawlable HTML",
        score=min(score, 100),
        status=get_status(min(score, 100)),
        details=details,
        recommendations=recommendations
    ).to_dict()