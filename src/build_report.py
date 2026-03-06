from pathlib import Path


def build_markdown_report(summary: dict, output_path: Path) -> None:
    schema = summary.get("schema", {})

    lines = [
        f"# Website Audit: {summary.get('url', 'Unknown URL')}",
        "",
        "## Homepage Summary",
        "",
        f"- **Title:** {summary.get('title') or 'Missing'}",
        f"- **Meta description:** {summary.get('meta_description') or 'Missing'}",
        f"- **Canonical:** {summary.get('canonical') or 'Missing'}",
        f"- **Robots meta:** {summary.get('robots') or 'Missing'}",
        f"- **H1:** {summary.get('h1') or 'Missing'}",
        f"- **H2 count:** {len(summary.get('h2s', []))}",
        f"- **Estimated word count:** {summary.get('word_count', 0)}",
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
    ]

    if not summary.get("title"):
        lines.append("- Missing page title.")
    if not summary.get("meta_description"):
        lines.append("- Missing meta description.")
    if not summary.get("h1"):
        lines.append("- Missing H1 heading.")
    if not summary.get("canonical"):
        lines.append("- Missing canonical tag.")
    if not schema.get("schema_found"):
        lines.append("- No JSON-LD schema found on the homepage.")
    if schema.get("schema_found") and not schema.get("has_local_business"):
        lines.append("- Schema is present, but LocalBusiness schema is missing.")
    if schema.get("schema_found") and not schema.get("has_breadcrumb"):
        lines.append("- Breadcrumb schema is missing.")

    if (
        summary.get("title")
        and summary.get("meta_description")
        and summary.get("h1")
        and summary.get("canonical")
    ):
        lines.append("- Core homepage SEO elements are present.")

    lines.extend(
        [
            "",
            "## Hatch Studio Opportunity",
            "",
            "This site can likely improve search visibility and AI-readability by tightening core on-page SEO, structured data, and content clarity.",
            "",
        ]
    )

    output_path.write_text("\n".join(lines), encoding="utf-8")