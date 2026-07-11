import time
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from models.metric_result import MetricResult
from utils.helpers import get_status


MAX_PAGES = 10


def crawl_internal_pages(base_url, domain):
    visited = set()
    to_visit = [base_url]
    pages = {}

    while to_visit and len(visited) < MAX_PAGES:
        url = to_visit.pop(0)
        if url in visited:
            continue
        try:
            res = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0 SEO Analyzer Bot"},
                timeout=8
            )
            soup = BeautifulSoup(res.text, "html.parser")

            title = soup.find("title")
            headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])]
            pages[url] = (title.get_text(strip=True) if title else "") + " ".join(headings)

            visited.add(url)

            for a in soup.find_all("a", href=True):
                full_url = urljoin(base_url, a["href"])
                if domain in full_url and full_url not in visited:
                    to_visit.append(full_url)

            time.sleep(0.5)

        except Exception:
            continue

    return pages


def run(site_data):
    result = MetricResult(factor="55 - Topical Authority Clusters")

    try:
        domain = site_data.domain
        pages = crawl_internal_pages(site_data.url, domain)

        result.details["pages_crawled"] = len(pages)

        if len(pages) < 2:
            result.score = 0
            result.status = get_status(result.score)
            result.recommendations.append(
                "Not enough internal pages found to assess topical clustering. "
                "Build out related content pages linking to each other."
            )
            return result.to_dict()

        texts = list(pages.values())
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(texts)

        base_vector = tfidf_matrix[0]
        similarities = cosine_similarity(base_vector, tfidf_matrix[1:])[0]

        avg_similarity = float(similarities.mean())
        result.details["average_topic_similarity"] = round(avg_similarity, 3)
        result.details["pages_analyzed"] = list(pages.keys())

        result.score = min(100, round(avg_similarity * 100))
        result.status = get_status(result.score)

        if avg_similarity < 0.3:
            result.recommendations.append(
                "Internal pages show low topical consistency. "
                "Build hub-and-spoke content clusters around your core topics."
            )

    except Exception as e:
        result.error = str(e)

    return result.to_dict()