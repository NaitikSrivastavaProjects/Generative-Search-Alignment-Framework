import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from models.site_data import SiteData
import os
from dotenv import load_dotenv

load_dotenv()

OPR_API_KEY = os.getenv("OPR_API_KEY")
OPR_API_URL = "https://openpagerank.com/api/v1.0/getPageRank"


def get_status(score):
    if score is None:
        return None
    if score >= 75:
        return "Good"
    if score >= 40:
        return "Average"
    return "Poor"


def fetch_opr_data(domain):
    if not OPR_API_KEY:
        return None
    try:
        response = requests.get(
            OPR_API_URL,
            headers={"API-OPR": OPR_API_KEY},
            params={"domains[]": domain},
            timeout=10
        )
        data = response.json()
        result = data["response"][0]
        return {
            "open_page_rank": result.get("page_rank_decimal", 0),
            "referring_domains": result.get("referring_domains", 0),
            "rank": result.get("rank", 0)
        }
    except Exception:
        return None


def build_site_data(url, keyword="", keywords=None, competitor_url=""):
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0 SEO Analyzer Bot"},
        timeout=10,
        allow_redirects=True
    )
    soup = BeautifulSoup(response.text, "html.parser")

    json_ld = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            json_ld.append(json.loads(script.string))
        except Exception:
            continue

    domain = urlparse(url).netloc
    opr_data = fetch_opr_data(domain)

    return SiteData(
        url=url,
        html=response.text,
        soup=soup,
        response=response,
        keyword=keyword,
        keywords=keywords or [],
        competitor_url=competitor_url,
        domain=domain,
        json_ld=json_ld,
        ai_results={},
        opr_data=opr_data
    )