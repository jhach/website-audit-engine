import sys
import json
from pathlib import Path

from fetch_page import fetch_homepage
from extract_content import extract_basic_seo
from extract_schema import extract_schema_types
from build_report import build_markdown_report


def normalize_domain(url: str) -> str:
    domain = url.replace("https://", "").replace("http://", "").split("/")[0]
    return domain


def main():
    if len(sys.argv) < 2:
        print("Usage: python src/main.py https://example.com")
        return

    url = sys.argv[1]
    domain = normalize_domain(url)

    base_dir = Path("audits") / domain
    raw_html_dir = base_dir / "raw" / "html"
    processed_dir = base_dir / "processed"
    report_dir = base_dir / "report"
    raw_schema_dir = base_dir / "raw" / "schema"

    raw_html_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    raw_schema_dir.mkdir(parents=True, exist_ok=True)

    html_path = fetch_homepage(url, raw_html_dir)

    summary = extract_basic_seo(html_path, url)
    schema_summary = extract_schema_types(html_path)

    summary["schema"] = {
        "schema_found": schema_summary["schema_found"],
        "schema_block_count": schema_summary["schema_block_count"],
        "schema_types": schema_summary["schema_types"],
        "has_organization": schema_summary["has_organization"],
        "has_local_business": schema_summary["has_local_business"],
        "has_website": schema_summary["has_website"],
        "has_breadcrumb": schema_summary["has_breadcrumb"],
        "has_faq": schema_summary["has_faq"],
    }

    summary_path = processed_dir / "homepage_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    raw_schema_path = raw_schema_dir / "home_schema_blocks.json"
    raw_schema_path.write_text(json.dumps(schema_summary["raw_blocks"], indent=2), encoding="utf-8")

    report_path = report_dir / "audit_report.md"
    build_markdown_report(summary, report_path)

    print(f"Saved summary JSON to {summary_path}")
    print(f"Saved raw schema blocks to {raw_schema_path}")
    print(f"Saved markdown report to {report_path}")


if __name__ == "__main__":
    main()