from dataclasses import dataclass, field
from bs4 import BeautifulSoup


@dataclass
class SiteData:
    url: str
    html: str = None
    soup: BeautifulSoup = None
    response: object = None
    keyword: str = ""
    keywords: list = field(default_factory=list)
    competitor_url: str = ""
    domain: str = ""
    json_ld: list = field(default_factory=list)
    ai_results: dict = field(default_factory=dict)
    opr_data: dict = None  # open_page_rank, referring_domains, rank