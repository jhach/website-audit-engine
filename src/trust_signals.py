import re
from pathlib import Path
from bs4 import BeautifulSoup


def detect_trust_signals(html_path: Path) -> dict:

    html = html_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "lxml")

    text = html.lower()

    phone_pattern = r'(\+?\d[\d\-\s]{7,}\d)'
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'

    phone_found = bool(re.search(phone_pattern, html))
    email_found = bool(re.search(email_pattern, html))

    address_keywords = [
        "street",
        "st ",
        "road",
        "rd ",
        "ave",
        "avenue",
        "sydney",
        "nsw",
        "postcode"
    ]

    address_found = any(keyword in text for keyword in address_keywords)

    form_found = bool(soup.find("form"))

    testimonial_keywords = [
        "testimonial",
        "review",
        "what our customers say",
        "client feedback"
    ]

    testimonial_found = any(keyword in text for keyword in testimonial_keywords)

    privacy_found = "privacy policy" in text

    about_found = "about" in text

    booking_keywords = [
        "book now",
        "book online",
        "schedule",
        "appointment",
        "quote"
    ]

    booking_found = any(keyword in text for keyword in booking_keywords)

    return {
        "phone_found": phone_found,
        "email_found": email_found,
        "address_found": address_found,
        "contact_form_found": form_found,
        "testimonials_found": testimonial_found,
        "privacy_policy_found": privacy_found,
        "about_page_reference": about_found,
        "booking_system_detected": booking_found
    }