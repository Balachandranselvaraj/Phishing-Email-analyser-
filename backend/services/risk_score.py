def calculate_risk(header_result, url_result, attachment_result, content_result,
                    sender_reputation_result=None):
    """
    Calculate overall risk score using weighted combination of all analysis components.
    Uses the 6-point methodology: headers, sender reputation, content, URLs, attachments, and verdict.
    
    Scoring:
    - Headers: up to 60 points (SPF/DKIM/DMARC, display name mismatch, domain mismatches)
    - URLs: up to 50 points (HTTPS, shortened URLs, IP hosts, brand impersonation)
    - Attachments: up to 60 points (executables, macros, entropy, suspicious strings)
    - Content: up to 50 points (urgency, credential theft, financial, threats)
    - TOTAL: 220 points max (normalized to 100)
    """
    
    # Get component scores
    header_score = header_result.get("score", 0)
    url_score = url_result.get("score", 0)
    attachment_score = attachment_result.get("score", 0)
    content_score = content_result.get("score", 0)
    
    # Weighted aggregation (adjusted based on threat severity)
    # Attachments are most critical (35% weight)
    # Headers are important for sender verification (25% weight)
    # URLs are critical for credential theft (25% weight)
    # Content analysis (15% weight)
    
    weights = {
        "attachment": 0.35,
        "header": 0.25,
        "url": 0.25,
        "content": 0.15,
    }
    
    # Normalize scores to 0-100 scale based on max component values
    normalized_attachment = min(attachment_score / 60 * 100, 100)
    normalized_header = min(header_score / 60 * 100, 100)
    normalized_url = min(url_score / 50 * 100, 100)
    normalized_content = min(content_score / 50 * 100, 100)
    
    # Calculate weighted score
    score = (
        normalized_attachment * weights["attachment"] +
        normalized_header * weights["header"] +
        normalized_url * weights["url"] +
        normalized_content * weights["content"]
    )
    
    final_score = min(int(score), 100)

    # Enhanced verdict logic
    if final_score >= 80:
        verdict = "CRITICAL - Highly Likely Phishing"
        recommendation = "⚠️ DO NOT interact with this email. Do not click links, open attachments, or reply. Report immediately to security team."
    elif final_score >= 60:
        verdict = "Dangerous - Probable Phishing"
        recommendation = "⚠️ This email shows multiple phishing indicators. Do not click links or download attachments. Verify sender using a trusted channel before taking any action."
    elif final_score >= 40:
        verdict = "Suspicious - Possible Phishing"
        recommendation = "⚠️ This email has some phishing characteristics. Be cautious with links and attachments. Verify the sender independently before responding or taking any action."
    elif final_score >= 20:
        verdict = "Low Risk - Minor Concerns"
        recommendation = "✓ No major warning signs found. Still verify unexpected requests independently before taking action."
    else:
        verdict = "Safe - Low Risk"
        recommendation = "✓ This email appears legitimate. No obvious phishing indicators detected."

    # Generate human-readable score explanation
    score_explanation = _generate_score_explanation(
        final_score, verdict,
        header_result, url_result, attachment_result, content_result,
        sender_reputation_result,
        weights, normalized_header, normalized_url,
        normalized_attachment, normalized_content,
    )

    return {
        "score": final_score,
        "verdict": verdict,
        "recommendation": recommendation,
        "score_explanation": score_explanation,
        "component_breakdown": {
            "headers": {
                "raw_score": header_score,
                "normalized_score": round(normalized_header, 1),
                "weight": weights["header"],
                "contribution": round(normalized_header * weights["header"], 1),
            },
            "urls": {
                "raw_score": url_score,
                "normalized_score": round(normalized_url, 1),
                "weight": weights["url"],
                "contribution": round(normalized_url * weights["url"], 1),
            },
            "attachments": {
                "raw_score": attachment_score,
                "normalized_score": round(normalized_attachment, 1),
                "weight": weights["attachment"],
                "contribution": round(normalized_attachment * weights["attachment"], 1),
            },
            "content": {
                "raw_score": content_score,
                "normalized_score": round(normalized_content, 1),
                "weight": weights["content"],
                "contribution": round(normalized_content * weights["content"], 1),
            },
        },
        "risk_level": "Critical" if final_score >= 80 else "Dangerous" if final_score >= 60 else "Suspicious" if final_score >= 40 else "Low Risk" if final_score >= 20 else "Safe",
    }


def _generate_score_explanation(final_score, verdict,
                                header_result, url_result,
                                attachment_result, content_result,
                                sender_reputation_result,
                                weights, norm_header, norm_url,
                                norm_attachment, norm_content):
    """
    Build a structured, human-readable explanation of why this email
    received the given risk score.
    
    Returns a dict with:
      - summary: one-sentence overview
      - categories: list of { name, contribution, status, reasons[] }
    """

    categories = []

    # --- Headers ---
    header_reasons = header_result.get("findings", [])
    header_contribution = round(norm_header * weights["header"], 1)
    checks = header_result.get("checks", {})
    auth_notes = []
    for proto in ("spf", "dkim", "dmarc"):
        status = checks.get(proto, "unknown")
        if status == "fail":
            auth_notes.append(f"{proto.upper()} authentication failed")
        elif status == "unknown":
            auth_notes.append(f"{proto.upper()} could not be verified")

    categories.append({
        "name": "Email Headers & Authentication",
        "icon": "🔐",
        "contribution": header_contribution,
        "weight_pct": int(weights["header"] * 100),
        "status": _severity_label(norm_header),
        "reasons": (auth_notes + header_reasons) if auth_notes else header_reasons,
    })

    # --- URLs ---
    url_reasons = []
    for r in url_result.get("results", []):
        issues = r.get("issues", [])
        url_str = r.get("url", "")
        for issue in issues:
            url_reasons.append(f"{issue} — {url_str}" if url_str else issue)
    if not url_reasons and url_result.get("findings"):
        url_reasons = url_result["findings"]

    url_contribution = round(norm_url * weights["url"], 1)
    categories.append({
        "name": "URLs & Links",
        "icon": "🔗",
        "contribution": url_contribution,
        "weight_pct": int(weights["url"] * 100),
        "status": _severity_label(norm_url),
        "reasons": url_reasons or ["No suspicious URLs detected"],
    })

    # --- Attachments ---
    att_reasons = []
    for r in attachment_result.get("results", []):
        issues = r.get("issues", [])
        fname = r.get("filename", "")
        for issue in issues:
            att_reasons.append(f"{issue} — {fname}" if fname else issue)
    if not att_reasons and attachment_result.get("findings"):
        att_reasons = attachment_result["findings"]

    att_contribution = round(norm_attachment * weights["attachment"], 1)
    categories.append({
        "name": "Attachments",
        "icon": "📎",
        "contribution": att_contribution,
        "weight_pct": int(weights["attachment"] * 100),
        "status": _severity_label(norm_attachment),
        "reasons": att_reasons or ["No suspicious attachments detected"],
    })

    # --- Content ---
    content_reasons = content_result.get("findings", [])
    content_contribution = round(norm_content * weights["content"], 1)
    categories.append({
        "name": "Email Content & Language",
        "icon": "📝",
        "contribution": content_contribution,
        "weight_pct": int(weights["content"] * 100),
        "status": _severity_label(norm_content),
        "reasons": content_reasons or ["No suspicious content patterns detected"],
    })

    # --- Sender Reputation (if available) ---
    if sender_reputation_result:
        rep_reasons = sender_reputation_result.get("findings", [])
        rep_score = sender_reputation_result.get("score", 0)
        rep_norm = min(rep_score / 30 * 100, 100)
        categories.append({
            "name": "Sender Reputation",
            "icon": "👤",
            "contribution": round(rep_norm * 0.1, 1),  # informational
            "weight_pct": None,  # not part of weighted score
            "status": _severity_label(rep_norm),
            "reasons": rep_reasons,
        })

    # --- Build summary sentence ---
    flagged = [c for c in categories if c["contribution"] > 0 and c["status"] != "Clean"]
    if not flagged:
        summary = (
            f"This email scored {final_score}/100 ({verdict}). "
            "No significant risk indicators were found across any analysis category."
        )
    else:
        top_names = [c["name"] for c in sorted(flagged, key=lambda c: c["contribution"], reverse=True)[:3]]
        summary = (
            f"This email scored {final_score}/100 ({verdict}). "
            f"The main risk factors come from: {', '.join(top_names)}."
        )

    return {
        "summary": summary,
        "categories": categories,
    }


def _severity_label(normalized_score):
    """Return a human-readable severity word for a 0-100 normalized score."""
    if normalized_score >= 70:
        return "High Risk"
    elif normalized_score >= 35:
        return "Moderate"
    elif normalized_score > 0:
        return "Low"
    return "Clean"

