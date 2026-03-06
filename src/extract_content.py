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

    h1_tag = soup.find("h1")
    h1 = h1_tag.get_text(strip=True) if h1_tag else None

    h2_tags = soup.find_all("h2")
    h2s = [tag.get_text(strip=True) for tag in h2_tags if tag.get_text(strip=True)]

    body_text = soup.get_text(separator=" ", strip=True)
    word_count = len(body_text.split()) if body_text else 0

    return {
        "url": url,
        "title": title,
        "meta_description": meta_description,
        "canonical": canonical,
        "robots": robots,
        "h1": h1,
        "h2s": h2s,
        "word_count": word_count,
    }