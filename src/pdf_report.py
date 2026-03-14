from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.utils import ImageReader


def build_pdf_report(summary: dict, output_path: Path) -> None:
    doc = SimpleDocTemplate(str(output_path), pagesize=LETTER)
    styles = getSampleStyleSheet()
    story = []

    schema = summary.get("schema", {})
    location_signals = summary.get("location_signals", {})
    trust_signals = summary.get("trust_signals", {})
    scorecard = summary.get("scorecard", {})
    lighthouse = summary.get("lighthouse", {})
    opportunity_summary = summary.get("opportunity_summary", {})

    # Title
    story.append(Paragraph(f"Website Audit: {summary.get('url', 'Unknown URL')}", styles["Title"]))
    story.append(Spacer(1, 12))

    # Scorecard
    story.append(Paragraph("Website Scorecard", styles["Heading2"]))
    story.append(Paragraph(
        f"<b>Total Score:</b> {scorecard.get('total_score', 0)} / 100",
        styles["BodyText"]
    ))
    story.append(Paragraph(
        f"<b>Grade:</b> {scorecard.get('grade_band', 'N/A')}",
        styles["BodyText"]
    ))
    story.append(Paragraph(
        f"On-Page SEO: {scorecard.get('seo_score', 0)} / 20",
        styles["BodyText"]
    ))
    story.append(Paragraph(
        f"Local Signals: {scorecard.get('local_score', 0)} / 20",
        styles["BodyText"]
    ))
    story.append(Paragraph(
        f"Trust & Conversion: {scorecard.get('trust_score', 0)} / 20",
        styles["BodyText"]
    ))
    story.append(Paragraph(
        f"Structured Data: {scorecard.get('schema_score', 0)} / 15",
        styles["BodyText"]
    ))
    story.append(Paragraph(
        f"Performance / UX: {scorecard.get('ux_score', 0)} / 25",
        styles["BodyText"]
    ))
    story.append(Spacer(1, 16))

    # Homepage screenshot
    screenshot_path = summary.get("desktop_screenshot")
    if screenshot_path:
        screenshot_file = Path(screenshot_path)
        if screenshot_file.exists():
            story.append(Paragraph("Homepage Screenshot", styles["Heading2"]))
            story.append(Spacer(1, 6))

            img_width, img_height = ImageReader(str(screenshot_file)).getSize()

            max_width = 450
            max_height = 300

            scale = min(max_width / img_width, max_height / img_height)
            scaled_width = img_width * scale
            scaled_height = img_height * scale

            story.append(Image(str(screenshot_file), width=scaled_width, height=scaled_height))
            story.append(Spacer(1, 16))

    # Homepage summary
    story.append(Paragraph("Homepage Summary", styles["Heading2"]))
    story.append(Paragraph(f"<b>Title:</b> {summary.get('title') or 'Missing'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Title length:</b> {summary.get('title_length', 0)}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Meta description:</b> {summary.get('meta_description') or 'Missing'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Meta description length:</b> {summary.get('meta_description_length', 0)}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Canonical:</b> {summary.get('canonical') or 'Missing'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Robots meta:</b> {summary.get('robots') or 'Missing'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>H1:</b> {summary.get('h1') or 'Missing'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>H1 count:</b> {summary.get('h1_count', 0)}", styles["BodyText"]))
    story.append(Paragraph(f"<b>H2 count:</b> {summary.get('h2_count', 0)}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Estimated word count:</b> {summary.get('word_count', 0)}", styles["BodyText"]))
    story.append(Spacer(1, 12))

    # Local signals
    story.append(Paragraph("Local Signals", styles["Heading2"]))
    found_broad_terms = ", ".join(location_signals.get("found_broad_terms", [])) or "None"
    found_priority_suburbs = ", ".join(location_signals.get("found_priority_suburbs", [])) or "None"
    story.append(Paragraph(f"<b>Found broad terms:</b> {found_broad_terms}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Found priority suburbs:</b> {found_priority_suburbs}", styles["BodyText"]))
    story.append(Spacer(1, 12))

    # Schema summary
    story.append(Paragraph("Schema Summary", styles["Heading2"]))
    story.append(Paragraph(f"<b>Schema found:</b> {'Yes' if schema.get('schema_found') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Schema types:</b> {', '.join(schema.get('schema_types', [])) if schema.get('schema_types') else 'None found'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Has Organization schema:</b> {'Yes' if schema.get('has_organization') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Has LocalBusiness schema:</b> {'Yes' if schema.get('has_local_business') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Has Breadcrumb schema:</b> {'Yes' if schema.get('has_breadcrumb') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Has FAQ schema:</b> {'Yes' if schema.get('has_faq') else 'No'}", styles["BodyText"]))
    story.append(Spacer(1, 12))

    # Trust signals
    story.append(Paragraph("Trust Signals", styles["Heading2"]))
    story.append(Paragraph(f"<b>Phone found:</b> {'Yes' if trust_signals.get('phone_found') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Email found:</b> {'Yes' if trust_signals.get('email_found') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Address found:</b> {'Yes' if trust_signals.get('address_found') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Contact form found:</b> {'Yes' if trust_signals.get('contact_form_found') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Testimonials found:</b> {'Yes' if trust_signals.get('testimonials_found') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Privacy policy found:</b> {'Yes' if trust_signals.get('privacy_policy_found') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Booking system detected:</b> {'Yes' if trust_signals.get('booking_system_detected') else 'No'}", styles["BodyText"]))
    story.append(Spacer(1, 12))

    # Lighthouse summary
    story.append(Paragraph("Lighthouse Summary", styles["Heading2"]))
    story.append(Paragraph(
        f"<b>Performance:</b> {lighthouse.get('performance', 'N/A')}",
        styles["BodyText"]
    ))
    story.append(Paragraph(
        f"<b>Accessibility:</b> {lighthouse.get('accessibility', 'N/A')}",
        styles["BodyText"]
    ))
    story.append(Paragraph(
        f"<b>Best Practices:</b> {lighthouse.get('best_practices', 'N/A')}",
        styles["BodyText"]
    ))
    story.append(Paragraph(
        f"<b>SEO:</b> {lighthouse.get('seo', 'N/A')}",
        styles["BodyText"]
    ))
    story.append(Paragraph(
        f"<b>LCP:</b> {lighthouse.get('largest_contentful_paint', 'N/A')}",
        styles["BodyText"]
    ))
    story.append(Paragraph(
        f"<b>CLS:</b> {lighthouse.get('cumulative_layout_shift', 'N/A')}",
        styles["BodyText"]
    ))
    story.append(Paragraph(
        f"<b>Speed Index:</b> {lighthouse.get('speed_index', 'N/A')}",
        styles["BodyText"]
    ))
    story.append(Paragraph(
        f"<b>Total Blocking Time:</b> {lighthouse.get('total_blocking_time', 'N/A')}",
        styles["BodyText"]
    ))
    story.append(Spacer(1, 12))

    # Opportunity summary
    story.append(Paragraph("Opportunity Summary", styles["Heading2"]))

    top_opportunities = opportunity_summary.get("top_opportunities", [])
    potential_impact = opportunity_summary.get("potential_impact", [])

    story.append(Paragraph("<b>Top Opportunities</b>", styles["BodyText"]))
    if top_opportunities:
        for item in top_opportunities:
            story.append(Paragraph(f"• {item}", styles["BodyText"]))
    else:
        story.append(Paragraph("• No major opportunities identified.", styles["BodyText"]))

    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Potential Impact</b>", styles["BodyText"]))
    if potential_impact:
        for item in potential_impact:
            story.append(Paragraph(f"• {item}", styles["BodyText"]))
    else:
        story.append(Paragraph("• No major impact areas identified.", styles["BodyText"]))

    story.append(Spacer(1, 12))

    # Initial notes
    story.append(Paragraph("Initial Notes", styles["Heading2"]))
    notes = []

    if not summary.get("title"):
        notes.append("Missing page title.")
    if summary.get("title_length", 0) > 60:
        notes.append("Title may be too long for search results.")
    if not summary.get("meta_description"):
        notes.append("Missing meta description.")
    if summary.get("meta_description_length", 0) > 155:
        notes.append("Meta description may be too long for search snippets.")
    if not summary.get("h1"):
        notes.append("Missing H1 heading.")
    if summary.get("h1_count", 0) > 1:
        notes.append("Multiple H1 tags detected.")
    if not summary.get("canonical"):
        notes.append("Missing canonical tag.")
    if not location_signals.get("found_broad_terms"):
        notes.append("No broad local area terms were detected on this page.")
    if not location_signals.get("found_priority_suburbs"):
        notes.append("No priority suburb terms were detected on this page.")
    if not schema.get("schema_found"):
        notes.append("No JSON-LD schema found on the page.")
    if schema.get("schema_found") and not schema.get("has_local_business"):
        notes.append("Schema is present, but LocalBusiness schema is missing.")
    if schema.get("schema_found") and not schema.get("has_breadcrumb"):
        notes.append("Breadcrumb schema is missing.")

    if not notes:
        notes.append("Core homepage SEO and structured data signals look solid.")

    for note in notes:
        story.append(Paragraph(f"• {note}", styles["BodyText"]))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Hatch Studio Opportunity", styles["Heading2"]))
    story.append(
        Paragraph(
            "This site can likely improve search visibility, local relevance, and AI-readability by tightening on-page SEO, suburb targeting, trust signals, and structured data.",
            styles["BodyText"]
        )
    )

    doc.build(story)