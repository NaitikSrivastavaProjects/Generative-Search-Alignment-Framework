# credential keywords for author bio detection (metric 61)
STRONG_CREDENTIALS = [
    "phd", "ph.d", "md", "m.d", "mbbs", "professor",
    "dr.", "licensed", "board certified", "peer reviewed"
]

MODERATE_CREDENTIALS = [
    "certified", "specialist", "expert", "researcher",
    "years of experience", "journalist", "author of"
]

WEAK_CREDENTIALS = [
    "writer", "contributor", "editor", "staff"
]

# editorial review phrases for byline detection (metric 66)
EDITORIAL_STRONG = [
    "medically reviewed by", "clinically reviewed",
    "reviewed by a licensed", "medical review", "peer reviewed"
]

EDITORIAL_MEDIUM = [
    "fact-checked by", "verified by", "independently verified",
    "reviewed for accuracy"
]

EDITORIAL_WEAK = [
    "edited by", "approved by", "reviewed by our editors",
    "quality checked"
]

# year-sensitive content signals for title year check (metric 94)
YEAR_SENSITIVE_KEYWORDS = [
    "best", "top", "review", "reviews", "comparison", "vs",
    "ranking", "rankings", "tools", "salary", "salaries",
    "statistics", "stats", "trends", "guide", "alternatives"
]

# commercial anchor text keywords for press release spam (metric 187)
COMMERCIAL_KEYWORDS = [
    "buy", "cheap", "discount", "best price", "order now",
    "affordable", "deals", "sale", "lowest price", "free shipping",
    "coupon", "promo", "offer", "shop now"
]

# date-related keywords for freshness checks (metric 67, 90)
DATE_KEYWORDS = [
    "updated", "published", "last modified", "reviewed", "modified"
]

# generic anchor text phrases for anchor text bucketing (metric 185)
GENERIC_ANCHOR_PHRASES = [
    "click here", "read more", "visit", "this site",
    "source", "learn more", "here", "link"
]

# comment and forum URL patterns for spam detection (metric 195)
COMMENT_FORUM_PATTERNS = [
    "/comment/", "/comments/", "?comment-", "#comment-",
    "/forum/", "/discussion/", "/reply/", "/thread/",
    "/board/", "/topic/", "/community/", "/guestbook/", "?p="
]

# disclosure keywords for conflict of interest check (metric 69)
DISCLOSURE_KEYWORDS = [
    "affiliate", "sponsored", "paid partnership",
    "advertiser disclosure", "commission", "compensated",
    "in partnership with", "brand partner"
]

# commercial intent signals for conflict of interest check (metric 69)
COMMERCIAL_INTENT_SIGNALS = [
    "buy now", "best price", "our pick",
    "top rated", "we recommend"
]

# transparency page keywords for site trust check (metric 68)
TRANSPARENCY_PAGE_KEYWORDS = {
    "about": ["about", "about-us", "about_us", "who-we-are"],
    "editorial_policy": ["editorial", "editorial-policy", "guidelines"],
    "privacy_policy": ["privacy", "privacy-policy"],
    "corrections": ["corrections", "correction-policy"],
    "contact": ["contact", "contact-us"]
}

# glossary page signals for definition box eligibility (metric 78)
GLOSSARY_URL_KEYWORDS = [
    "glossary", "dictionary", "terms", "definitions"
]

# calculator-related class and id names for tool detection (metric 77)
CALCULATOR_CLASS_KEYWORDS = [
    "calculator", "calc", "estimator", "tool",
    "finder", "checker", "wizard"
]

# heading keywords suggesting calculator intent (metric 77)
CALCULATOR_HEADING_KEYWORDS = [
    "calculate", "estimate", "find your",
    "how much", "compare"
]


CONTACT_KEYWORDS = [
    "contact",
    "contact us",
    "support",
    "help",
    "reach us",
    "get in touch",
]

ADDRESS_KEYWORDS = [
    "address",
    "office",
    "location",
    "head office",
]

SITEMAP_KEYWORDS = [
    "sitemap",
    "site map",
]

PRIVACY_KEYWORDS = [
    "privacy",
    "privacy policy",
]

TERMS_KEYWORDS = [
    "terms",
    "terms of service",
    "terms and conditions",
]