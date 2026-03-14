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

    # left footer
    canvas.drawString(40, 20, footer_text)

    # right footer
    canvas.drawRightString(570, 20, page_number)

    canvas.restoreState()
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
        "C": "Underperforming in several areas that could be improved.",
        "D": "Weak foundations are likely holding the site back.",
        "F": "Significant issues are likely affecting visibility and conversions."
    }.get(grade, "No grade interpretation available.")

    # -----------------------------
    # Hatch Studio branding/header
    # -----------------------------
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
    story.append(Paragraph("hatchstudio.com.au", brand_style))
    story.append(Paragraph("james@hatchstudio.com.au", brand_style))
    story.append(Paragraph("0408 076 901", brand_style))
    story.append(Spacer(1, 16))

    # -----------------------------
    # Audit title
    # -----------------------------
    story.append(Paragraph(f"Website Audit: {summary.get('url', 'Unknown URL')}", styles["Title"]))
    story.append(Spacer(1, 12))

    # -----------------------------
    # Scorecard
    # -----------------------------
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

    # -----------------------------
    # Homepage screenshot
    # -----------------------------
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

    # -----------------------------
    # Homepage summary
    # -----------------------------
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

    # -----------------------------
    # Local signals
    # -----------------------------
    story.append(Paragraph("Local Signals", styles["Heading2"]))
    found_broad_terms = ", ".join(location_signals.get("found_broad_terms", [])) or "None"
    found_priority_suburbs = ", ".join(location_signals.get("found_priority_suburbs", [])) or "None"
    story.append(Paragraph(f"<b>Found broad terms:</b> {found_broad_terms}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Found priority suburbs:</b> {found_priority_suburbs}", styles["BodyText"]))
    story.append(Spacer(1, 12))

    # -----------------------------
    # Schema summary
    # -----------------------------
    story.append(Paragraph("Schema Summary", styles["Heading2"]))
    story.append(Paragraph(f"<b>Schema found:</b> {'Yes' if schema.get('schema_found') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Schema types:</b> {', '.join(schema.get('schema_types', [])) if schema.get('schema_types') else 'None found'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Has Organization schema:</b> {'Yes' if schema.get('has_organization') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Has LocalBusiness schema:</b> {'Yes' if schema.get('has_local_business') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Has Breadcrumb schema:</b> {'Yes' if schema.get('has_breadcrumb') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Has FAQ schema:</b> {'Yes' if schema.get('has_faq') else 'No'}", styles["BodyText"]))
    story.append(Spacer(1, 12))

    # -----------------------------
    # Trust signals
    # -----------------------------
    story.append(Paragraph("Trust Signals", styles["Heading2"]))
    story.append(Paragraph(f"<b>Phone found:</b> {'Yes' if trust_signals.get('phone_found') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Email found:</b> {'Yes' if trust_signals.get('email_found') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Address found:</b> {'Yes' if trust_signals.get('address_found') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Contact form found:</b> {'Yes' if trust_signals.get('contact_form_found') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Testimonials found:</b> {'Yes' if trust_signals.get('testimonials_found') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Privacy policy found:</b> {'Yes' if trust_signals.get('privacy_policy_found') else 'No'}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Booking system detected:</b> {'Yes' if trust_signals.get('booking_system_detected') else 'No'}", styles["BodyText"]))
    story.append(Spacer(1, 12))

    # -----------------------------
    # Performance snapshot
    # -----------------------------
    story.append(Paragraph("Performance Snapshot", styles["Heading2"]))

    performance = lighthouse.get("performance")
    accessibility = lighthouse.get("accessibility")
    best_practices = lighthouse.get("best_practices")
    seo_lh = lighthouse.get("seo")
    lcp = lighthouse.get("largest_contentful_paint", "N/A")

    story.append(Paragraph(
        f"<b>Performance:</b> {performance if performance is not None else 'N/A'} / 100",
        styles["BodyText"]
    ))
    story.append(Paragraph(
        _performance_message(performance),
        styles["BodyText"]
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        f"<b>Accessibility:</b> {accessibility if accessibility is not None else 'N/A'} / 100",
        styles["BodyText"]
    ))
    story.append(Paragraph(
        _accessibility_message(accessibility),
        styles["BodyText"]
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        f"<b>Best Practices:</b> {best_practices if best_practices is not None else 'N/A'} / 100",
        styles["BodyText"]
    ))
    story.append(Paragraph(
        _best_practices_message(best_practices),
        styles["BodyText"]
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        f"<b>Technical SEO:</b> {seo_lh if seo_lh is not None else 'N/A'} / 100",
        styles["BodyText"]
    ))
    story.append(Paragraph(
        _seo_message(seo_lh),
        styles["BodyText"]
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        f"<b>Main content load time:</b> {lcp}",
        styles["BodyText"]
    ))
    story.append(Paragraph(
        _lcp_message(lcp),
        styles["BodyText"]
    ))
    story.append(Spacer(1, 12))

    # -----------------------------
    # Opportunity summary
    # -----------------------------
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

    # -----------------------------
    # Initial notes
    # -----------------------------
    story.append(Paragraph("Initial Notes", styles["Heading2"]))
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
    story.append(Paragraph("Summary", styles["Heading2"]))
    story.append(
        Paragraph(
            "Overall, the site has a solid base, but there are a few practical improvements that could strengthen local visibility, improve performance, and make it easier for visitors to turn into enquiries.",
            styles["BodyText"]
        )
    )

    doc.build(
    story,
    onFirstPage=add_footer,
    onLaterPages=add_footer
)