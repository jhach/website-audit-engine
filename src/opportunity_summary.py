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
        opportunities.append("LocalBusiness schema is missing, which weakens local search and Google Business relevance.")

    if not location.get("title_has_local_term") or not location.get("h1_has_local_term"):
        opportunities.append("Local area targeting is weak in key page elements like the title tag or H1.")

    if meta_length > 155:
        opportunities.append("The meta description is too long and may truncate in search results.")

    if not trust.get("testimonials_found"):
        opportunities.append("No testimonials or review signals were detected, which weakens trust and conversion.")

    if not trust.get("contact_form_found") and not trust.get("booking_system_detected"):
        opportunities.append("The page lacks a strong enquiry or booking path, which can reduce conversions.")

    perf = lighthouse.get("performance")
    if perf is not None and perf < 70:
        opportunities.append("Performance is below recommended levels, especially for mobile users.")

    if scorecard.get("schema_score", 0) <= 8:
        impact.append("Improving structured data can help search engines and AI systems understand the business more clearly.")

    if scorecard.get("local_score", 0) <= 12:
        impact.append("Stronger suburb and service area targeting can improve local visibility and relevance.")

    if scorecard.get("trust_score", 0) <= 12:
        impact.append("Improving trust signals can help turn more visitors into enquiries.")

    if scorecard.get("ux_score", 0) <= 15:
        impact.append("Improving performance and usability can help reduce drop-off and improve engagement.")

    if not impact:
        impact.append("This site has a solid base, but refining visibility, local relevance, and structured data could still improve results.")

    return {
        "top_opportunities": opportunities[:5],
        "potential_impact": impact[:4]
    }