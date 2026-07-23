import re
from urllib.parse import urlparse
 
 
STOCK_PHOTO_DOMAINS = [
    "shutterstock.com", "istockphoto.com", "gettyimages.com", "adobe.stock",
    "stock.adobe.com", "unsplash.com", "pexels.com", "freepik.com",
    "depositphotos.com", "123rf.com", "dreamstime.com", "pixabay.com",
    "canva.com", "envato", "alamy.com"
]
 
# alt/filename keywords that indicate a chart, diagram, or data visualization
CHART_KEYWORDS = [
    "chart", "diagram", "graph", "infographic", "flowchart", "flow chart",
    "architecture", "schema", "workflow", "process map", "data visualization",
    "visualisation", "comparison table", "timeline"
]
 
# JS chart/diagram libraries whose presence signals custom-rendered visuals
CHART_LIBRARY_HINTS = [
    "chart.js", "chartjs", "highcharts", "d3.js", "d3.min.js",
    "plotly", "mermaid", "apexcharts", "echarts", "recharts"
]
 
 
def _domain_of(url):
    try:
        return urlparse(url).netloc.lower()
    except ValueError:
        return ""
 
 
def _is_stock_photo(src):
    domain = _domain_of(src)
    return any(stock_domain in domain for stock_domain in STOCK_PHOTO_DOMAINS)
 
 
def _mentions_chart_keywords(text):
    lower = (text or "").lower()
    return any(keyword in lower for keyword in CHART_KEYWORDS)
 
 
def analyze_original_diagrams_vs_stock(site_data):
 
    soup = site_data.soup
 
    inline_svgs = soup.find_all("svg")
    canvases = soup.find_all("canvas")
    images = soup.find_all("img")
    figures_with_caption = soup.find_all("figure")
 
    original_svg_count = len(inline_svgs)
    original_canvas_count = len(canvases)
 
    stock_images = 0
    original_chart_images = 0
    generic_images = 0
 
    for img in images:
        src = img.get("src") or img.get("data-src") or ""
        alt = img.get("alt") or ""
 
        if _is_stock_photo(src):
            stock_images += 1
        elif _mentions_chart_keywords(alt) or _mentions_chart_keywords(src):
            original_chart_images += 1
        else:
            generic_images += 1
 
    # check for chart-library script tags, which strongly indicate original,
    # dynamically rendered data visualizations rather than static stock art
    scripts = soup.find_all("script")
    script_sources = " ".join(
        (s.get("src") or "") + " " + (s.string or "" if s.string else "")
        for s in scripts
    ).lower()
    chart_library_detected = any(hint in script_sources for hint in CHART_LIBRARY_HINTS)
 
    captioned_figures = 0
    for fig in figures_with_caption:
        if fig.find("figcaption"):
            captioned_figures += 1
 
    total_original_visuals = (
        original_svg_count + original_canvas_count + original_chart_images
    )
    total_visuals = total_original_visuals + stock_images
 
    pct_original = (total_original_visuals / total_visuals * 100) if total_visuals else None
 
    score = 0
 
    if total_visuals > 0:
        score += round(pct_original * 0.6)
        score += min(total_original_visuals, 10) * 3
 
        if chart_library_detected:
            score += 10
 
        if captioned_figures > 0:
            score += min(captioned_figures, 5) * 2
 
        if stock_images > 0 and total_original_visuals == 0:
            score = min(score, 25)
    elif images:
        # images exist but none classified as stock or chart-like -- likely
        # generic/decorative photography; treat as weak-but-not-penalized
        score = 50
    else:
        score = 70  # no visuals at all -- not applicable, not penalized
 
    score = max(0, min(score, 100))
 
    details = {
        "inline_svg_diagrams": original_svg_count,
        "canvas_rendered_charts": original_canvas_count,
        "original_chart_images": original_chart_images,
        "stock_images": stock_images,
        "generic_uncategorized_images": generic_images,
        "chart_library_script_detected": chart_library_detected,
        "captioned_figures": captioned_figures,
        "pct_original_of_classified_visuals": round(pct_original, 1) if pct_original is not None else None
    }
 
    recommendations = []
 
    if score < 75:
 
        if stock_images > 0 and total_original_visuals == 0:
            recommendations.append(
                "This page relies entirely on stock imagery with no original diagrams or charts — stock photos "
                "are rarely cited in AI-generated answers, while original data visualizations are cited far more often."
            )
        elif stock_images > total_original_visuals:
            recommendations.append(
                "Stock images outnumber original diagrams/charts — replace decorative stock photography with "
                "original charts, diagrams, or infographics wherever the content involves data or process explanation."
            )
 
        if total_original_visuals == 0 and not chart_library_detected:
            recommendations.append(
                "Add original diagrams, flowcharts, or data visualizations (e.g. as inline SVG or via a charting "
                "library) to illustrate key concepts and processes."
            )
 
        if total_original_visuals > 0 and captioned_figures < total_original_visuals:
            recommendations.append(
                "Wrap original diagrams/charts in <figure> with a <figcaption> describing the data or process shown — "
                "this gives multi-modal LLMs explicit, citable context for the visual."
            )
 
    return {
        "factor": "Original Diagrams and Charts",
        "score": score,
        "status": "Good" if score >= 75 else "Average" if score >= 40 else "Poor",
        "details": details,
        "recommendations": recommendations
    }
 
 
# plugin loader in main.py looks for a `run` attribute
run = analyze_original_diagrams_vs_stock