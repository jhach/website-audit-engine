from pathlib import Path


def _performance_message(score):
    if score is None:
        return "Performance data was not available."
    if score >= 90:
        return "The site is performing strongly and loading at a healthy speed."
    if score >= 70:
        return "The site is reasonably healthy, but there is room to improve speed and responsiveness."
    if score >= 50:
        return "The site is loading slower than recommended, especially for mobile visitors."
    return "The site is performing poorly and may be losing visitors before the page fully loads."


def _accessibility_message(score):
    if score is None:
        return "Accessibility data was not available."
    if score >= 90:
        return "Accessibility is in a strong place overall."
    if score >= 75:
        return "Accessibility is decent, with some areas that could be improved."
    return "Accessibility needs attention to make the site easier to use for all visitors."


def _best_practices_message(score):
    if score is None:
        return "Best practices data was not available."
    if score >= 90:
        return "The site follows technical best practices well overall."
    if score >= 75:
        return "The site is in decent shape technically, but there are a few improvements worth making."
    return "There are technical issues that should be cleaned up to strengthen the site."


def _seo_message(score):
    if score is None:
        return "Technical SEO data was not available."
    if score >= 90:
        return "The site has a solid technical SEO base."
    if score >= 75:
        return "The technical SEO base is decent, with some worthwhile improvements available."
    return "Technical SEO needs work to improve how clearly the site is understood by search engines."


def _lcp_message(lcp_value):
    try:
        seconds = float(str(lcp_value).replace("s", "").strip())
    except Exception:
        return "This measures how quickly the main visible content appears."

    if seconds <= 2.5:
        return "The main content is loading within a healthy range."
    if seconds <= 4:
        return "The main content is a little slower than ideal."
    if seconds <= 6:
        return "The main content is loading slower than recommended and may affect user experience."
    return "The main content is taking too long to appear, which can hurt both engagement and conversions."


def build_markdown_report(summary: dict, output_path: Path) -> None:
    schema = summary.get("schema", {})
    location_signals = summary.get("location_signals", {})
    trust_signals = summary.get("trust_signals", {})
    scorecard = summary.get("scorecard", {})
    lighthouse = summary.get("lighthouse", {})
    opportunity_summary = summary.get("opportunity_summary", {})

    broad_mentions = location_signals.get("broad_mentions", {})
    priority_suburb_mentions = location_signals.get("priority_suburb_mentions", {})
    found_broad_terms = location_signals.get("found_broad_terms", [])
    found_priority_suburbs = location_signals.get("found_priority_suburbs", [])
    missing_broad_terms = location_signals.get("missing_broad_terms", [])
    missing_priority_suburbs = location_signals.get("missing_priority_suburbs", [])

    grade = scorecard.get("grade_band", "N/A")
    grade_message = {
        "A": "Strong foundation with a few refinement opportunities.",
        "B": "Good base with some worthwhile improvement areas.",
        "C": "Underperforming in several areas that could be improved.",
        "D": "Weak foundations are likely holding the site back.",
        "F": "Significant issues are likely affecting visibility and conversions."
    }.get(grade, "No grade interpretation available.")

    performance = lighthouse.get("performance")
    accessibility = lighthouse.get("accessibility")
    best_practices = lighthouse.get("best_practices")
    seo_lh = lighthouse.get("seo")
    lcp = lighthouse.get("largest_contentful_paint", "N/A")

    top_opportunities = opportunity_summary.get("top_opportunities", [])
    potential_impact = opportunity_summary.get("potential_impact", [])

    lines = [
        f"# Website Audit: {summary.get('url', 'Unknown URL')}",
        "",
        "## Website Scorecard",
        "",
        f"- **Total Score:** {scorecard.get('total_score', 0)} / 100",
        f"- **Grade:** {grade}",
        f"- **What this means:** {grade_message}",
        f"- **On-Page SEO:** {scorecard.get('seo_score', 0)} / 20",
        f"- **Local Signals:** {scorecard.get('local_score', 0)} / 20",
        f"- **Trust & Conversion:** {scorecard.get('trust_score', 0)} / 20",
        f"- **Structured Data:** {scorecard.get('schema_score', 0)} / 15",
        f"- **Performance / UX:** {scorecard.get('ux_score', 0)} / 25",
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
        "### Broad Terms",
        ""
    ]

    for term, count in broad_mentions.items():
        lines.append(f"- **{term}:** {count} mention(s)")

    lines.extend([
        "",
        f"- **Found broad terms:** {', '.join(found_broad_terms) if found_broad_terms else 'None'}",
        f"- **Missing broad terms:** {', '.join(missing_broad_terms) if missing_broad_terms else 'None'}",
        "",
        "### Priority Suburbs",
        ""
    ])

    for term, count in priority_suburb_mentions.items():
        if count > 0:
            lines.append(f"- **{term}:** {count} mention(s)")

    lines.extend([
        "",
        f"- **Found priority suburbs:** {', '.join(found_priority_suburbs) if found_priority_suburbs else 'None'}",
        f"- **Missing priority suburbs:** {', '.join(missing_priority_suburbs) if missing_priority_suburbs else 'None'}",
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
        "## Trust Signals",
        "",
        f"- **Phone found:** {'Yes' if trust_signals.get('phone_found') else 'No'}",
        f"- **Email found:** {'Yes' if trust_signals.get('email_found') else 'No'}",
        f"- **Address found:** {'Yes' if trust_signals.get('address_found') else 'No'}",
        f"- **Contact form found:** {'Yes' if trust_signals.get('contact_form_found') else 'No'}",
        f"- **Testimonials found:** {'Yes' if trust_signals.get('testimonials_found') else 'No'}",
        f"- **Privacy policy found:** {'Yes' if trust_signals.get('privacy_policy_found') else 'No'}",
        f"- **Booking system detected:** {'Yes' if trust_signals.get('booking_system_detected') else 'No'}",
        "",
        "## Performance Snapshot",
        "",
        f"- **Performance:** {performance if performance is not None else 'N/A'} / 100",
        f"  - {_performance_message(performance)}",
        f"- **Accessibility:** {accessibility if accessibility is not None else 'N/A'} / 100",
        f"  - {_accessibility_message(accessibility)}",
        f"- **Best Practices:** {best_practices if best_practices is not None else 'N/A'} / 100",
        f"  - {_best_practices_message(best_practices)}",
        f"- **Technical SEO:** {seo_lh if seo_lh is not None else 'N/A'} / 100",
        f"  - {_seo_message(seo_lh)}",
        f"- **Main content load time:** {lcp}",
        f"  - {_lcp_message(lcp)}",
        "",
        "## Opportunity Summary",
        "",
        "### Top Opportunities",
        ""
    ])

    if top_opportunities:
        for item in top_opportunities:
            lines.append(f"- {item}")
    else:
        lines.append("- No major opportunities identified.")

    lines.extend([
        "",
        "### Potential Impact",
        ""
    ])

    if potential_impact:
        for item in potential_impact:
            lines.append(f"- {item}")
    else:
        lines.append("- No major impact areas identified.")

    lines.extend([
        "",
        "## Initial Notes",
        ""
    ])

    if not summary.get("title"):
        lines.append("- Title tag is missing.")
    if summary.get("title_length", 0) > 60:
        lines.append("- Title length could be improved for search results.")
    if not summary.get("meta_description"):
        lines.append("- Meta description is missing.")
    if summary.get("meta_description_length", 0) > 155:
        lines.append("- Meta description is longer than ideal and may truncate in search.")
    if not summary.get("h1"):
        lines.append("- Main page heading (H1) is missing.")
    if summary.get("h1_count", 0) > 1:
        lines.append("- Heading structure could be cleaned up.")
    if not summary.get("canonical"):
        lines.append("- Canonical tag is missing.")
    if not found_broad_terms:
        lines.append("- Broad local area terms were not detected on this page.")
    if not found_priority_suburbs:
        lines.append("- Priority suburb terms were not detected on this page.")
    if not schema.get("schema_found"):
        lines.append("- Structured data was not detected.")
    if schema.get("schema_found") and not schema.get("has_local_business"):
        lines.append("- LocalBusiness schema was not detected.")
    if schema.get("schema_found") and not schema.get("has_breadcrumb"):
        lines.append("- Breadcrumb schema was not detected.")

    if not (
        not summary.get("title")
        or summary.get("title_length", 0) > 60
        or not summary.get("meta_description")
        or summary.get("meta_description_length", 0) > 155
        or not summary.get("h1")
        or summary.get("h1_count", 0) > 1
        or not summary.get("canonical")
        or not found_broad_terms
        or not found_priority_suburbs
        or not schema.get("schema_found")
        or (schema.get("schema_found") and not schema.get("has_local_business"))
        or (schema.get("schema_found") and not schema.get("has_breadcrumb"))
    ):
        lines.append("- The page has a solid technical base with only minor refinement opportunities.")

    lines.extend([
        "",
        "## Summary",
        "",
        "Overall, the site has a solid base, but there are a few practical improvements that could strengthen local visibility, improve performance, and make it easier for visitors to turn into enquiries.",
        ""
    ])

    output_path.write_text("\n".join(lines), encoding="utf-8")