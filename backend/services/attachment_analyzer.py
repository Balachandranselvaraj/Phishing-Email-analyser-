import hashlib
import os
import re

# Highly dangerous - can execute code directly
CRITICAL_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".js", ".vbs", ".scr", ".ps1", ".jar", ".msi",
    ".hta", ".wsf", ".lnk", ".com", ".pif"
}

# Macro-enabled office documents (can contain malicious macros)
MACRO_EXTENSIONS = {".docm", ".xlsm", ".pptm", ".xltm"}

# Archives that can contain hidden executables
ARCHIVE_EXTENSIONS = {".zip", ".rar", ".7z", ".gz", ".tar", ".iso"}

# Suspicious strings to search for in file content
SUSPICIOUS_STRINGS = [
    b"powershell", b"cmd.exe", b"wscript", b"cscript", b"CreateObject",
    b"AutoOpen", b"Shell.Application", b"http://", b"https://", b"base64",
    b"eval", b"execute", b"ShellExecute", b"VBScript", b"rundll32",
]


def sha256(data):
    """Calculate SHA256 hash of data."""
    return hashlib.sha256(data or b"").hexdigest()


def calculate_entropy(data):
    """
    Calculate Shannon entropy of data (0-8).
    High entropy (>7.2) suggests compressed or encrypted content.
    """
    if not data:
        return 0.0
    import math
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    entropy = 0.0
    for count in counts:
        if count:
            p = count / len(data)
            entropy -= p * math.log2(p)
    return round(entropy, 3)


def analyze_attachments(attachments):
    """
    Analyze attachments for malware indicators.
    Returns comprehensive attachment analysis with confidence scores.
    """
    results = []
    total_score = 0

    for item in attachments:
        filename = item.get("filename", "unknown")
        data = item.get("bytes", b"") or b""
        ext = os.path.splitext(filename.lower())[1]
        issues = []
        score = 0
        confidence_factors = []

        # 1. Critical executable/script detection
        if ext in CRITICAL_EXTENSIONS:
            score += 40
            issues.append("CRITICAL: Dangerous executable/script file type that can execute code")
            confidence_factors.append(("critical_extension", 0.95))

        # 2. Macro-enabled office document
        elif ext in MACRO_EXTENSIONS:
            score += 30
            issues.append("Macro-enabled Office document (common malware vector)")
            confidence_factors.append(("macro_document", 0.9))

        # 3. Archive file
        elif ext in ARCHIVE_EXTENSIONS:
            score += 15
            issues.append("Archive file may hide malicious payloads or executables")
            confidence_factors.append(("archive_file", 0.7))

        # 4. File size analysis
        if len(data) > 10 * 1024 * 1024:  # >10MB
            score += 8
            issues.append("Large attachment size (>10MB)")
            confidence_factors.append(("large_file", 0.6))
        elif len(data) > 5 * 1024 * 1024:  # >5MB
            score += 4
            issues.append("Moderately large attachment size (>5MB)")
            confidence_factors.append(("moderately_large_file", 0.5))

        # 5. Entropy analysis (detect compression/encryption)
        sample_data = data[:1024 * 1024]  # Analyze first 1MB
        entropy = calculate_entropy(sample_data)
        if entropy > 7.2:
            score += 12
            issues.append(f"High entropy content detected (entropy: {entropy}) - likely compressed or encrypted")
            confidence_factors.append(("high_entropy", 0.75))
        elif entropy > 6.5:
            score += 4
            confidence_factors.append(("moderate_entropy", 0.5))

        # 6. Suspicious string detection
        lowered = sample_data.lower()
        found_strings = []
        for marker in SUSPICIOUS_STRINGS:
            if marker.lower() in lowered:
                found_strings.append(marker.decode(errors="ignore"))
        
        if found_strings:
            score += 20
            issues.append(f"Suspicious strings found: {', '.join(found_strings[:3])}")
            confidence_factors.append(("suspicious_strings", 0.85))

        # 7. Double extension detection (e.g., document.pdf.exe)
        name_without_ext = os.path.splitext(filename.lower())[0]
        if "." in name_without_ext:
            score += 12
            issues.append("Double extension detected (possible disguised executable)")
            confidence_factors.append(("double_extension", 0.8))

        # 8. Null bytes detection (obfuscation technique)
        if b"\x00" in sample_data and ext not in {".bin", ".iso", ".exe", ".dll", ".bin"}:
            score += 8
            issues.append("Null bytes detected (possible obfuscation)")
            confidence_factors.append(("null_bytes", 0.6))

        total_score += min(score, 55)
        
        # Calculate average confidence
        avg_confidence = sum(cf[1] for cf in confidence_factors) / len(confidence_factors) if confidence_factors else 0.5

        results.append({
            "filename": filename,
            "extension": ext,
            "content_type": item.get("content_type", "unknown"),
            "size": len(data),
            "size_kb": round(len(data) / 1024, 2),
            "sha256": sha256(data),
            "entropy": entropy,
            "score": min(score, 55),
            "confidence": round(avg_confidence, 2),
            "issues": issues or ["No obvious attachment issue found"],
        })

    return {
        "score": min(total_score, 60),  # Increased from 55 to 60
        "count": len(attachments),
        "results": results,
        "critical_attachments": len([r for r in results if r["score"] >= 40]),
        "suspicious_attachments": len([r for r in results if r["score"] >= 20]),
    }
