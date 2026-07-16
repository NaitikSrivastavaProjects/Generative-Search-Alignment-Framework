"""
Factor 207 - Contact Us Page
Detects contact links, emails, and phone numbers.
"""

import re
from urllib.parse import urljoin
from models.metric_result import MetricResult

def run(site_data):
    result = MetricResult(factor="207 - Contact Us Page")

    # Early Exit: Ensure parsed HTML exists from the central fetcher
    if not hasattr(site_data, 'soup') or not site_data.soup:
        result.error = "Parsed HTML (soup) not found in site_data"
        result.status = "Error"
        result.score = 0
        return result.to_dict()

    try:
        page_url = getattr(site_data, 'url', '')
        
        # Pull the already-fetched and parsed HTML
        soup = site_data.soup
        raw_html = getattr(site_data, 'raw_html', str(soup)).lower()

        links = soup.find_all("a", href=True)
        contact_found = False

        for link in links:
            text = link.get_text(strip=True).lower()
            href = link["href"].lower()

            if "contact" in text or "contact" in href:
                contact_found = True
                result.details["contact_page"] = urljoin(page_url, link["href"])
                break

        page_text = soup.get_text(" ")

        email = bool(re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", page_text))
        phone = bool(re.search(r"\+?\d[\d\s\-\(\)]{7,}", page_text))

        # Minimal fallbacks using the pre-fetched raw HTML
        if not contact_found and "contact" in raw_html:
            contact_found = True

        if not email and "mailto:" in raw_html:
            email = True

        if not phone and "tel:" in raw_html:
            phone = True

        score = 0
        if contact_found:
            score += 40
        if email:
            score += 30
        if phone:
            score += 30

        result.score = score
        
        # Basic status fallback based on the score
        if score >= 70:
            result.status = "Found"
        elif score > 0:
            result.status = "Partial"
        else:
            result.status = "Not Found"

        result.details["contact_found"] = contact_found
        result.details["email_found"] = email
        result.details["phone_found"] = phone

    except Exception as e:
        result.error = str(e)
        result.status = "Error"
        result.score = 0

    return result.to_dict()