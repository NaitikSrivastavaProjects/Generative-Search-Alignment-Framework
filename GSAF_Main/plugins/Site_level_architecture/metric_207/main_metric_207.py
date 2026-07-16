"""
Factor 207 - Contact Us Page
Detects contact links, emails, and phone numbers.
"""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from models.metric_result import MetricResult

def run(site_data):
    result = MetricResult(factor="207 - Contact Us Page")

    try:
        page_url = site_data.url
        
        # Fetch and parse HTML (replacing self.fetch_html())
        response = requests.get(page_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        links = soup.find_all("a", href=True)
        contact_found = False

        for link in links:
            text = link.get_text(strip=True).lower()
            href = link["href"].lower()

            if "contact" in text or "contact" in href:
                contact_found = True
                result.details["contact_page"] = urljoin(page_url, link["href"])
                break

        page = soup.get_text(" ")

        email = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", page)
        phone = re.search(r"\+?\d[\d\s\-\(\)]{7,}", page)

        score = 0
        if contact_found:
            score += 40
        if email:
            score += 30
        if phone:
            score += 30

        result.score = score
        
        # Adding a basic status fallback based on the score
        if score >= 70:
            result.status = "Found"
        elif score > 0:
            result.status = "Partial"
        else:
            result.status = "Not Found"

        result.details["contact_found"] = contact_found
        result.details["email_found"] = bool(email)
        result.details["phone_found"] = bool(phone)

    except Exception as e:
        result.error = str(e)

    return result.to_dict()