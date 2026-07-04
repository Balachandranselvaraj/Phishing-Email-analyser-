"""
Sender Reputation Analysis Module

Analyzes sender domain and email address for indicators of spoofing or malicious intent.
This implements the "Sender Reputation" component of the phishing detection methodology.
"""

from email.utils import parseaddr
import re
from datetime import datetime


# Known blocklists and suspicious patterns
KNOWN_SUSPICIOUS_DOMAINS = {
    "tempmail.com", "guerrillamail.com", "10minutemail.com", "maildrop.cc",
    "throwaway.email", "fakeinbox.com", "trashmail.com"
}

# Legitimate corporate domains (won't flag these)
TRUSTED_DOMAINS = {
    "google.com", "microsoft.com", "apple.com", "amazon.com", "paypal.com",
    "apple.com", "facebook.com", "linkedin.com", "github.com", "ibm.com"
}


def _extract_sender_info(from_header):
    """Extract display name and email from From header."""
    display_name, email_addr = parseaddr(from_header or "")
    return display_name.strip(), email_addr.strip()


def _check_free_email_abuse(email_addr):
    """
    Check if sender is using a free email service to impersonate a company.
    This is a common phishing tactic.
    """
    free_email_domains = {
        "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com",
        "mail.com", "protonmail.com", "icloud.com", "yandex.com"
    }
    
    if "@" not in email_addr:
        return None, 0
    
    domain = email_addr.split("@")[-1].lower()
    return domain in free_email_domains, 0


def _check_suspicious_domain(email_addr):
    """Check if email uses a known temporary/disposable email domain."""
    if "@" not in email_addr:
        return None, 0, None  # Fixed: must always return 3 values

    domain = email_addr.split("@")[-1].lower()

    if domain in KNOWN_SUSPICIOUS_DOMAINS:
        return True, 20, f"Disposable email domain detected: {domain}"

    # Check for suspicious patterns
    if any(x in domain for x in ["temp", "trash", "fake", "test"]):
        if domain not in TRUSTED_DOMAINS:
            return True, 10, f"Suspicious domain pattern: {domain}"

    return False, 0, None


def _check_display_name_email_mismatch(display_name, email_addr):
    """
    Check if display name matches the email domain.
    E.g., "Amazon Customer Service" from "support@randomdomain.com" is suspicious.
    """
    if not display_name or not email_addr or "@" not in email_addr:
        return None, 0, None
    
    domain = email_addr.split("@")[-1].lower()
    display_lower = display_name.lower()
    
    # Extract company/brand name from domain
    domain_name = domain.split(".")[0].lower()
    
    # Check if display name mentions a brand but email is from different domain
    common_companies = {
        "amazon": ["amazon", "aws"],
        "apple": ["apple", "icloud"],
        "google": ["google", "gmail"],
        "microsoft": ["microsoft", "outlook", "windows"],
        "paypal": ["paypal", "ebay"],
        "facebook": ["facebook", "meta"],
        "linkedin": ["linkedin"],
        "bank": ["bank", "financial", "credit union"],
    }
    
    for company, keywords in common_companies.items():
        for keyword in keywords:
            if keyword in display_lower:
                # Check if email is actually from that company
                if company not in domain_name and domain not in TRUSTED_DOMAINS:
                    return True, 15, f"Display name mentions '{company}' but email is from '{domain}'"
    
    return False, 0, None


def _check_generic_greeting(body_text):
    """
    Check if email uses generic greetings instead of personalized.
    Phishing emails often use "Dear Customer" instead of actual names.
    """
    generic_greetings = [
        r"dear customer", r"dear user", r"dear account holder",
        r"hello customer", r"dear sir", r"dear madam", r"valued customer"
    ]
    
    body_lower = (body_text or "").lower()
    found_greetings = []
    
    for greeting in generic_greetings:
        if re.search(greeting, body_lower):
            found_greetings.append(greeting.replace("r\"", "").replace("\"", ""))
    
    if found_greetings:
        return True, 8, f"Generic greetings used: {', '.join(found_greetings[:2])}"
    
    return False, 0, None


def analyze_sender_reputation(parsed_email):
    """
    Analyze sender reputation based on multiple indicators.
    
    Returns:
    {
        "score": 0-30,
        "findings": [],
        "risk_indicators": {
            "free_email": bool,
            "suspicious_domain": bool,
            "display_name_mismatch": bool,
            "generic_greeting": bool,
        }
    }
    """
    findings = []
    score = 0
    risk_indicators = {
        "free_email": False,
        "suspicious_domain": False,
        "display_name_mismatch": False,
        "generic_greeting": False,
    }
    
    from_header = parsed_email.get("from", "")
    body_text = parsed_email.get("body_text", "")
    
    # 1. Check for display name vs email mismatch
    display_name, email_addr = _extract_sender_info(from_header)
    is_mismatch, mismatch_score, mismatch_msg = _check_display_name_email_mismatch(display_name, email_addr)
    if is_mismatch and mismatch_msg:
        score += mismatch_score
        findings.append(mismatch_msg)
        risk_indicators["display_name_mismatch"] = True
    
    # 2. Check for suspicious domain
    is_suspicious, suspicious_score, suspicious_msg = _check_suspicious_domain(email_addr)
    if is_suspicious and suspicious_msg:
        score += suspicious_score
        findings.append(suspicious_msg)
        risk_indicators["suspicious_domain"] = True
    
    # 3. Check for generic greeting (sign of mass phishing)
    has_generic, generic_score, generic_msg = _check_generic_greeting(body_text)
    if has_generic and generic_msg:
        score += generic_score
        findings.append(generic_msg)
        risk_indicators["generic_greeting"] = True
    
    # 4. Check if using free email service
    is_free_email, free_score = _check_free_email_abuse(email_addr)
    if is_free_email:
        # Only flag if also has other suspicious indicators
        if any([is_mismatch, is_suspicious, has_generic]):
            score += 5
            findings.append(f"Sender using free email service: {email_addr.split('@')[1]}")
            risk_indicators["free_email"] = True
    
    return {
        "score": min(score, 30),  # Cap at 30
        "findings": findings or ["No suspicious sender reputation indicators"],
        "sender_email": email_addr,
        "sender_display_name": display_name,
        "risk_indicators": risk_indicators,
        "risk_summary": sum(1 for v in risk_indicators.values() if v),
    }
