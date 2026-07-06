# trusted CDN and script domains for hacked code detection (metric 192)
TRUSTED_SCRIPT_DOMAINS = [
    "cdnjs.cloudflare.com", "jquery.com", "googleapis.com",
    "bootstrapcdn.com", "unpkg.com", "jsdelivr.net",
    "cloudflare.com", "ajax.googleapis.com"
]

# authoritative domains for citation quality check (metric 63)
AUTHORITATIVE_DOMAINS = [
    ".gov", ".edu", "pubmed.ncbi.nlm.nih.gov",
    "scholar.google.com", "who.int", "cdc.gov",
    "nature.com", "science.org", "jstor.org",
    "researchgate.net", "ncbi.nlm.nih.gov"
]

# moderate authority domains for citation check (metric 63)
MODERATE_DOMAINS = [
    "wikipedia.org", "mayoclinic.org", "webmd.com",
    "bbc.com", "reuters.com", "apnews.com"
]

# professional registry domains for real-world verification (metric 70)
REGISTRY_DOMAINS = [
    "linkedin.com", "researchgate.net", "orcid.org",
    "ama-assn.org", "americanbar.org", "sec.gov",
    "npi.cms.hhs.gov", "scholar.google.com",
    "certifiedfinancialplanner.net"
]

# known live data provider domains for live embed detection (metric 92)
LIVE_DATA_PROVIDERS = [
    "widgets.coindesk.com", "tradingview.com",
    "weather.com", "ticker", "live-score"
]

# author section class/id patterns for bio detection (metrics 57, 61)
AUTHOR_CLASS_PATTERNS = [
    "author", "byline", "bio", "writer", "contributor"
]

# overlay and interstitial class patterns for popup detection (metric 85)
OVERLAY_CLASS_PATTERNS = [
    "modal", "popup", "overlay", "banner", "cookie",
    "gdpr", "newsletter", "interstitial", "lightbox"
]

# sameAs platform weights for entity linking score (metric 54)
SAMEAS_PLATFORM_WEIGHTS = {
    "wikipedia.org": 30,
    "wikidata.org": 20,
    "linkedin.com": 15,
    "crunchbase.com": 10,
    "twitter.com": 8,
    "x.com": 8,
    "instagram.com": 5,
    "facebook.com": 5,
    "imdb.com": 10,
    "youtube.com": 5,
    "github.com": 8
}

# brand schema fields and their score weights (metric 58)
BRAND_SCHEMA_FIELDS = {
    "@type": 10,
    "name": 10,
    "url": 10,
    "logo": 10,
    "founder": 15,
    "foundingDate": 15,
    "address": 15,
    "sameAs": 15
}

# scoring thresholds
SCORE_GOOD = 75
SCORE_AVERAGE = 40