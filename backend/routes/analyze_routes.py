import os
from flask import Blueprint, jsonify, request
from config import ALLOWED_EMAIL_EXTENSIONS
from services.email_parser import parse_email
from services.header_analyzer import analyze_headers
from services.url_analyzer import analyze_urls
from services.attachment_analyzer import analyze_attachments
from services.content_analyzer import analyze_content
from services.sender_reputation import analyze_sender_reputation
from services.risk_score import calculate_risk
from storage.db import save_scan

analyze_bp = Blueprint("analyze", __name__)


def _read_email_input():
    raw_text = request.form.get("raw_email", "") or ""
    email_file = request.files.get("email_file")

    if email_file and email_file.filename:
        ext = os.path.splitext(email_file.filename.lower())[1]
        if ext not in ALLOWED_EMAIL_EXTENSIONS:
            raise ValueError("Only .eml or .txt email files are allowed")
        return email_file.read(), email_file.filename

    if not raw_text.strip():
        raise ValueError("Paste raw email content or upload a .eml file")
    return raw_text, "pasted_email"


def _read_extra_attachments():
    attachments = []
    for file in request.files.getlist("attachments"):
        if not file or not file.filename:
            continue
        data = file.read()
        attachments.append({
            "filename": file.filename,
            "content_type": file.content_type or "application/octet-stream",
            "size": len(data),
            "bytes": data,
        })
    return attachments


@analyze_bp.post("/analyze")
def analyze_email():
    try:
        raw_email, source_name = _read_email_input()
        parsed = parse_email(raw_email)
        extra_attachments = _read_extra_attachments()
        all_attachments = parsed.get("attachments", []) + extra_attachments

        # Run all analysis components
        header_result = analyze_headers(parsed)
        sender_reputation_result = analyze_sender_reputation(parsed)
        url_result = analyze_urls(parsed.get("urls", []))
        attachment_result = analyze_attachments(all_attachments)
        content_result = analyze_content(parsed.get("subject"), parsed.get("body_text"))
        
        # Calculate overall risk
        risk = calculate_risk(header_result, url_result, attachment_result, content_result,
                              sender_reputation_result=sender_reputation_result)

        result = {
            "source": source_name,
            "email_summary": {
                "from": parsed.get("from", ""),
                "to": parsed.get("to", ""),
                "reply_to": parsed.get("reply_to", ""),
                "return_path": parsed.get("return_path", ""),
                "subject": parsed.get("subject", ""),
                "date": parsed.get("date", ""),
                "url_count": len(parsed.get("urls", [])),
                "attachment_count": len(all_attachments),
            },
            "risk": risk,
            "analysis_components": {
                "header_analysis": header_result,
                "sender_reputation": sender_reputation_result,
                "url_analysis": url_result,
                "attachment_analysis": attachment_result,
                "content_analysis": content_result,
            },
        }
        scan_id = save_scan(result)
        result["scan_id"] = scan_id
        return jsonify(result)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": "Analysis failed", "details": str(exc)}), 500
