
import re
from urllib.parse import urlparse


URGENT_PHRASES = [
    "act immediately",
    "urgent action required",
    "account will be suspended",
    "account has been suspended",
    "within 24 hours",
    "immediate action required",
    "unusual activity detected",
]

SENSITIVE_REQUESTS = [
    "password",
    "one-time password",
    "otp",
    "bank details",
    "credit card",
    "login credentials",
    "security code",
]

SUSPICIOUS_PHRASES = [
    "click here immediately",
    "claim your prize",
    "you have won",
    "confirm your identity",
    "update your payment",
    "avoid account closure",
    "gift card",
]


def extract_urls(text):
    """Extract HTTP, HTTPS, and www URLs from text."""
    pattern = r"""https?://[^\s<>"']+|www\.[^\s<>"']+"""
    urls = re.findall(pattern, text, flags=re.IGNORECASE)

    # Remove common punctuation from the ends of extracted URLs.
    return [url.rstrip(".,!?;:)") for url in urls]


def analyze_email(email_text, sender=""):
    """
    Return a heuristic phishing assessment.
    This tool cannot prove that an email is safe or malicious.
    """

    if not isinstance(email_text, str) or not email_text.strip():
        return {
            "status": "Invalid",
            "score": 0,
            "findings": ["Please enter email text."],
            "urls": [],
        }

    text = email_text.lower()
    sender = sender.strip().lower() if isinstance(sender, str) else ""

    findings = []
    score = 0

    # 1. Detect urgent or threatening language.
    matched_urgent = [
        phrase for phrase in URGENT_PHRASES if phrase in text
    ]

    if matched_urgent:
        findings.append(
            "Urgent or threatening language detected: "
            + ", ".join(matched_urgent)
        )
        score += 10 * len(matched_urgent)

    # 2. Detect requests for sensitive information.
    for phrase in SENSITIVE_REQUESTS:
        escaped_phrase = re.escape(phrase)

        request_patterns = [
            rf"\b(?:enter|provide|send|share|submit|confirm|reply with)"
            rf"\b.{{0,40}}\b{escaped_phrase}\b",
            rf"\b{escaped_phrase}\b.{{0,40}}"
            rf"\b(?:enter|provide|send|share|submit|reply with|to us|with us)\b",
        ]

        negative_patterns = [
            rf"\bnever\b.{{0,30}}\b(?:share|send|provide|reveal|disclose)"
            rf"\b.{{0,30}}\b{escaped_phrase}\b",
            rf"\bdo not\b.{{0,30}}\b(?:share|send|provide|reveal|disclose)"
            rf"\b.{{0,30}}\b{escaped_phrase}\b",
            rf"\bdon't\b.{{0,30}}\b(?:share|send|provide|reveal|disclose)"
            rf"\b.{{0,30}}\b{escaped_phrase}\b",
        ]

        is_request = any(
            re.search(pattern, text) for pattern in request_patterns
        )

        is_negative_advice = any(
            re.search(pattern, text) for pattern in negative_patterns
        )

        if is_request and not is_negative_advice:
            findings.append(
                f"Possible request for sensitive information: '{phrase}'"
            )
            score += 12

    # 3. Detect other suspicious phrases.
    matched_suspicious = [
        phrase for phrase in SUSPICIOUS_PHRASES if phrase in text
    ]

    if matched_suspicious:
        findings.append(
            "Potentially suspicious wording: "
            + ", ".join(matched_suspicious)
        )
        score += 10 * len(matched_suspicious)

    # 4. Extract URLs for review.
    urls = extract_urls(email_text)

    if urls:
        findings.append(
            f"Found {len(urls)} URL(s). Review each link before opening it."
        )

    # Keep the risk score between 0 and 100.
    score = min(score, 100)

    # 5. Assign a simple risk category.
    if score >= 60:
        status = "High Risk"
    elif score >= 30:
        status = "Medium Risk"
    elif score > 0:
        status = "Low Risk"
    else:
        status = "No Indicators Found"

    if not findings:
        findings.append(
            "No configured warning indicators were found. "
            "This does not prove the email is safe."
        )

    return {
        "status": status,
        "score": score,
        "findings": findings,
        "urls": urls,
    }
