from models.metric_result import MetricResult
from utils.helpers import get_status


def run(site_data):

    response = site_data.response

    score = 0
    details = {}
    recommendations = []

    # ----------------------------------------
    # 1. Calculate Page Size (40)
    # ----------------------------------------

    content_length = response.headers.get("Content-Length")

    page_size_kb = 0

    if content_length:
        page_size_kb = int(content_length) / 1024

    else:
        # fallback when Content-Length header is missing
        page_size_kb = len(response.content) / 1024


    details["page_size_kb"] = round(page_size_kb, 2)


    # Recommended page size:
    # Excellent: < 500 KB
    # Good: 500 KB - 1 MB
    # Poor: > 1 MB

    if page_size_kb <= 500:
        score += 40

    elif page_size_kb <= 1024:
        score += 25

        recommendations.append(
            "Page size is acceptable but can be optimized further."
        )

    else:
        recommendations.append(
            "Reduce page size by optimizing images, scripts, and resources."
        )


    # ----------------------------------------
    # 2. Compression Check (20)
    # ----------------------------------------

    encoding = response.headers.get(
        "Content-Encoding",
        ""
    ).lower()

    details["compression"] = encoding


    if encoding in ["gzip", "br", "deflate"]:
        score += 20

    else:
        recommendations.append(
            "Enable GZIP or Brotli compression for faster page delivery."
        )


    # ----------------------------------------
    # 3. HTML Document Size (20)
    # ----------------------------------------

    html_size = len(response.text.encode("utf-8")) / 1024

    details["html_size_kb"] = round(html_size, 2)


    if html_size <= 100:
        score += 20

    elif html_size <= 300:
        score += 10

        recommendations.append(
            "Reduce unnecessary HTML content and duplicate markup."
        )

    else:
        recommendations.append(
            "HTML document is large. Minify HTML and remove unused code."
        )


    # ----------------------------------------
    # 4. Resource Optimization Check (20)
    # ----------------------------------------

    soup = site_data.soup

    images = soup.find_all("img")
    scripts = soup.find_all("script")
    stylesheets = soup.find_all("link", rel="stylesheet")


    details["images_count"] = len(images)
    details["scripts_count"] = len(scripts)
    details["stylesheets_count"] = len(stylesheets)


    total_resources = (
        len(images)
        + len(scripts)
        + len(stylesheets)
    )


    if total_resources <= 50:
        score += 20

    elif total_resources <= 100:
        score += 10

        recommendations.append(
            "Reduce the number of page resources to improve loading speed."
        )

    else:
        recommendations.append(
            "Too many resources detected. Combine and optimize files."
        )


    # ----------------------------------------
    # Final Result
    # ----------------------------------------

    final_score = min(score, 100)

    return MetricResult(
        factor="Metric 168 - Page Size Reasonable",
        score=final_score,
        status=get_status(final_score),
        details=details,
        recommendations=recommendations
    ).to_dict()