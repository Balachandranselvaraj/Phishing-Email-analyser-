from email import policy
from email.parser import BytesParser, Parser
from bs4 import BeautifulSoup
import re


def _decode_payload(part):
    try:
        payload = part.get_payload(decode=True)
        if payload is None:
            return ""
        charset = part.get_content_charset() or "utf-8"
        return payload.decode(charset, errors="replace")
    except Exception:
        return ""


def html_to_text(html):
    soup = BeautifulSoup(html or "", "html.parser")
    return soup.get_text(" ", strip=True)


def parse_email(raw_email):
    if isinstance(raw_email, bytes):
        msg = BytesParser(policy=policy.default).parsebytes(raw_email)
    else:
        msg = Parser(policy=policy.default).parsestr(raw_email or "")

    headers = {key: str(value) for key, value in msg.items()}
    body_text = ""
    body_html = ""
    attachments = []

    if msg.is_multipart():
        for part in msg.walk():
            content_disposition = part.get_content_disposition()
            content_type = part.get_content_type()
            filename = part.get_filename()

            if filename or content_disposition == "attachment":
                payload = part.get_payload(decode=True) or b""
                attachments.append({
                    "filename": filename or "unknown",
                    "content_type": content_type,
                    "size": len(payload),
                    "bytes": payload,
                })
                continue

            if content_type == "text/plain":
                body_text += "\n" + _decode_payload(part)
            elif content_type == "text/html":
                body_html += "\n" + _decode_payload(part)
    else:
        content_type = msg.get_content_type()
        if content_type == "text/html":
            body_html = _decode_payload(msg)
        else:
            body_text = _decode_payload(msg)

    if not body_text and body_html:
        body_text = html_to_text(body_html)

    urls = extract_urls(body_text + "\n" + body_html)

    return {
        "headers": headers,
        "from": str(msg.get("From", "")),
        "to": str(msg.get("To", "")),
        "reply_to": str(msg.get("Reply-To", "")),
        "return_path": str(msg.get("Return-Path", "")),
        "subject": str(msg.get("Subject", "")),
        "date": str(msg.get("Date", "")),
        "body_text": body_text.strip(),
        "body_html": body_html.strip(),
        "urls": urls,
        "attachments": attachments,
    }


def extract_urls(text):
    pattern = r"https?://[^\s<'\")]+|www\.[^\s<'\")]+"
    matches = re.findall(pattern, text or "", flags=re.IGNORECASE)
    clean_urls = []
    for url in matches:
        url = url.rstrip(".,;:!?]})>")
        if url.startswith("www."):
            url = "http://" + url
        if url not in clean_urls:
            clean_urls.append(url)
    return clean_urls
