import socket

import requests
from bs4 import BeautifulSoup


class SEOResult(dict):
    """Simple result container with a helper for adding detail values."""

    def add(self, key, value):
        self[key] = value


class BaseSEOPlugin:
    """Base implementation shared by all SEO plugins."""

    def __init__(self, site_data=None):
        self.site_data = site_data or {}
        self.url = self.site_data.get("url", "")
        self.keyword = self.site_data.get("keyword", "")
        self.keywords = self.site_data.get("keywords", [])
        self.competitor_url = self.site_data.get("competitor_url", "")
        self.last_response = None

    @property
    def factor(self):
        return "Unknown Factor"

    def create_result(self):
        return SEOResult({
            "factor": self.factor,
            "score": None,
            "status": "Pending",
            "details": {},
            "recommendations": [],
        })

    def set_score(self, result, score):
        result["score"] = score
        if score is None:
            result["status"] = "Error"
        elif score >= 80:
            result["status"] = "Pass"
        elif score >= 50:
            result["status"] = "Warning"
        else:
            result["status"] = "Needs Attention"

    def fetch_html(self):
        if not self.url:
            return None, BeautifulSoup("", "html.parser")

        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            response = requests.get(self.url, headers=headers, timeout=5)
            response.raise_for_status()
        except (requests.RequestException, TimeoutError, socket.timeout, KeyboardInterrupt):
            self.last_response = None
            return None, BeautifulSoup("", "html.parser")

        self.last_response = response
        soup = BeautifulSoup(response.text, "html.parser")
        return response, soup
