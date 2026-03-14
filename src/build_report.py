from pathlib import Path


def _performance_message(score):
    if score is None:
        return "Performance data was not available."
    if score >= 90:
        return "The site is performing strongly and loading at a healthy speed."
    if score >= 70:
        return "The site is in decent shape, but there is still room to improve speed and responsiveness."
    if score >= 50:
        return "The site is loading slower than recommended, especially on mobile."
    return "The site is performing poorly and may be losing visitors before the page fully loads."


def _accessibility_message(score):
    if score is None:
        return "Accessibility data was not available."
    if score >= 90:
        return "Accessibility is in a strong place overall."
    if score >= 75:
        return "Accessibility is decent, with a few areas that could be improved."
    return "Accessibility needs attention to make the site easier to use for more visitors."


def _best_practices_message(score):
    if score is None:
        return "Best practices data was not available."
    if score >= 90:
        return "The site follows technical best practices well overall."
    if score >= 75:
        return "The site is in decent shape technically, with a few worthwhile improvements available."
    return "There are technical issues worth cleaning up to strengthen the site."


def _seo_message(score):
    if score is None:
        return "Technical SEO data was not available."
    if score >= 90:
        return "The site has a solid technical SEO base."
    if score >= 75:
        return "The technical SEO base is decent, with a few worthwhile improvements available."
    return "Technical SEO needs work to make the site easier for search engines to understand."


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


def _search_indexing_message(robots_value):
    if not robots_value:
        return "No robots meta tag was detected."
    robots_lower = robots_value.lower()
    if "noindex" in robots_lower:
        return "Search engines may be blocked from indexing this page."
    return "Search engines appear to be allowed to index this page."


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
        "C": "There are a few clear gaps that could be holding the site back.",
        "D": "The site has some weaker foundations that are likely limiting visibility and conversions.",
        "F": "There are significant issues that are likely affecting performance, visibility, and trust."
    }.get(grade, "No grade interpretation available.")

    performance = lighthouse.get("performance")
    accessibility = lighthouse.get("accessibility")
    best_practices = lighthouse.get("best_practices")
    seo_lh = lighthouse.get("seo")
    lcp = lighthouse.get("largest_contentful_paint", "N/A")

    robots_value = summary.get("robots")
    search_indexing = _search_indexing_message(robots_value)

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
        f"- **Search indexing:** {search_indexing}",
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
        "## Technical Observations",
        ""
    ])

    notes = []

    if not summary.get("title"):
        notes.append("Title tag is missing.")
    if summary.get("title_length", 0) > 60:
        notes.append("Title length could be improved for search results.")
    if not summary.get("meta_description"):
        notes.append("Meta description is missing.")
    if summary.get("meta_description_length", 0) > 155:
        notes.append("Meta description is longer than ideal and may truncate in search.")
    if not summary.get("h1"):
        notes.append("Main page heading (H1) is missing.")
    if summary.get("h1_count", 0) > 1:
        notes.append("Heading structure could be cleaned up.")
    if not summary.get("canonical"):
        notes.append("Canonical tag is missing.")
    if not found_broad_terms:
        notes.append("Broad local area terms were not detected on this page.")
    if not found_priority_suburbs:
        notes.append("Priority suburb terms were not detected on this page.")
    if not schema.get("schema_found"):
        notes.append("Structured data was not detected.")
    if schema.get("schema_found") and not schema.get("has_local_business"):
        notes.append("LocalBusiness schema was not detected.")
    if schema.get("schema_found") and not schema.get("has_breadcrumb"):
        notes.append("Breadcrumb schema was not detected.")

    if notes:
        for note in notes:
            lines.append(f"- {note}")
    else:
        lines.append("- The page has a solid technical base with only minor refinement opportunities.")

    lines.extend([
        "",
        "## Hatch Studio Notes",
        "",
        "From a quick audit, the site has a solid base but there are a few areas that could be tightened to improve search visibility, loading performance, and how clearly the business is understood by Google. Most of these are practical fixes rather than major rebuilds.",
        ""
    ])

    output_path.write_text("\n".join(lines), encoding="utf-8")