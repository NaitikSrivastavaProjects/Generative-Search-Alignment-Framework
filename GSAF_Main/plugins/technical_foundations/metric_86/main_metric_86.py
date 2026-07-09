import requests
import xml.etree.ElementTree as ET
from models.metric_result import MetricResult
from utils.helpers import get_status


def fetch_sitemap_urls(sitemap_url):
    try:
        response = requests.get(
            sitemap_url,
            headers={"User-Agent": "Mozilla/5.0 SEO Analyzer Bot"},
            timeout=10
        )
        if response.status_code != 200:
            return []

        root = ET.fromstring(response.content)
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        # handle sitemap index files pointing to other sitemaps
        sitemap_refs = root.findall("sm:sitemap/sm:loc", namespace)
        if sitemap_refs:
            urls = []
            for ref in sitemap_refs[:3]:  # check first 3 sub-sitemaps only
                urls.extend(fetch_sitemap_urls(ref.text.strip()))
            return urls

        return [loc.text.strip() for loc in root.findall("sm:url/sm:loc", namespace)]

    except Exception:
        return []


def run(site_data):
    result = MetricResult(factor="86 - Sitemap Inclusion")

    try:
        domain = site_data.domain
        url = site_data.url

        # check robots.txt for custom sitemap location first
        robots_url = f"https://{domain}/robots.txt"
        sitemap_url = f"https://{domain}/sitemap.xml"

        try:
            robots = requests.get(robots_url, timeout=8).text
            for line in robots.splitlines():
                if line.lower().startswith("sitemap:"):
                    sitemap_url = line.split(":", 1)[1].strip()
                    break
        except Exception:
            pass

        sitemap_urls = fetch_sitemap_urls(sitemap_url)

        result.details["sitemap_url"] = sitemap_url
        result.details["total_urls_in_sitemap"] = len(sitemap_urls)

        if not sitemap_urls:
            result.score = 0
            result.recommendations.append(
                "No sitemap found. Create and submit a sitemap.xml to help crawlers discover your pages."
            )
        elif url in sitemap_urls:
            result.score = 100
            result.details["page_in_sitemap"] = True
        else:
            result.score = 40
            result.details["page_in_sitemap"] = False
            result.recommendations.append(
                "Sitemap exists but this specific page URL was not found in it. "
                "Add this page to your sitemap to ensure it gets crawled."
            )

        result.status = get_status(result.score)

    except Exception as e:
        result.error = str(e)

    return result.to_dict()