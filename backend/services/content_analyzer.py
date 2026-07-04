import re

# Enhanced phishing patterns with multiple variants
PHISHING_PATTERNS = {
    "urgency": [
        r"urgent", r"immediately", r"within 24 hours", r"act now", r"final warning",
        r"limited time", r"account will be closed", r"account suspended", r"time.{0,10}sensitive",
        r"don't delay", r"asap", r"verify now", r"confirm now", r"update now"
    ],
    "credential_theft": [
        r"verify your account", r"confirm your identity", r"password expired",
        r"reset your password", r"login to continue", r"validate your account",
        r"otp", r"one.?time.?password", r"card details", r"bank details", 
        r"ssn", r"social security", r"pin", r"security code", r"cvc",
        r"confirm password", r"re-enter password", r"verify identity"
    ],
    "financial": [
        r"payment failed", r"invoice attached", r"refund", r"wire transfer",
        r"tax refund", r"unusual transaction", r"billing issue", r"charge",
        r"payment pending", r"outstanding balance", r"claim", r"reward",
        r"prize", r"settlement", r"compensation", r"reimbursement"
    ],
    "generic_greeting": [
        r"dear customer", r"dear user", r"dear account holder", r"valued customer",
        r"dear member", r"hello customer", r"dear sir", r"dear madam"
    ],
    "threat": [
        r"legal action", r"blocked", r"terminated", r"penalty", r"locked",
        r"suspended", r"close.*account", r"fraud", r"unauthorized access",
        r"violation", r"restricted", r"disabled", r"deactivated"
    ],
    "impersonation": [
        r"on behalf of", r"acting as", r"representing", r"from our team",
        r"official.*notice", r"system.*notification", r"administrative.*notice"
    ],
}

# Words/phrases that reduce phishing score
LEGITIMATE_INDICATORS = [
    r"unsubscribe", r"email preferences", r"manage.*subscription",
    r"privacy policy", r"terms of service", r"contact us",
    r"no reply", r"do not reply", r"please don't reply"
]


def _count_suspicious_patterns(text):
    """Count suspicious patterns and return score + findings."""
    findings = []
    score = 0

    for category, patterns in PHISHING_PATTERNS.items():
        hits = []
        for pattern in patterns:
            if re.search(pattern, text, re.I):
                hits.append(pattern.replace("\\", "").replace("?", ""))
        if hits:
            # Progressive scoring: more patterns = higher score
            category_score = min(3 * len(hits), 15)
            score += category_score
            findings.append({
                "category": category,
                "matches": hits[:5],  # Show up to 5 matches
                "score": category_score,
                "confidence": min(len(hits) / 3, 1.0),  # Confidence 0-1
            })

    return score, findings


def _check_email_metadata(subject, body):
    """Check metadata like subject line style and body length."""
    score = 0
    findings = []

    # Check for very short body (often phishing)
    if len(body or "") < 40:
        score += 5
        findings.append({
            "category": "short_body",
            "matches": ["Very short email body (<40 chars)"],
            "score": 5,
            "confidence": 0.5
        })

    # Check for excessive uppercase in subject
    if re.search(r"[A-Z]{8,}", subject or ""):
        score += 5
        findings.append({
            "category": "subject_style",
            "matches": ["Subject contains long uppercase words"],
            "score": 5,
            "confidence": 0.6
        })

    # Check for excessive punctuation
    if subject and len(re.findall(r"[!?]{2,}", subject)) > 2:
        score += 3
        findings.append({
            "category": "excessive_punctuation",
            "matches": ["Multiple exclamation marks or question marks"],
            "score": 3,
            "confidence": 0.5
        })

    # Check for multiple URLs in body (common in phishing)
    url_count = len(re.findall(r"https?://|www\.", body or "", re.I))
    if url_count > 3:
        score += 4
        findings.append({
            "category": "multiple_urls",
            "matches": [f"Body contains {url_count} URLs"],
            "score": 4,
            "confidence": 0.6
        })

    return score, findings


def _check_legitimate_indicators(text):
    """Reduce score if legitimate indicators are found."""
    score = 0
    for indicator in LEGITIMATE_INDICATORS:
        if re.search(indicator, text, re.I):
            score -= 5
    return max(score, -10)  # Don't reduce more than 10 points


def analyze_content(subject, body):
    """
    Analyze email content for phishing indicators.
    Returns score (0-50) and detailed findings with confidence levels.
    """
    text = f"{subject or ''}\n{body or ''}".lower()
    
    # Main pattern analysis
    pattern_score, findings = _count_suspicious_patterns(text)
    
    # Metadata checks
    metadata_score, metadata_findings = _check_email_metadata(subject, body)
    findings.extend(metadata_findings)
    
    # Legitimate indicator adjustment
    legit_adjustment = _check_legitimate_indicators(text)
    
    # Combine scores
    total_score = pattern_score + metadata_score + legit_adjustment
    
    return {
        "score": min(max(total_score, 0), 50),  # Cap between 0-50
        "findings": findings or [{"category": "content", "matches": ["No obvious phishing language found"], "score": 0, "confidence": 0.8}],
        "pattern_count": sum(len(f.get("matches", [])) for f in findings),
        "analysis_summary": {
            "total_suspicious_patterns": len(findings),
            "has_urgency_language": any(f["category"] == "urgency" for f in findings),
            "has_credential_requests": any(f["category"] == "credential_theft" for f in findings),
            "has_financial_language": any(f["category"] == "financial" for f in findings),
            "has_threats": any(f["category"] == "threat" for f in findings),
        }
    }
