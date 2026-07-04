import re
from email.utils import parseaddr


def _domain_from_email(value):
    _, addr = parseaddr(value or "")
    if "@" in addr:
        return addr.split("@")[-1].lower()
    return ""


def _extract_display_name_and_email(value):
    """Extract display name and email address from From/Reply-To headers."""
    display_name, email_addr = parseaddr(value or "")
    return display_name.strip(), email_addr.strip()


def _check_display_name_mismatch(display_name, email_addr):
    """
    Check if display name matches the email domain.
    E.g., "PayPal Support" from "paypa1-secure@randomdomain.xyz" is suspicious.
    """
    if not display_name or not email_addr or "@" not in email_addr:
        return None, 0
    
    domain = email_addr.split("@")[-1].lower()
    display_lower = display_name.lower()
    
    # Extract brand name from display name
    common_brands = {
        "paypal": ["paypal"],
        "google": ["google", "gmail"],
        "microsoft": ["microsoft", "outlook"],
        "apple": ["apple", "icloud"],
        "amazon": ["amazon"],
        "banking": ["bank", "icici", "hdfc", "sbi", "axis"],
    }
    
    brand_found = None
    for brand, keywords in common_brands.items():
        for keyword in keywords:
            if keyword in display_lower:
                brand_found = brand
                break
        if brand_found:
            break
    
    if brand_found:
        if brand_found not in domain:
            return f"Display name mentions '{brand_found}' but email is from '{domain}'", 20
    
    return None, 0


def analyze_headers(parsed):
    headers = parsed.get("headers", {})
    findings = []
    score = 0

    # 1. SPF/DKIM/DMARC authentication checks
    auth_results = " ".join([
        headers.get("Authentication-Results", ""),
        headers.get("ARC-Authentication-Results", ""),
        headers.get("Received-SPF", ""),
    ]).lower()

    checks = {
        "spf": "unknown",
        "dkim": "unknown",
        "dmarc": "unknown",
    }

    for key in checks:
        if re.search(rf"\b{key}\s*=\s*pass\b", auth_results):
            checks[key] = "pass"
        elif re.search(rf"\b{key}\s*=\s*(fail|softfail|temperror|permerror|neutral)\b", auth_results):
            checks[key] = "fail"
            score += 15 if key != "dmarc" else 20
            findings.append(f"{key.upper()} authentication failed or is not trusted")

    # 2. Domain mismatch checks
    from_domain = _domain_from_email(parsed.get("from"))
    reply_domain = _domain_from_email(parsed.get("reply_to"))
    return_path_domain = _domain_from_email(parsed.get("return_path"))

    if parsed.get("reply_to") and from_domain and reply_domain and from_domain != reply_domain:
        score += 15
        findings.append("Reply-To domain is different from From domain")

    if parsed.get("return_path") and from_domain and return_path_domain and from_domain != return_path_domain:
        score += 10
        findings.append("Return-Path domain is different from From domain")

    # 3. Display name vs email address mismatch (brand spoofing)
    display_name, email_addr = _extract_display_name_and_email(parsed.get("from"))
    mismatch_msg, mismatch_score = _check_display_name_mismatch(display_name, email_addr)
    if mismatch_msg:
        score += mismatch_score
        findings.append(mismatch_msg)

    # 4. Received chain analysis
    received_count = len([k for k in headers.keys() if k.lower() == "received"])
    if received_count > 8:
        score += 5
        findings.append("Email passed through many mail servers (possible relay abuse)")
    elif received_count == 0:
        score += 8
        findings.append("No Received headers found (suspicious)")

    # 5. Message-ID check
    if not headers.get("Message-ID"):
        score += 10
        findings.append("Message-ID header is missing (sign of spoofed email)")

    # 6. X-Originating-IP analysis
    x_orig_ip = headers.get("X-Originating-IP", "")
    if x_orig_ip and re.search(r"\d+\.\d+\.\d+\.\d+", x_orig_ip):
        findings.append(f"Email sent from IP: {x_orig_ip}")

    return {
        "score": min(score, 60),
        "checks": checks,
        "from_domain": from_domain,
        "from_display_name": display_name,
        "reply_to_domain": reply_domain,
        "return_path_domain": return_path_domain,
        "findings": findings,
    }
