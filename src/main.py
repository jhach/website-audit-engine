import sys
import json
from pathlib import Path
from pdf_report import build_pdf_report

from crawl import discover_top_pages
from fetch_page import fetch_page
from extract_content import extract_basic_seo, detect_location_mentions
from trust_signals import detect_trust_signals
from extract_schema import extract_schema_types
from build_report import build_markdown_report
from screenshot import capture_screenshots
from utils import load_location_terms


def normalize_domain(url: str) -> str:
    domain = url.replace("https://", "").replace("http://", "").split("/")[0]
    return domain


def main():
    if len(sys.argv) < 2:
        print("Usage: python src/main.py https://example.com")
        return

    url = sys.argv[1]
    domain = normalize_domain(url)
    location_config = load_location_terms()

    base_dir = Path("audits") / domain
    raw_html_dir = base_dir / "raw" / "html"
    processed_dir = base_dir / "processed"
    report_dir = base_dir / "report"
    raw_schema_dir = base_dir / "raw" / "schema"
    raw_screenshot_dir = base_dir / "raw" / "screenshots"

    raw_html_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    raw_schema_dir.mkdir(parents=True, exist_ok=True)
    raw_screenshot_dir.mkdir(parents=True, exist_ok=True)

    pages = discover_top_pages(url, max_pages=5)

    all_page_summaries = []

    for page in pages:
        page_url = page["url"]
        slug = page["slug"]

        try:
            html_path = fetch_page(page_url, raw_html_dir, slug)

            desktop_path = raw_screenshot_dir / f"{slug}_desktop.png"
            mobile_path = raw_screenshot_dir / f"{slug}_mobile.png"
            capture_screenshots(page_url, desktop_path, mobile_path)

            seo_summary = extract_basic_seo(html_path, page_url)
            location_summary = detect_location_mentions(html_path, location_config)
            schema_summary = extract_schema_types(html_path)
            trust_summary = detect_trust_signals(html_path)

            seo_summary["slug"] = slug
            seo_summary["desktop_screenshot"] = str(desktop_path)
            seo_summary["mobile_screenshot"] = str(mobile_path)
            seo_summary["location_signals"] = location_summary
            seo_summary["trust_signals"] = trust_summary
            seo_summary["schema"] = {
                "schema_found": schema_summary["schema_found"],
                "schema_block_count": schema_summary["schema_block_count"],
                "schema_types": schema_summary["schema_types"],
                "has_organization": schema_summary["has_organization"],
                "has_local_business": schema_summary["has_local_business"],
                "has_website": schema_summary["has_website"],
                "has_breadcrumb": schema_summary["has_breadcrumb"],
                "has_faq": schema_summary["has_faq"]
            }

            raw_schema_path = raw_schema_dir / f"{slug}_schema_blocks.json"
            raw_schema_path.write_text(
                json.dumps(schema_summary["raw_blocks"], indent=2),
                encoding="utf-8"
            )

            all_page_summaries.append(seo_summary)

        except Exception as e:
            print(f"Skipping {page_url} due to error: {e}")

    page_inventory_path = processed_dir / "page_inventory.json"
    page_inventory_path.write_text(
        json.dumps(all_page_summaries, indent=2),
        encoding="utf-8"
    )

    site_summary = build_site_summary(all_page_summaries)
    site_summary_path = processed_dir / "site_summary.json"
    site_summary_path.write_text(
        json.dumps(site_summary, indent=2),
        encoding="utf-8"
    )

    homepage_summary = next((p for p in all_page_summaries if p["slug"] == "home"), None)
    if homepage_summary:
        report_path = report_dir / "audit_report.md"
        pdf_path = report_dir / "audit_report.pdf"

        build_markdown_report(homepage_summary, report_path)
        build_pdf_report(homepage_summary, pdf_path)

        print(f"Saved markdown report to {report_path}")
        print(f"Saved PDF report to {pdf_path}")

        print(f"Saved page inventory JSON to {page_inventory_path}")
        print(f"Saved site summary JSON to {site_summary_path}")


def build_site_summary(page_summaries: list[dict]) -> dict:
    missing_titles = []
    missing_meta_descriptions = []
    missing_h1s = []
    missing_canonicals = []
    pages_without_schema = []
    pages_without_local_business_schema = []
    thin_pages = []
    pages_missing_all_broad_terms = []
    pages_missing_all_priority_suburbs = []
    pages_missing_all_suburbs = []

    for page in page_summaries:
        url = page["url"]
        schema = page.get("schema", {})
        location_signals = page.get("location_signals", {})

        if not page.get("title"):
            missing_titles.append(url)

        if not page.get("meta_description"):
            missing_meta_descriptions.append(url)

        if not page.get("h1"):
            missing_h1s.append(url)

        if not page.get("canonical"):
            missing_canonicals.append(url)

        if not schema.get("schema_found"):
            pages_without_schema.append(url)

        if schema.get("schema_found") and not schema.get("has_local_business"):
            pages_without_local_business_schema.append(url)

        if page.get("word_count", 0) < 250:
            thin_pages.append(url)

        if not location_signals.get("has_any_broad_term", False):
            pages_missing_all_broad_terms.append(url)

        if not location_signals.get("has_any_priority_suburb", False):
            pages_missing_all_priority_suburbs.append(url)

        if not location_signals.get("has_any_suburb", False):
            pages_missing_all_suburbs.append(url)

    return {
        "total_pages_audited": len(page_summaries),
        "missing_titles": missing_titles,
        "missing_meta_descriptions": missing_meta_descriptions,
        "missing_h1s": missing_h1s,
        "missing_canonicals": missing_canonicals,
        "pages_without_schema": pages_without_schema,
        "pages_without_local_business_schema": pages_without_local_business_schema,
        "thin_pages_under_250_words": thin_pages,
        "pages_missing_all_broad_terms": pages_missing_all_broad_terms,
        "pages_missing_all_priority_suburbs": pages_missing_all_priority_suburbs,
        "pages_missing_all_suburbs": pages_missing_all_suburbs
    }


if __name__ == "__main__":
    main()