from __future__ import annotations

import argparse
import json
from pathlib import Path

from pdf_report import build_pdf_report
from scorecard import calculate_score
from lighthouse_audit import run_lighthouse
from opportunity_summary import build_opportunity_summary

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
        "pages_missing_all_suburbs": pages_missing_all_suburbs,
    }


def run_audit(
    url: str,
    output_root: str | Path = "audits",
    business_name: str | None = None,
    max_pages: int = 5,
    generate_pdf: bool = True,
    generate_screenshots: bool = True,
) -> dict:
    """
    Runs a single website audit and returns a structured result.
    """

    domain = normalize_domain(url)
    location_config = load_location_terms()

    base_dir = Path(output_root)
    if business_name:
        # batch mode usually passes a custom output_root like reports/business-name
        audit_dir = base_dir
    else:
        # single-site mode defaults to audits/domain
        audit_dir = base_dir / domain

    raw_html_dir = audit_dir / "raw" / "html"
    processed_dir = audit_dir / "processed"
    report_dir = audit_dir / "report"
    raw_schema_dir = audit_dir / "raw" / "schema"
    raw_screenshot_dir = audit_dir / "raw" / "screenshots"
    raw_lighthouse_dir = audit_dir / "raw" / "lighthouse"

    raw_html_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    raw_schema_dir.mkdir(parents=True, exist_ok=True)
    raw_lighthouse_dir.mkdir(parents=True, exist_ok=True)
    raw_screenshot_dir.mkdir(parents=True, exist_ok=True)

    pages = discover_top_pages(url, max_pages=max_pages)
    all_page_summaries = []
    page_errors = []

    for page in pages:
        page_url = page["url"]
        slug = page["slug"]

        try:
            html_path = fetch_page(page_url, raw_html_dir, slug)

            desktop_path = raw_screenshot_dir / f"{slug}_desktop.png"
            mobile_path = raw_screenshot_dir / f"{slug}_mobile.png"

            if generate_screenshots:
                capture_screenshots(page_url, desktop_path, mobile_path)

            seo_summary = extract_basic_seo(html_path, page_url)
            location_summary = detect_location_mentions(
                html_path,
                location_config,
                title=seo_summary.get("title", ""),
                h1=seo_summary.get("h1", "")
            )
            schema_summary = extract_schema_types(html_path)
            trust_summary = detect_trust_signals(html_path)

            seo_summary["slug"] = slug
            seo_summary["desktop_screenshot"] = str(desktop_path) if generate_screenshots else ""
            seo_summary["mobile_screenshot"] = str(mobile_path) if generate_screenshots else ""
            seo_summary["location_signals"] = location_summary
            seo_summary["trust_signals"] = trust_summary
            seo_summary["title_has_local_term"] = location_summary.get("title_has_local_term", False)
            seo_summary["h1_has_local_term"] = location_summary.get("h1_has_local_term", False)
            seo_summary["schema"] = {
                "schema_found": schema_summary["schema_found"],
                "schema_block_count": schema_summary["schema_block_count"],
                "schema_types": schema_summary["schema_types"],
                "has_organization": schema_summary["has_organization"],
                "has_local_business": schema_summary["has_local_business"],
                "has_website": schema_summary["has_website"],
                "has_breadcrumb": schema_summary["has_breadcrumb"],
                "has_faq": schema_summary["has_faq"],
            }

            if slug == "home":
                lighthouse_summary = run_lighthouse(page_url, raw_lighthouse_dir, slug)
                seo_summary["lighthouse"] = lighthouse_summary

            seo_summary["scorecard"] = calculate_score(seo_summary)
            seo_summary["opportunity_summary"] = build_opportunity_summary(seo_summary)

            raw_schema_path = raw_schema_dir / f"{slug}_schema_blocks.json"
            raw_schema_path.write_text(
                json.dumps(schema_summary["raw_blocks"], indent=2),
                encoding="utf-8"
            )

            all_page_summaries.append(seo_summary)

        except Exception as e:
            page_errors.append({
                "url": page_url,
                "slug": slug,
                "error": str(e),
            })
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

    report_path = report_dir / "audit_report.md"
    pdf_path = report_dir / "audit_report.pdf"
    homepage_summary_path = processed_dir / "homepage_summary.json"
    errors_path = processed_dir / "page_errors.json"

    errors_path.write_text(json.dumps(page_errors, indent=2), encoding="utf-8")

    if homepage_summary:
        homepage_summary_path.write_text(
            json.dumps(homepage_summary, indent=2),
            encoding="utf-8"
        )

        build_markdown_report(homepage_summary, report_path)

        if generate_pdf:
            build_pdf_report(homepage_summary, pdf_path)

    result = {
        "business_name": business_name or domain,
        "url": url,
        "domain": domain,
        "audit_dir": str(audit_dir),
        "page_inventory_path": str(page_inventory_path),
        "site_summary_path": str(site_summary_path),
        "homepage_summary_path": str(homepage_summary_path) if homepage_summary else "",
        "markdown_report_path": str(report_path) if homepage_summary else "",
        "pdf_report_path": str(pdf_path) if homepage_summary and generate_pdf else "",
        "total_pages_discovered": len(pages),
        "total_pages_audited": len(all_page_summaries),
        "page_errors": page_errors,
        "homepage_summary": homepage_summary,
        "site_summary": site_summary,
        "status": "success" if homepage_summary else "partial",
    }

    summary_output_path = processed_dir / "audit_result.json"
    summary_output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a local SEO website audit.")
    parser.add_argument("url", help="Website URL to audit")
    parser.add_argument("--business-name", default="", help="Business name")
    parser.add_argument("--output-root", default="audits", help="Base output folder")
    parser.add_argument("--max-pages", type=int, default=5, help="Maximum pages to crawl")
    parser.add_argument("--no-pdf", action="store_true", help="Skip PDF generation")
    parser.add_argument("--no-screenshots", action="store_true", help="Skip screenshots")
    return parser.parse_args()


def main():
    args = parse_args()

    result = run_audit(
        url=args.url,
        output_root=args.output_root,
        business_name=args.business_name or None,
        max_pages=args.max_pages,
        generate_pdf=not args.no_pdf,
        generate_screenshots=not args.no_screenshots,
    )

    print(json.dumps({
        "status": result["status"],
        "business_name": result["business_name"],
        "url": result["url"],
        "audit_dir": result["audit_dir"],
        "markdown_report_path": result["markdown_report_path"],
        "pdf_report_path": result["pdf_report_path"],
        "total_pages_audited": result["total_pages_audited"],
        "page_errors": len(result["page_errors"]),
    }, indent=2))


if __name__ == "__main__":
    main()