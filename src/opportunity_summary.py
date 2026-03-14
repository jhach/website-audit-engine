def build_opportunity_summary(summary: dict) -> dict:
    opportunities = []
    impact = []

    schema = summary.get("schema", {})
    trust = summary.get("trust_signals", {})
    location = summary.get("location_signals", {})
    lighthouse = summary.get("lighthouse", {})
    scorecard = summary.get("scorecard", {})
    meta_length = summary.get("meta_description_length", 0)

    if not schema.get("has_local_business"):
        opportunities.append("Add LocalBusiness schema so Google and AI tools can better understand the business and its location.")

    if not location.get("title_has_local_term") or not location.get("h1_has_local_term"):
        opportunities.append("Strengthen local targeting in the page title and main heading so the service area is clearer.")

    if meta_length > 155:
        opportunities.append("Tighten the meta description so it displays more cleanly in search results.")

    if not trust.get("testimonials_found"):
        opportunities.append("Add stronger trust signals such as testimonials or reviews to help turn more visitors into enquiries.")

    if not trust.get("contact_form_found") and not trust.get("booking_system_detected"):
        opportunities.append("Create a clearer enquiry path so visitors know exactly what to do next.")

    perf = lighthouse.get("performance")
    if perf is not None and perf < 70:
        opportunities.append("Improve page speed, especially on mobile, to reduce drop-off and create a better first impression.")

    if scorecard.get("schema_score", 0) <= 8:
        impact.append("Clearer structured data can improve how the business appears in search and how easily it is understood by AI tools.")

    if scorecard.get("local_score", 0) <= 12:
        impact.append("Stronger suburb and service area targeting can improve local relevance and search visibility.")

    if scorecard.get("trust_score", 0) <= 12:
        impact.append("Improving trust signals can help more visitors feel confident getting in touch.")

    if scorecard.get("ux_score", 0) <= 15:
        impact.append("Improving speed and usability can help reduce friction and support better enquiry conversion.")

    if not impact:
        impact.append("The site has a solid base, but refining visibility, speed, and local targeting could still lift performance.")

    return {
        "top_opportunities": opportunities[:5],
        "potential_impact": impact[:4]
    }