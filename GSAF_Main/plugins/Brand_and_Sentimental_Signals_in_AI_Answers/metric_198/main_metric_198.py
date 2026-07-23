import re
import json
 
 
FOUNDER_TITLE_PATTERNS = [
    r"\bfounder\b", r"\bco-founder\b", r"\bcofounder\b",
    r"\bceo and founder\b", r"\bfounder and ceo\b", r"\bfounder & ceo\b"
]
 
QUOTE_ATTRIBUTION_PATTERNS = [
    r'"[^"]{15,}"\s*[,-]?\s*(?:said|says|explains|notes|shares)\s+',
    r'(?:said|says|explains|notes|shares)\s+[A-Z][a-z]+\s+[A-Z][a-z]+',
]
 
PODCAST_INTERVIEW_DOMAINS = [
    "open.spotify.com", "podcasts.apple.com", "soundcloud.com",
    "youtube.com", "youtu.be", "buzzsprout.com", "libsyn.com"
]
 
EXTERNAL_APPEARANCE_PHRASES = [
    "guest on", "interviewed on", "featured guest", "appeared on",
    "spoke at", "keynote at", "panelist at", "guest post on", "wrote for"
]
 
SAMEAS_AUTHORITY_DOMAINS = [
    "linkedin.com", "twitter.com", "x.com", "crunchbase.com",
    "forbes.com", "muckrack.com"
]
 
 
def _get_json_ld_blocks(soup):
    blocks = []
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "{}")
        except (json.JSONDecodeError, TypeError):
            continue
        candidates = data if isinstance(data, list) else [data]
        for block in candidates:
            if isinstance(block, dict):
                blocks.append(block)
                graph = block.get("@graph")
                if isinstance(graph, list):
                    blocks.extend(b for b in graph if isinstance(b, dict))
    return blocks
 
 
def _extract_founder_from_schema(blocks):
    for block in blocks:
        if block.get("@type") in ("Organization", "Brand"):
            founder = block.get("founder")
            if isinstance(founder, dict):
                return founder.get("name"), founder
            if isinstance(founder, str):
                return founder, None
            if isinstance(founder, list) and founder:
                first = founder[0]
                if isinstance(first, dict):
                    return first.get("name"), first
                if isinstance(first, str):
                    return first, None
    return None, None
 
 
def _extract_founder_person_schema(blocks, founder_name):
    for block in blocks:
        if block.get("@type") == "Person":
            name = block.get("name", "")
            job_title = (block.get("jobTitle") or "").lower()
            if (founder_name and founder_name.lower() in name.lower()) or \
               any(re.search(p, job_title) for p in FOUNDER_TITLE_PATTERNS):
                return block
    return None
 
 
def _find_founder_mention_in_text(soup, founder_name):
    text = soup.get_text(" ", strip=True)
    if founder_name and founder_name in text:
        return True
 
    lower = text.lower()
    return any(re.search(pattern, lower) for pattern in FOUNDER_TITLE_PATTERNS)
 
 
def _find_founder_bio_section(soup, founder_name):
    headings = soup.find_all(["h1", "h2", "h3", "h4"])
    for heading in headings:
        heading_text = heading.get_text(strip=True).lower()
        if "founder" in heading_text or "about" in heading_text or \
           (founder_name and founder_name.lower() in heading_text):
            return heading
 
    author_divs = soup.find_all(attrs={"class": re.compile(r"(author|bio|founder)", re.IGNORECASE)})
    return author_divs[0] if author_divs else None
 
 
def _find_founder_bylines(soup, founder_name):
    if not founder_name:
        return 0
 
    bylines = soup.find_all(attrs={"rel": "author"})
    byline_hits = sum(1 for b in bylines if founder_name.lower() in b.get_text(strip=True).lower())
 
    author_class_els = soup.find_all(attrs={"class": re.compile(r"(byline|author)", re.IGNORECASE)})
    author_hits = sum(
        1 for el in author_class_els if founder_name.lower() in el.get_text(strip=True).lower()
    )
 
    return byline_hits + author_hits
 
 
def _find_founder_quotes(soup, founder_name):
    text = soup.get_text(" ", strip=True)
    quote_count = 0
 
    if founder_name:
        name_quote_pattern = re.compile(
            rf'"[^"]{{15,}}"\s*[,-]?\s*(?:said|says|explains|notes|shares|according to)\s+{re.escape(founder_name)}',
            re.IGNORECASE
        )
        quote_count += len(name_quote_pattern.findall(text))
 
    for pattern in QUOTE_ATTRIBUTION_PATTERNS:
        quote_count += len(re.findall(pattern, text))
 
    return quote_count
 
 
def _find_external_appearance_signals(soup, founder_name):
    text = soup.get_text(" ", strip=True).lower()
    phrase_hits = sum(1 for phrase in EXTERNAL_APPEARANCE_PHRASES if phrase in text)
 
    podcast_links = [
        a["href"] for a in soup.find_all("a", href=True)
        if any(domain in a["href"].lower() for domain in PODCAST_INTERVIEW_DOMAINS)
    ]
 
    return phrase_hits, len(podcast_links)
 
 
def analyze_founder_authority(site_data):
 
    soup = site_data.soup
    blocks = _get_json_ld_blocks(soup)
 
    founder_name, founder_schema_obj = _extract_founder_from_schema(blocks)
    founder_person_schema = _extract_founder_person_schema(blocks, founder_name)
 
    founder_mentioned = _find_founder_mention_in_text(soup, founder_name)
    founder_bio_section = _find_founder_bio_section(soup, founder_name)
    founder_bylines = _find_founder_bylines(soup, founder_name)
    founder_quotes = _find_founder_quotes(soup, founder_name)
    appearance_phrase_hits, podcast_link_count = _find_external_appearance_signals(soup, founder_name)
 
    sameas_links = []
    if founder_person_schema:
        same_as = founder_person_schema.get("sameAs", [])
        sameas_links = same_as if isinstance(same_as, list) else [same_as]
    has_authority_sameas = any(
        any(domain in link for domain in SAMEAS_AUTHORITY_DOMAINS) for link in sameas_links if link
    )
 
    score = 0
 
    if founder_name:
        score += 15
    if founder_person_schema:
        score += 20
    if has_authority_sameas:
        score += 10
    if founder_bio_section is not None:
        score += 10
    if founder_bylines > 0:
        score += min(founder_bylines, 3) * 5
    if founder_quotes > 0:
        score += min(founder_quotes, 3) * 8
    if appearance_phrase_hits > 0:
        score += min(appearance_phrase_hits, 3) * 5
    if podcast_link_count > 0:
        score += min(podcast_link_count, 3) * 5
 
    score = max(0, min(score, 100))
 
    details = {
        "founder_name_detected": founder_name,
        "founder_organization_schema_present": founder_schema_obj is not None,
        "founder_person_schema_present": founder_person_schema is not None,
        "founder_sameas_authority_links": [
            l for l in sameas_links if any(d in l for d in SAMEAS_AUTHORITY_DOMAINS)
        ],
        "founder_bio_section_found": founder_bio_section is not None,
        "founder_bylines_found": founder_bylines,
        "founder_quotes_found": founder_quotes,
        "external_appearance_phrases_found": appearance_phrase_hits,
        "podcast_or_video_interview_links": podcast_link_count,
        "founder_mentioned_anywhere": founder_mentioned
    }
 
    recommendations = []
 
    if score < 75:
 
        if not founder_name:
            recommendations.append(
                "Add the founder's name to Organization structured data (the \"founder\" field) so LLMs can "
                "associate a named individual with the brand narrative."
            )
 
        if founder_name and not founder_person_schema:
            recommendations.append(
                "Add Person structured data for the founder with jobTitle and sameAs links to their LinkedIn, "
                "Twitter/X, and other authoritative profiles."
            )
 
        if founder_person_schema and not has_authority_sameas:
            recommendations.append(
                "Link the founder's Person schema to authoritative external profiles (LinkedIn, Crunchbase, "
                "press profiles) via sameAs to strengthen entity authority."
            )
 
        if founder_bio_section is None:
            recommendations.append(
                "Add a founder bio section (e.g. on an About page) describing their background and expertise."
            )
 
        if founder_bylines == 0:
            recommendations.append(
                "Attribute some articles/content directly to the founder with a byline — founder-authored "
                "content builds authorship signals LLMs use to shape brand narrative."
            )
 
        if founder_quotes == 0:
            recommendations.append(
                "Include direct, attributed quotes from the founder in content — quoted commentary is a "
                "strong signal LLMs draw on when generating brand-related answers."
            )
 
        if appearance_phrase_hits == 0 and podcast_link_count == 0:
            recommendations.append(
                "Reference or link to the founder's external appearances (podcasts, interviews, guest posts, "
                "conference talks) to build authority signals beyond your own site."
            )
 
    return {
        "factor": "Founder Authority Building",
        "score": score,
        "status": "Good" if score >= 75 else "Average" if score >= 40 else "Poor",
        "details": details,
        "recommendations": recommendations
    }
 
 
# plugin loader in main.py looks for a `run` attribute
run = analyze_founder_authority