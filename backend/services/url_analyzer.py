from urllib.parse import urlparse
import ipaddress
import re
import tldextract

SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly",
    "cutt.ly", "rebrand.ly", "shorturl.at", "lnkd.in", "rb.gy", "short.link"
}

# Major legitimate brands
BRAND_KEYWORDS = {
    "paypal": ["paypal", "paypale"],
    "google": ["google", "gmail"],
    "microsoft": ["microsoft", "office365", "outlook"],
    "apple": ["apple", "icloud"],
    "amazon": ["amazon"],
    "netflix": ["netflix"],
    "facebook": ["facebook", "fbcdn"],
    "instagram": ["instagram"],
    "linkedin": ["linkedin"],
    "banking": ["icici", "hdfc", "sbi", "axisbank"],
    "fintech": ["phonepe", "paytm"],
}

# Common legitimate TLDs
LEGITIMATE_TLDS = {"com", "org", "net", "edu", "gov", "co", "uk", "de", "fr", "in", "io", "info"}

# Suspicious TLDs (often abused)
SUSPICIOUS_TLDS = {"xyz", "top", "club", "click", "work", "zip", "mov", "tk", "gq", "ml", "cf", "loan", "review", "download"}


def is_ip_host(hostname):
    """Check if hostname is actually an IP address."""
    try:
        ipaddress.ip_address(hostname)
        return True
    except Exception:
        return False


def _calculate_domain_similarity(domain1, domain2):
    """
    Calculate similarity between two domains (0-1).
    Used to detect typosquatting/lookalikes.
    """
    if domain1 == domain2:
        return 1.0
    
    # Normalize: replace common substitutions
    normalized1 = domain1.replace("0", "o").replace("1", "l").replace("3", "e").replace("5", "s")
    normalized2 = domain2.replace("0", "o").replace("1", "l").replace("3", "e").replace("5", "s")
    
    if normalized1 == normalized2:
        return 0.95
    
    # Levenshtein-like check for character substitution
    if len(domain1) == len(domain2):
        diff = sum(c1 != c2 for c1, c2 in zip(domain1, domain2))
        return 1.0 - (diff / len(domain1))
    
    return 0


def _check_brand_impersonation(host, domain, tld):
    """
    Check if URL is impersonating a known brand.
    Returns (brand_name, suspicion_level, message).
    """
    normalized_host = host.replace("0", "o").replace("1", "l").replace("3", "e").replace("5", "s").replace("-", "")
    normalized_domain = domain.replace("0", "o").replace("1", "l").replace("3", "e").replace("5", "s").replace("-", "")
    
    for brand, keywords in BRAND_KEYWORDS.items():
        for keyword in keywords:
            keyword_normalized = keyword.replace("-", "")
            
            # Exact brand match but wrong domain
            if keyword in normalized_domain and domain not in {f"{keyword}", brand}:
                # Check if it's actually the real domain
                if domain not in {f"{keyword}.com", f"{keyword}.co", brand}:
                    # Check if the TLD looks suspicious
                    if tld in SUSPICIOUS_TLDS:
                        return brand, 0.9, f"Brand '{brand}' on suspicious TLD '.{tld}'"
                    else:
                        return brand, 0.6, f"Domain contains brand name '{brand}' but uses '.{tld}'"
            
            # Typosquatting: 1 or 2 character substitutions
            if keyword_normalized in normalized_domain:
                similarity = _calculate_domain_similarity(keyword, domain)
                if 0.7 <= similarity < 1.0:
                    return brand, 0.85, f"Possible typosquatting: '{domain}' similar to '{keyword}'"
    
    return None, 0, None


def analyze_urls(urls):
    """
    Analyze URLs for phishing indicators.
    Returns comprehensive URL analysis with confidence scores.
    """
    results = []
    score = 0

    for url in urls:
        try:
            parsed = urlparse(url)
            host = (parsed.hostname or "").lower()
            ext = tldextract.extract(host)
            domain = ".".join(part for part in [ext.domain, ext.suffix] if part)
            tld = ext.suffix.split(".")[-1] if ext.suffix else ""
            issues = []
            url_score = 0
            confidence_factors = []

            # 1. HTTPS check
            if parsed.scheme != "https":
                url_score += 10
                issues.append("URL does not use HTTPS (not encrypted)")
                confidence_factors.append(("no_https", 0.7))

            # 2. Shortened URL detection
            if host in SHORTENERS or domain in SHORTENERS:
                url_score += 20
                issues.append("Shortened URL detected (destination hidden)")
                confidence_factors.append(("shortened_url", 0.95))

            # 3. IP address instead of domain
            if is_ip_host(host):
                url_score += 25
                issues.append("URL uses IP address instead of domain name")
                confidence_factors.append(("ip_host", 0.95))

            # 4. @ symbol (can hide real destination)
            if "@" in url:
                url_score += 20
                issues.append("URL contains @ symbol (can hide real destination)")
                confidence_factors.append(("at_symbol", 0.9))

            # 5. Many subdomains
            if len(host.split(".")) >= 4:
                url_score += 8
                issues.append("URL has excessive subdomains")
                confidence_factors.append(("many_subdomains", 0.6))

            # 6. Suspicious TLD
            if tld in SUSPICIOUS_TLDS:
                url_score += 15
                issues.append(f"Domain uses commonly abused TLD '.{tld}'")
                confidence_factors.append(("suspicious_tld", 0.8))
            elif tld not in LEGITIMATE_TLDS and tld:
                url_score += 5
                confidence_factors.append(("uncommon_tld", 0.5))

            # 7. Phishing-related keywords in URL
            if re.search(r"login|verify|secure|account|update|wallet|bank|password|confirm|validate|reset", url, re.I):
                url_score += 10
                issues.append("URL contains phishing-related keywords")
                confidence_factors.append(("phishing_keywords", 0.75))

            # 8. Brand impersonation check
            brand_name, brand_suspicion, brand_msg = _check_brand_impersonation(host, domain, tld)
            if brand_name:
                brand_score = int(brand_suspicion * 20)
                url_score += brand_score
                issues.append(brand_msg)
                confidence_factors.append(("brand_impersonation", brand_suspicion))

            # 9. Port check (non-standard ports are suspicious)
            if parsed.port and parsed.port not in [80, 443]:
                url_score += 8
                issues.append(f"Non-standard port {parsed.port} detected")
                confidence_factors.append(("non_standard_port", 0.6))

            score += min(url_score, 40)
            
            # Calculate average confidence
            avg_confidence = sum(cf[1] for cf in confidence_factors) / len(confidence_factors) if confidence_factors else 0.5

            results.append({
                "url": url,
                "host": host,
                "domain": domain,
                "tld": tld,
                "score": min(url_score, 40),
                "confidence": round(avg_confidence, 2),
                "issues": issues or ["No obvious URL issue found"],
            })

        except Exception as e:
            # Malformed URL
            results.append({
                "url": url,
                "host": "unknown",
                "domain": "unknown",
                "tld": "unknown",
                "score": 15,
                "confidence": 0.7,
                "issues": [f"Malformed URL: {str(e)}"],
            })

    return {
        "score": min(score, 50),
        "count": len(urls),
        "results": results,
        "average_confidence": round(sum(r["confidence"] for r in results) / len(results) if results else 0, 2),
    }
