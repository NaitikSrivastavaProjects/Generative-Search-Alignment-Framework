from models.metric_result import MetricResult
from utils.helpers import get_status


def run(site_data):

    soup = site_data.soup
    html = site_data.html.lower()

    score = 0
    details = {}
    recommendations = []

    # ------------------------------------
    # 1. Visible HTML Content (30)
    # ------------------------------------

    body = soup.find("body")

    if body:
        text = body.get_text(" ", strip=True)
        details["visible_text_length"] = len(text)

        if len(text) >= 500:
            score += 30
        elif len(text) >= 250:
            score += 20
        elif len(text) >= 100:
            score += 10
        else:
            recommendations.append(
                "Very little HTML content detected."
            )

    # ------------------------------------
    # 2. JavaScript Files (20)
    # ------------------------------------

    scripts = soup.find_all("script", src=True)

    details["external_scripts"] = len(scripts)

    if len(scripts) <= 5:
        score += 20
    elif len(scripts) <= 10:
        score += 15
    else:
        recommendations.append(
            "Large number of JavaScript files detected."
        )

    # ------------------------------------
    # 3. Empty Root Div (20)
    # ------------------------------------

    root = soup.find(id="root") or soup.find(id="app")

    if root:

        if root.get_text(strip=True):
            score += 20
        else:
            recommendations.append(
                "Page appears to rely heavily on client-side rendering."
            )

    else:
        score += 20

    # ------------------------------------
    # 4. Framework Detection (15)
    # ------------------------------------

    frameworks = []

    if "__next" in html:
        frameworks.append("Next.js")

    if "__nuxt" in html:
        frameworks.append("Nuxt.js")

    if "react" in html:
        frameworks.append("React")

    if "vue" in html:
        frameworks.append("Vue")

    if "angular" in html:
        frameworks.append("Angular")

    details["frameworks_detected"] = frameworks

    if not frameworks:
        score += 15
    else:
        score += 10

    # ------------------------------------
    # 5. Heading Structure (15)
    # ------------------------------------

    h1 = soup.find_all("h1")
    h2 = soup.find_all("h2")

    details["h1_count"] = len(h1)
    details["h2_count"] = len(h2)

    if len(h1) >= 1:
        score += 15
    else:
        recommendations.append(
            "No H1 heading found in initial HTML."
        )

    return MetricResult(
        factor="Metric 164 - Server Side Rendering",
        score=min(score, 100),
        status=get_status(min(score, 100)),
        details=details,
        recommendations=recommendations
    ).to_dict()