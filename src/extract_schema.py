import json
from pathlib import Path
from bs4 import BeautifulSoup


def extract_schema_types(html_path: Path) -> dict:
    html = html_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "lxml")

    schema_blocks = soup.find_all("script", attrs={"type": "application/ld+json"})

    raw_blocks = []
    schema_types = []

    for block in schema_blocks:
        raw_text = block.string or block.get_text(strip=True)
        if not raw_text:
            continue

        raw_blocks.append(raw_text)

        try:
            parsed = json.loads(raw_text)

            if isinstance(parsed, list):
                for item in parsed:
                    _collect_schema_types(item, schema_types)
            else:
                _collect_schema_types(parsed, schema_types)

        except Exception:
            continue

    unique_types = sorted(list(set(schema_types)))

    return {
        "schema_found": len(raw_blocks) > 0,
        "schema_block_count": len(raw_blocks),
        "schema_types": unique_types,
        "has_organization": "Organization" in unique_types,
        "has_local_business": "LocalBusiness" in unique_types,
        "has_website": "WebSite" in unique_types,
        "has_breadcrumb": "BreadcrumbList" in unique_types,
        "has_faq": "FAQPage" in unique_types,
        "raw_blocks": raw_blocks,
    }


def _collect_schema_types(item, schema_types):
    if isinstance(item, dict):
        item_type = item.get("@type")
        if isinstance(item_type, list):
            schema_types.extend(item_type)
        elif isinstance(item_type, str):
            schema_types.append(item_type)

        graph = item.get("@graph")
        if isinstance(graph, list):
            for graph_item in graph:
                _collect_schema_types(graph_item, schema_types)