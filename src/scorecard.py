def get_grade_band(total_score: int) -> str:
    if total_score >= 90:
        return "A"
    elif total_score >= 75:
        return "B"
    elif total_score >= 60:
        return "C"
    elif total_score >= 40:
        return "D"
    return "F"


def calculate_score(summary: dict) -> dict:
    schema = summary.get("schema", {})
    trust = summary.get("trust_signals", {})
    location = summary.get("location_signals", {})
    lighthouse = summary.get("lighthouse", {})

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
    # On-page SEO (20)
    # -----------------------
    seo_score = 0
    seo_notes = []

    if title:
        seo_score += 3
    else:
        seo_notes.append("Title tag is missing.")

    if 30 <= title_length <= 60:
        seo_score += 3
    else:
        seo_notes.append("Title length could be improved.")

    if meta_description:
        seo_score += 3
    else:
        seo_notes.append("Meta description is missing.")

    if 70 <= meta_length <= 155:
        seo_score += 2
    else:
        seo_notes.append("Meta description length could be improved.")

    if h1:
        seo_score += 3
    else:
        seo_notes.append("Main page heading (H1) is missing.")

    if h1_count == 1:
        seo_score += 2
    else:
        seo_notes.append("Heading structure could be cleaned up.")

    if canonical:
        seo_score += 2
    else:
        seo_notes.append("Canonical tag is missing.")

    if word_count >= 300:
        seo_score += 2
    elif word_count >= 200:
        seo_score += 1
        seo_notes.append("Page copy could be more detailed.")
    else:
        seo_notes.append("Page copy is fairly light.")

    # -----------------------
    # Local relevance (20)
    # -----------------------
    local_score = 0
    local_notes = []

    if location.get("has_any_broad_term"):
        local_score += 5
    else:
        local_notes.append("Broader service area terms were not detected.")

    if location.get("has_any_priority_suburb"):
        local_score += 5
    else:
        local_notes.append("Priority suburb terms were not detected.")

    found_priority_suburbs = location.get("found_priority_suburbs", [])
    if len(found_priority_suburbs) >= 2:
        local_score += 4
    elif len(found_priority_suburbs) == 1:
        local_score += 2
    else:
        local_notes.append("Suburb coverage is limited.")

    if title_has_local_term:
        local_score += 3
    else:
        local_notes.append("No local area was found in the title tag.")

    if h1_has_local_term:
        local_score += 3
    else:
        local_notes.append("No local area was found in the main heading.")

    # -----------------------
    # Trust & conversion (20)
    # -----------------------
    trust_score = 0
    trust_notes = []

    if trust.get("phone_found"):
        trust_score += 3
    else:
        trust_notes.append("A phone number was not clearly detected.")

    if trust.get("email_found"):
        trust_score += 2
    else:
        trust_notes.append("An email address was not clearly detected.")

    if trust.get("address_found"):
        trust_score += 3
    else:
        trust_notes.append("Address or service area signals were not clearly detected.")

    if trust.get("contact_form_found"):
        trust_score += 4
    else:
        trust_notes.append("A contact form was not detected.")

    if trust.get("testimonials_found"):
        trust_score += 4
    else:
        trust_notes.append("Testimonials or review signals were not detected.")

    if trust.get("privacy_policy_found"):
        trust_score += 1
    else:
        trust_notes.append("A privacy policy was not detected.")

    if trust.get("booking_system_detected"):
        trust_score += 3
    else:
        trust_notes.append("A clear booking or enquiry path was not detected.")

    # -----------------------
    # Structured data (15)
    # -----------------------
    schema_score = 0
    schema_notes = []

    if schema.get("schema_found"):
        schema_score += 4
    else:
        schema_notes.append("Structured data was not detected.")

    schema_types = schema.get("schema_types", [])

    if schema.get("has_organization") or "WebSite" in schema_types:
        schema_score += 3
    else:
        schema_notes.append("Organization or WebSite schema could be added.")

    if schema.get("has_breadcrumb"):
        schema_score += 3
    else:
        schema_notes.append("Breadcrumb schema was not detected.")

    if schema.get("has_local_business"):
        schema_score += 5
    else:
        schema_notes.append("LocalBusiness schema was not detected.")

    # -----------------------
    # Performance / UX (25)
    # -----------------------
    ux_notes = []

    perf = lighthouse.get("performance")
    access = lighthouse.get("accessibility")
    best = lighthouse.get("best_practices")
    seo_lh = lighthouse.get("seo")

    # weight performance more heavily
    weighted_scores = []
    if isinstance(perf, int):
        weighted_scores.extend([perf, perf])  # double weight
    if isinstance(access, int):
        weighted_scores.append(access)
    if isinstance(best, int):
        weighted_scores.append(best)
    if isinstance(seo_lh, int):
        weighted_scores.append(seo_lh)

    if weighted_scores:
        weighted_average = sum(weighted_scores) / len(weighted_scores)
        ux_score = round((weighted_average / 100) * 25)
    else:
        ux_score = 0
        ux_notes.append("Performance data was not available.")

    # penalty logic
    lcp_display = lighthouse.get("largest_contentful_paint") or ""
    lcp_penalty = 0

    if isinstance(perf, int):
        if perf < 50:
            lcp_penalty += 4
            ux_notes.append("Page speed is well below recommended levels.")
        elif perf < 70:
            lcp_penalty += 2
            ux_notes.append("Page speed is below recommended levels.")

    # crude but effective LCP penalty using string values like '12.2 s'
    try:
        lcp_seconds = float(str(lcp_display).replace("s", "").strip())
        if lcp_seconds > 6:
            lcp_penalty += 4
            ux_notes.append("Largest Contentful Paint is very high.")
        elif lcp_seconds > 4:
            lcp_penalty += 2
            ux_notes.append("Largest Contentful Paint could be improved.")
    except Exception:
        pass

    ux_score = max(0, min(25, ux_score - lcp_penalty))

    if access is not None and access < 85:
        ux_notes.append("Accessibility could be improved.")
    if best is not None and best < 85:
        ux_notes.append("Technical best practices could be improved.")
    if seo_lh is not None and seo_lh < 90:
        ux_notes.append("Technical SEO signals could be improved.")

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