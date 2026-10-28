
import os
import re
import ipaddress
import requests

from urllib.parse import urlparse, unquote
from dotenv import load_dotenv

load_dotenv()

from urllib.parse import urlparse, unquote
import ipaddress
import re
from difflib import SequenceMatcher


SUSPICIOUS_KEYWORDS = {
    "login": 10,
    "verify": 10,
    "password": 15,
    "account": 5,
    "banking": 10,
    "credential": 15,
    "reset": 8,
    "wallet": 8,
}

# Demonstration list for lookalike checks.
# This is not a complete list of brands or official domains.
BRAND_DOMAINS = {
    "google": "google.com",
    "microsoft": "microsoft.com",
    "paypal": "paypal.com",
    "amazon": "amazon.com",
    "facebook": "facebook.com",
    "apple": "apple.com",
}


def _lookalike_findings(hostname):
    findings = []
    labels = hostname.lower().split(".")

    for brand, official_domain in BRAND_DOMAINS.items():
        if hostname == official_domain or hostname.endswith("." + official_domain):
            continue

        for label in labels:
            # Detect close spellings, such as paypaI-like variants.
            similarity = SequenceMatcher(
                None, label.replace("-", ""), brand
            ).ratio()

            if label != brand and len(label) >= 4 and similarity >= 0.80:
                findings.append(
                    f"Possible lookalike spelling of '{brand}'"
                )
                break

        # A brand name used in a different domain can be misleading.
        if brand in labels and hostname != official_domain:
            findings.append(
                f"Brand name '{brand}' appears in a different domain"
            )

    return list(dict.fromkeys(findings))

def check_google_safe_browsing(url):
    """
    Check a URL against Google Safe Browsing.
    Returns: (status, details)
    """

    api_key = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY")

    if not api_key or api_key == "paste_your_actual_api_key_here":
        return "disabled", "API key is not configured."

    endpoint = (
        "https://safebrowsing.googleapis.com/v4/"
        "threatMatches:find"
    )

    payload = {
        "client": {
            "clientId": "cyberpulse-student-project",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": [
                "MALWARE",
                "SOCIAL_ENGINEERING",
                "UNWANTED_SOFTWARE",
                "POTENTIALLY_HARMFUL_APPLICATION"
            ],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }

    try:
        response = requests.post(
            endpoint,
            params={"key": api_key},
            json=payload,
            timeout=8
        )

        if response.status_code != 200:
            return (
                "unavailable",
                f"Reputation service returned HTTP "
                f"{response.status_code}."
            )

        data = response.json()

        if data.get("matches"):
            threat_types = sorted({
                match.get("threatType", "UNKNOWN")
                for match in data["matches"]
            })

            return (
                "match",
                "Google Safe Browsing reported a match: "
                + ", ".join(threat_types)
            )

        return (
            "no_match",
            "No match was returned by Google Safe Browsing. "
            "This does not prove the URL is safe."
        )

    except (requests.RequestException, ValueError):
        return (
            "unavailable",
            "Could not complete the reputation check."
        )


def analyze_url(url):
    """Return (status, explanation), compatible with the current frontend."""

    if not isinstance(url, str) or not url.strip():
        return "Invalid", "Please enter a URL."

    url = url.strip()

    if any(ord(char) < 32 or char.isspace() for char in url):
        return "Invalid", "The URL contains whitespace or control characters."

    candidate = url if "://" in url else "https://" + url

    try:
        parsed = urlparse(candidate)
        hostname = parsed.hostname
        _ = parsed.port  # Validate port syntax.

        if (
            parsed.scheme not in ("http", "https")
            or not hostname
            or "." not in hostname
            or hostname.startswith(".")
            or hostname.endswith(".")
        ):
            return "Invalid", "The URL format is invalid."

    except ValueError:
        return "Invalid", "The URL or port format is invalid."

    hostname = hostname.rstrip(".").lower()
    findings = []

    def add_finding(points, message):
        findings.append((points, message))

    if parsed.scheme == "http":
        add_finding(15, "Uses unencrypted HTTP")

    if parsed.username is not None or parsed.password is not None:
        add_finding(25, "Contains credentials in the URL")

    try:
        ipaddress.ip_address(hostname)
        add_finding(20, "Uses an IP address instead of a domain name")
    except ValueError:
        pass

    if "xn--" in hostname:
        add_finding(20, "Contains an internationalized domain label")

    if len(hostname) > 60:
        add_finding(10, "Unusually long hostname")

    if hostname.count("-") >= 3:
        add_finding(10, "Hostname contains multiple hyphens")

    if re.search(r"\d{5,}", hostname):
        add_finding(10, "Hostname contains a long sequence of digits")

    decoded_text = unquote(
        hostname + parsed.path + "?" + parsed.query
    ).lower()

    for keyword, points in SUSPICIOUS_KEYWORDS.items():
        if keyword in decoded_text:
            add_finding(
                points,
                f"Contains the potentially suspicious keyword '{keyword}'"
            )

    for message in _lookalike_findings(hostname):
        add_finding(25, message)

    # Cap the score at 100. This is a heuristic score, not a probability.
    score = min(100, sum(points for points, _ in findings))
    api_status, api_details = check_google_safe_browsing(url)
    st_status = api_status
    st_details = api_details
    print("Safe Browsing status:", api_status)
    print("Safe Browsing details:", api_details)

    if api_status == "match":
        findings.append((50, api_details))
        score = min(100, sum(points for points, _ in findings))

    if not findings:
        return (
            "No Basic Warning Found",
            "Risk score: 0/100 (heuristic). "
            "No configured warning indicators were found. "
            "This does not prove the URL is safe."
        )

    details = "\n".join(
        f"- {message} (+{points})"
        for points, message in findings
    )

    message = (
        f"Risk score: {score}/100 (heuristic; not a probability)\n\n"
        f"Indicators found:\n{details}\n\n"
        "This result is a warning for review, not proof of malicious activity."
    )

    return "Review Needed", message
