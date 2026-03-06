from pathlib import Path


def build_markdown_report(summary: dict, output_path: Path) -> None:
    schema = summary.get("schema", {})
    location_signals = summary.get("location_signals", {})

    location_mentions = location_signals.get("location_mentions", {})
    found_terms = location_signals.get("found_location_terms", [])
    missing_terms = location_signals.get("missing_location_terms", [])

    lines = [
        f"# Website Audit: {summary.get('url', 'Unknown URL')}",
        "",
        "## Homepage Summary",
        "",
        f"- **Title:** {summary.get('title') or 'Missing'}",
        f"- **Title length:** {summary.get('title_length', 0)}",
        f"- **Meta description:** {summary.get('meta_description') or 'Missing'}",
        f"- **Meta description length:** {summary.get('meta_description_length', 0)}",
        f"- **Canonical:** {summary.get('canonical') or 'Missing'}",
        f"- **Robots meta:** {summary.get('robots') or 'Missing'}",
        f"- **H1:** {summary.get('h1') or 'Missing'}",
        f"- **H1 count:** {summary.get('h1_count', 0)}",
        f"- **H2 count:** {summary.get('h2_count', 0)}",
        f"- **Estimated word count:** {summary.get('word_count', 0)}",
        "",
        "## Local Signals",
        "",
    ]

    if location_mentions:
        for term, count in location_mentions.items():
            lines.append(f"- **{term}:** {count} mention(s)")
    else:
        lines.append("- No location terms checked.")

    lines.extend([
        "",
        f"- **Found location terms:** {', '.join(found_terms) if found_terms else 'None'}",
        f"- **Missing location terms:** {', '.join(missing_terms) if missing_terms else 'None'}",
        "",
        "## Schema Summary",
        "",
        f"- **Schema found:** {'Yes' if schema.get('schema_found') else 'No'}",
        f"- **Schema block count:** {schema.get('schema_block_count', 0)}",
        f"- **Schema types:** {', '.join(schema.get('schema_types', [])) if schema.get('schema_types') else 'None found'}",
        f"- **Has Organization schema:** {'Yes' if schema.get('has_organization') else 'No'}",
        f"- **Has LocalBusiness schema:** {'Yes' if schema.get('has_local_business') else 'No'}",
        f"- **Has WebSite schema:** {'Yes' if schema.get('has_website') else 'No'}",
        f"- **Has Breadcrumb schema:** {'Yes' if schema.get('has_breadcrumb') else 'No'}",
        f"- **Has FAQ schema:** {'Yes' if schema.get('has_faq') else 'No'}",
        "",
        "## Initial Notes",
        "",
    ])

    if not summary.get("title"):
        lines.append("- Missing page title.")
    if summary.get("title_length", 0) > 60:
        lines.append("- Title may be too long for search results.")
    if not summary.get("meta_description"):
        lines.append("- Missing meta description.")
    if summary.get("meta_description_length", 0) > 155:
        lines.append("- Meta description may be too long for search snippets.")
    if not summary.get("h1"):
        lines.append("- Missing H1 heading.")
    if summary.get("h1_count", 0) > 1:
        lines.append("- Multiple H1 tags detected.")
    if not summary.get("canonical"):
        lines.append("- Missing canonical tag.")
    if not found_terms:
        lines.append("- No target local terms were detected on this page.")
    if not schema.get("schema_found"):
        lines.append("- No JSON-LD schema found on the page.")
    if schema.get("schema_found") and not schema.get("has_local_business"):
        lines.append("- Schema is present, but LocalBusiness schema is missing.")
    if schema.get("schema_found") and not schema.get("has_breadcrumb"):
        lines.append("- Breadcrumb schema is missing.")

    lines.extend([
        "",
        "## Hatch Studio Opportunity",
        "",
        "This site can likely improve search visibility, local relevance, and AI-readability by tightening on-page SEO, location targeting, and structured data.",
        "",
    ])

    output_path.write_text("\n".join(lines), encoding="utf-8")