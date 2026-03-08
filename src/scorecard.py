def get_grade_band(total_score: int) -> str:
    if total_score >= 85:
        return "A"
    elif total_score >= 70:
        return "B"
    elif total_score >= 55:
        return "C"
    elif total_score >= 40:
        return "D"
    return "F"

def calculate_score(summary: dict) -> dict:
    schema = summary.get("schema", {})
    trust = summary.get("trust_signals", {})
    location = summary.get("location_signals", {})

    title = summary.get("title") or ""
    meta_description = summary.get("meta_description") or ""
    h1 = summary.get("h1") or ""
    h1_count = summary.get("h1_count", 0)
    canonical = summary.get("canonical")
    word_count = summary.get("word_count", 0)

    title_length = summary.get("title_length", 0)
    meta_length = summary.get("meta_description_length", 0)

    title_has_local_term = summary.get("title_has_local_term", False)
    h1_has_local_term = summary.get("h1_has_local_term", False)

    # -----------------------
    # On-page SEO (25)
    # -----------------------
    seo_score = 0
    seo_notes = []

    if title:
        seo_score += 3
    else:
        seo_notes.append("Missing title tag.")

    if 30 <= title_length <= 60:
        seo_score += 3
    else:
        seo_notes.append("Title length is not ideal.")

    if meta_description:
        seo_score += 3
    else:
        seo_notes.append("Missing meta description.")

    if 70 <= meta_length <= 155:
        seo_score += 3
    else:
        seo_notes.append("Meta description length is not ideal.")

    if h1:
        seo_score += 4
    else:
        seo_notes.append("Missing H1.")

    if h1_count == 1:
        seo_score += 2
    else:
        seo_notes.append("H1 count is not ideal.")

    if canonical:
        seo_score += 3
    else:
        seo_notes.append("Missing canonical tag.")

    if word_count >= 300:
        seo_score += 4
    elif word_count >= 200:
        seo_score += 2
        seo_notes.append("Page copy is a bit thin.")
    else:
        seo_notes.append("Page copy is thin.")

    # -----------------------
    # Local relevance (20)
    # -----------------------
    local_score = 0
    local_notes = []

    if location.get("has_any_broad_term"):
        local_score += 5
    else:
        local_notes.append("No broad local area terms detected.")

    if location.get("has_any_priority_suburb"):
        local_score += 5
    else:
        local_notes.append("No priority suburb terms detected.")

    found_priority_suburbs = location.get("found_priority_suburbs", [])
    if len(found_priority_suburbs) >= 2:
        local_score += 5
    elif len(found_priority_suburbs) == 1:
        local_score += 3
    else:
        local_notes.append("No meaningful suburb coverage detected.")

    if title_has_local_term:
        local_score += 2
    else:
        local_notes.append("No local term found in title tag.")

    if h1_has_local_term:
        local_score += 3
    else:
        local_notes.append("No local term found in H1.")

    # -----------------------
    # Trust & conversion (25)
    # -----------------------
    trust_score = 0
    trust_notes = []

    if trust.get("phone_found"):
        trust_score += 4
    else:
        trust_notes.append("Phone number not detected.")

    if trust.get("email_found"):
        trust_score += 3
    else:
        trust_notes.append("Email address not detected.")

    if trust.get("address_found"):
        trust_score += 4
    else:
        trust_notes.append("Address or service area signals not detected.")

    if trust.get("contact_form_found"):
        trust_score += 4
    else:
        trust_notes.append("Contact form not detected.")

    if trust.get("testimonials_found"):
        trust_score += 4
    else:
        trust_notes.append("Testimonials or reviews not detected.")

    if trust.get("privacy_policy_found"):
        trust_score += 2
    else:
        trust_notes.append("Privacy policy not detected.")

    if trust.get("booking_system_detected"):
        trust_score += 4
    else:
        trust_notes.append("Booking or enquiry CTA not detected.")

    # -----------------------
    # Structured data (15)
    # -----------------------
    schema_score = 0
    schema_notes = []

    if schema.get("schema_found"):
        schema_score += 4
    else:
        schema_notes.append("No schema detected.")

    schema_types = schema.get("schema_types", [])

    if schema.get("has_organization") or "WebSite" in schema_types:
        schema_score += 3
    else:
        schema_notes.append("No Organization/WebSite schema detected.")

    if schema.get("has_breadcrumb"):
        schema_score += 3
    else:
        schema_notes.append("No Breadcrumb schema detected.")

    if schema.get("has_local_business"):
        schema_score += 5
    else:
        schema_notes.append("No LocalBusiness schema detected.")

    # -----------------------
    # UX / presentation baseline (15)
    # -----------------------
    ux_score = 0
    ux_notes = []

    if summary.get("h2_count", 0) >= 2:
        ux_score += 3
    else:
        ux_notes.append("Low heading structure depth.")

    if summary.get("desktop_screenshot"):
        ux_score += 1

    if summary.get("mobile_screenshot"):
        ux_score += 1

    if trust.get("contact_form_found") or trust.get("booking_system_detected"):
        ux_score += 4
    else:
        ux_notes.append("Weak conversion path.")

    if trust.get("testimonials_found"):
        ux_score += 3
    else:
        ux_notes.append("Weak visible trust proof.")

    if h1_count == 1:
        ux_score += 3
    else:
        ux_notes.append("Heading hierarchy may be messy.")

    total = seo_score + local_score + trust_score + schema_score + ux_score

    grade_band = get_grade_band(total)

    return {
        "total_score": total,
        "grade_band": grade_band,
        "seo_score": seo_score,
        "local_score": local_score,
        "trust_score": trust_score,
        "schema_score": schema_score,
        "ux_score": ux_score,
        "score_breakdown": {
            "seo_notes": seo_notes,
            "local_notes": local_notes,
            "trust_notes": trust_notes,
            "schema_notes": schema_notes,
            "ux_notes": ux_notes
        }
    }