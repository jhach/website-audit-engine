def calculate_score(summary: dict) -> dict:

    schema = summary.get("schema", {})
    trust = summary.get("trust_signals", {})
    location = summary.get("location_signals", {})

    # -----------------------
    # On-page SEO
    # -----------------------

    seo_score = 0

    if summary.get("title"):
        seo_score += 5

    if summary.get("meta_description"):
        seo_score += 5

    if summary.get("h1"):
        seo_score += 5

    if summary.get("canonical"):
        seo_score += 5

    if summary.get("word_count", 0) >= 300:
        seo_score += 5

    # -----------------------
    # Local signals
    # -----------------------

    local_score = 0

    if location.get("has_any_broad_term"):
        local_score += 10

    if location.get("has_any_priority_suburb"):
        local_score += 10

    if location.get("has_any_suburb"):
        local_score += 5

    # -----------------------
    # Trust signals
    # -----------------------

    trust_score = 0

    if trust.get("phone_found"):
        trust_score += 5

    if trust.get("email_found"):
        trust_score += 5

    if trust.get("contact_form_found"):
        trust_score += 5

    if trust.get("testimonials_found"):
        trust_score += 5

    if trust.get("address_found"):
        trust_score += 5

    # -----------------------
    # Structured data
    # -----------------------

    schema_score = 0

    if schema.get("schema_found"):
        schema_score += 10

    if schema.get("has_organization"):
        schema_score += 5

    if schema.get("has_breadcrumb"):
        schema_score += 5

    if schema.get("has_local_business"):
        schema_score += 5

    total = seo_score + local_score + trust_score + schema_score

    return {
        "total_score": total,
        "seo_score": seo_score,
        "local_score": local_score,
        "trust_score": trust_score,
        "schema_score": schema_score
    }