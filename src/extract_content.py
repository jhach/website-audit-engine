from pathlib import Path
from bs4 import BeautifulSoup


def extract_basic_seo(html_path: Path, url: str) -> dict:
    html = html_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "lxml")

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else None

    meta_description_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = (
        meta_description_tag.get("content", "").strip()
        if meta_description_tag and meta_description_tag.get("content")
        else None
    )

    canonical_tag = soup.find("link", attrs={"rel": "canonical"})
    canonical = (
        canonical_tag.get("href", "").strip()
        if canonical_tag and canonical_tag.get("href")
        else None
    )

    robots_tag = soup.find("meta", attrs={"name": "robots"})
    robots = (
        robots_tag.get("content", "").strip()
        if robots_tag and robots_tag.get("content")
        else None
    )

    h1_tags = soup.find_all("h1")
    h1 = h1_tags[0].get_text(strip=True) if h1_tags else None
    h1_count = len(h1_tags)

    h2_tags = soup.find_all("h2")
    h2s = [tag.get_text(strip=True) for tag in h2_tags if tag.get_text(strip=True)]

    body_text = soup.get_text(separator=" ", strip=True)
    word_count = len(body_text.split()) if body_text else 0

    return {
        "url": url,
        "title": title,
        "title_length": len(title) if title else 0,
        "meta_description": meta_description,
        "meta_description_length": len(meta_description) if meta_description else 0,
        "canonical": canonical,
        "robots": robots,
        "h1": h1,
        "h1_count": h1_count,
        "h2s": h2s,
        "h2_count": len(h2s),
        "word_count": word_count,
    }


def detect_location_mentions(html_path: Path, location_config: dict, title: str = "", h1: str = "") -> dict:
    html = html_path.read_text(encoding="utf-8", errors="ignore").lower()

    broad_terms = location_config.get("broad_terms", [])
    priority_suburbs = location_config.get("priority_suburbs", [])
    all_suburbs = location_config.get("all_suburbs", [])

    broad_mentions = _count_term_mentions(html, broad_terms)
    priority_suburb_mentions = _count_term_mentions(html, priority_suburbs)
    all_suburb_mentions = _count_term_mentions(html, all_suburbs)

    found_broad_terms = [term for term, count in broad_mentions.items() if count > 0]
    found_priority_suburbs = [term for term, count in priority_suburb_mentions.items() if count > 0]
    found_all_suburbs = [term for term, count in all_suburb_mentions.items() if count > 0]

    missing_broad_terms = [term for term, count in broad_mentions.items() if count == 0]
    missing_priority_suburbs = [term for term, count in priority_suburb_mentions.items() if count == 0]

    title_lower = (title or "").lower()
    h1_lower = (h1 or "").lower()

    title_has_local_term = any(term.lower() in title_lower for term in broad_terms + priority_suburbs + all_suburbs)
    h1_has_local_term = any(term.lower() in h1_lower for term in broad_terms + priority_suburbs + all_suburbs)

    return {
        "broad_mentions": broad_mentions,
        "priority_suburb_mentions": priority_suburb_mentions,
        "all_suburb_mentions": all_suburb_mentions,
        "found_broad_terms": found_broad_terms,
        "found_priority_suburbs": found_priority_suburbs,
        "found_all_suburbs": found_all_suburbs,
        "missing_broad_terms": missing_broad_terms,
        "missing_priority_suburbs": missing_priority_suburbs,
        "has_any_broad_term": len(found_broad_terms) > 0,
        "has_any_priority_suburb": len(found_priority_suburbs) > 0,
        "has_any_suburb": len(found_all_suburbs) > 0,
        "title_has_local_term": title_has_local_term,
        "h1_has_local_term": h1_has_local_term
    }


def _count_term_mentions(html: str, terms: list[str]) -> dict:
    mentions = {}

    for term in terms:
        clean_term = term.strip()
        if not clean_term:
            continue

        count = html.count(clean_term.lower())
        mentions[term] = count

    return mentions