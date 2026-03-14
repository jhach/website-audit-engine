from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def add_footer(canvas, doc):
    canvas.saveState()
    footer_text = "Hatch Studio | hatchstudio.com.au"
    page_number = f"Page {doc.page}"
    canvas.setFont("Helvetica", 9)
    canvas.drawString(40, 20, footer_text)
    canvas.drawRightString(570, 20, page_number)
    canvas.restoreState()


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

    brand_style = ParagraphStyle(
        "BrandStyle",
        parent=styles["BodyText"],
        leading=14,
        spaceAfter=4
    )

    logo_path = Path("assets/hatchstudio-logo.png")
    if logo_path.exists():
        img_width, img_height = ImageReader(str(logo_path)).getSize()
        max_width = 160
        max_height = 60
        scale = min(max_width / img_width, max_height / img_height)
        scaled_width = img_width * scale
        scaled_height = img_height * scale
        story.append(Image(str(logo_path), width=scaled_width, height=scaled_height))
        story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Hatch Studio</b>", styles["Heading2"]))
    story.append(Paragraph("Inner West Web Design & SEO", brand_style))
    story.append(Paragraph("Website: hatchstudio.com.au", brand_style))
    story.append(Paragraph("Email: hello@hatchstudio.com.au", brand_style))
    story.append(Paragraph("Phone: 0400 123 456", brand_style))
    story.append(Spacer(1, 16))

    story.append(Paragraph(f"Website Audit: {summary.get('url', 'Unknown URL')}", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Website Scorecard", styles["Heading2"]))
    story.append(Paragraph(
        f"Total Score: {scorecard.get('total_score', 0)} / 100",
        styles["BodyText"]
    ))
    story.append(Paragraph(
        f"Grade: {grade}",
        styles["BodyText"]
    ))
    story.append(Paragraph(
        f"What this means: {grade_message}",
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

    story.append(Paragraph("Homepage Summary", styles["Heading2"]))
    story.append(Paragraph(f"Title: {summary.get('title') or 'Missing'}", styles["BodyText"]))
    story.append(Paragraph(f"Title length: {summary.get('title_length', 0)}", styles["BodyText"]))
    story.append(Paragraph(f"Meta description: {summary.get('meta_description') or 'Missing'}", styles["BodyText"]))
    story.append(Paragraph(f"Meta description length: {summary.get('meta_description_length', 0)}", styles["BodyText"]))
    story.append(Paragraph(f"Canonical: {summary.get('canonical') or 'Missing'}", styles["BodyText"]))
    story.append(Paragraph(f"Search indexing: {search_indexing}", styles["BodyText"]))
    story.append(Paragraph(f"H1: {summary.get('h1') or 'Missing'}", styles["BodyText"]))
    story.append(Paragraph(f"H1 count: {summary.get('h1_count', 0)}", styles["BodyText"]))
    story.append(Paragraph(f"H2 count: {summary.get('h2_count', 0)}", styles["BodyText"]))
    story.append(Paragraph(f"Estimated word count: {summary.get('word_count', 0)}", styles["BodyText"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Local Signals", styles["Heading2"]))
    found_broad_terms = ", ".join(location_signals.get("found_broad_terms", [])) or "None"
    found_priority_suburbs = ", ".join(location_signals.get("found_priority_suburbs", [])) or "None"
    story.append(Paragraph(f"Found broad terms: {found_broad_terms}", styles["BodyText"]))
    story.append(Paragraph(f"Found priority suburbs: {found_priority_suburbs}", styles["BodyText"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Schema Summary", styles["Heading2"]))
    story.append(Paragraph(f"Schema found: {'Yes' if schema.get('schema_found') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"Schema types: {', '.join(schema.get('schema_types', [])) if schema.get('schema_types') else 'None found'}", styles["BodyText"]))
    story.append(Paragraph(f"Has Organization schema: {'Yes' if schema.get('has_organization') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"Has LocalBusiness schema: {'Yes' if schema.get('has_local_business') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"Has Breadcrumb schema: {'Yes' if schema.get('has_breadcrumb') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"Has FAQ schema: {'Yes' if schema.get('has_faq') else 'No'}", styles["BodyText"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Trust Signals", styles["Heading2"]))
    story.append(Paragraph(f"Phone found: {'Yes' if trust_signals.get('phone_found') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"Email found: {'Yes' if trust_signals.get('email_found') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"Address found: {'Yes' if trust_signals.get('address_found') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"Contact form found: {'Yes' if trust_signals.get('contact_form_found') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"Testimonials found: {'Yes' if trust_signals.get('testimonials_found') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"Privacy policy found: {'Yes' if trust_signals.get('privacy_policy_found') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"Booking system detected: {'Yes' if trust_signals.get('booking_system_detected') else 'No'}", styles["BodyText"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Performance Snapshot", styles["Heading2"]))
    story.append(Paragraph(
        f"Performance: {performance if performance is not None else 'N/A'} / 100",
        styles["BodyText"]
    ))
    story.append(Paragraph(
        _performance_message(performance),
        styles["BodyText"]
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        f"Accessibility: {accessibility if accessibility is not None else 'N/A'} / 100",
        styles["BodyText"]
    ))
    story.append(Paragraph(
        _accessibility_message(accessibility),
        styles["BodyText"]
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        f"Best Practices: {best_practices if best_practices is not None else 'N/A'} / 100",
        styles["BodyText"]
    ))
    story.append(Paragraph(
        _best_practices_message(best_practices),
        styles["BodyText"]
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        f"Technical SEO: {seo_lh if seo_lh is not None else 'N/A'} / 100",
        styles["BodyText"]
    ))
    story.append(Paragraph(
        _seo_message(seo_lh),
        styles["BodyText"]
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        f"Main content load time: {lcp}",
        styles["BodyText"]
    ))
    story.append(Paragraph(
        _lcp_message(lcp),
        styles["BodyText"]
    ))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Opportunity Summary", styles["Heading2"]))

    top_opportunities = opportunity_summary.get("top_opportunities", [])
    potential_impact = opportunity_summary.get("potential_impact", [])

    story.append(Paragraph("Top Opportunities", styles["BodyText"]))
    if top_opportunities:
        for item in top_opportunities:
            story.append(Paragraph(f"• {item}", styles["BodyText"]))
    else:
        story.append(Paragraph("• No major opportunities identified.", styles["BodyText"]))

    story.append(Spacer(1, 8))
    story.append(Paragraph("Potential Impact", styles["BodyText"]))
    if potential_impact:
        for item in potential_impact:
            story.append(Paragraph(f"• {item}", styles["BodyText"]))
    else:
        story.append(Paragraph("• No major impact areas identified.", styles["BodyText"]))

    story.append(Spacer(1, 12))

    story.append(Paragraph("Technical Observations", styles["Heading2"]))
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
    if not location_signals.get("found_broad_terms"):
        notes.append("Broad local area terms were not detected on this page.")
    if not location_signals.get("found_priority_suburbs"):
        notes.append("Priority suburb terms were not detected on this page.")
    if not schema.get("schema_found"):
        notes.append("Structured data was not detected.")
    if schema.get("schema_found") and not schema.get("has_local_business"):
        notes.append("LocalBusiness schema was not detected.")
    if schema.get("schema_found") and not schema.get("has_breadcrumb"):
        notes.append("Breadcrumb schema was not detected.")

    if not notes:
        notes.append("The page has a solid technical base with only minor refinement opportunities.")

    for note in notes:
        story.append(Paragraph(f"• {note}", styles["BodyText"]))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Hatch Studio Notes", styles["Heading2"]))
    story.append(
        Paragraph(
            "From a quick audit, the site has a solid base but there are a few areas that could be tightened to improve search visibility, loading performance, and how clearly the business is understood by Google. Most of these are practical fixes rather than major rebuilds.",
            styles["BodyText"]
        )
    )

    doc.build(
        story,
        onFirstPage=add_footer,
        onLaterPages=add_footer
    )