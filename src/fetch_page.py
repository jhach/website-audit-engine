import requests
from pathlib import Path


def fetch_page(url: str, output_dir, slug: str) -> Path:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=20, verify=False)
        response.raise_for_status()

        html = response.text
        output_path = Path(output_dir) / f"{slug}_raw.html"
        output_path.write_text(html, encoding="utf-8")

        print(f"Saved HTML for {url} to {output_path}")
        return output_path

    except Exception as e:
        print(f"Error fetching page {url}: {e}")
        raise


def fetch_homepage(url: str, output_dir) -> Path:
    return fetch_page(url, output_dir, "home")