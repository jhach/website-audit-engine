from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup


def discover_top_pages(start_url: str, max_pages: int = 5) -> list[dict]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(start_url, headers=headers, timeout=20, verify=False)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    start_domain = urlparse(start_url).netloc
    discovered = []
    seen = set()

    # Always include homepage first
    discovered.append({"url": start_url, "slug": "home"})
    seen.add(_normalize_url(start_url))

    for link in soup.find_all("a", href=True):
        href = link["href"].strip()

        if not href:
            continue

        absolute_url = urljoin(start_url, href)
        normalized_url = _normalize_url(absolute_url)

        if not normalized_url:
            continue

        parsed = urlparse(normalized_url)

        # Same domain only
        if parsed.netloc != start_domain:
            continue

        # Skip junk URLs
        if _should_skip_url(normalized_url):
            continue

        if normalized_url in seen:
            continue

        slug = _url_to_slug(normalized_url, start_domain)
        discovered.append({"url": normalized_url, "slug": slug})
        seen.add(normalized_url)

        if len(discovered) >= max_pages:
            break

    return discovered


def _normalize_url(url: str) -> str:
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        return ""

    cleaned = parsed._replace(fragment="", query="")
    normalized = cleaned.geturl().rstrip("/")

    # Preserve root slash as domain root
    if normalized == f"{parsed.scheme}://{parsed.netloc}":
        return normalized + "/"

    return normalized


def _should_skip_url(url: str) -> bool:
    lower = url.lower()

    skip_patterns = [
        ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".pdf",
        ".doc", ".docx", ".xls", ".xlsx", ".zip",
        "/wp-admin", "/wp-login", "/cart", "/checkout", "/my-account",
        "mailto:", "tel:", "javascript:"
    ]

    return any(pattern in lower for pattern in skip_patterns)


def _url_to_slug(url: str, domain: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")

    if not path:
        return "home"

    slug = path.replace("/", "-")
    return slug[:100]