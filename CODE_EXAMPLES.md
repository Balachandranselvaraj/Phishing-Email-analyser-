# Code Examples: Phishing Detection in Action

## Example 1: Sophisticated Phishing Email

### Input Email
```
From: "Amazon Customer Service" <support@amazoniservices.xyz>
Reply-To: verify@amazoniservices.xyz
Subject: URGENT: Your Account Will Be Closed in 24 Hours!!!
To: user@example.com

Dear Customer,

We have detected unusual activity on your Amazon account. 
To prevent your account from being permanently closed, 
please verify your identity immediately by clicking the link below.

Click here to verify: http://amazoni-services.xyz/verify-account?user=abc123

Alternatively, your will need to confirm your credit card details, 
SSN, and one-time password (OTP).

Regards,
Amazon Security Team
```

### Analysis Output
```json
{
  "risk": {
    "score": 87,
    "verdict": "CRITICAL - Highly Likely Phishing",
    "recommendation": "⚠️ DO NOT interact with this email. Do not click links, open attachments, or reply. Report immediately to security team.",
    "risk_level": "Critical",
    "component_breakdown": {
      "headers": {
        "raw_score": 45,
        "normalized_score": 75.0,
        "contribution": 18.8
      },
      "urls": {
        "raw_score": 38,
        "normalized_score": 76.0,
        "contribution": 19.0
      },
      "attachments": {
        "raw_score": 0,
        "normalized_score": 0.0,
        "contribution": 0.0
      },
      "content": {
        "raw_score": 42,
        "normalized_score": 84.0,
        "contribution": 12.6
      }
    }
  },
  "analysis_components": {
    "header_analysis": {
      "score": 45,
      "checks": {
        "spf": "unknown",
        "dkim": "unknown",
        "dmarc": "unknown"
      },
      "findings": [
        "Display name mentions 'amazon' but email is from 'xyz.com' (+20)",
        "Reply-To domain is different from From domain (+15)",
        "Domain uses commonly abused TLD '.xyz' (+10)"
      ]
    },
    "sender_reputation": {
      "score": 22,
      "findings": [
        "Domain contains brand name 'amazon' on suspicious TLD '.xyz'",
        "Display name 'Amazon Customer Service' from suspicious domain"
      ],
      "risk_indicators": {
        "suspicious_domain": true,
        "display_name_mismatch": true
      }
    },
    "content_analysis": {
      "score": 42,
      "findings": [
        {
          "category": "urgency",
          "matches": ["urgent", "within 24 hours", "immediately"],
          "score": 9,
          "confidence": 0.9
        },
        {
          "category": "threat",
          "matches": ["account will be closed", "permanently closed"],
          "score": 6,
          "confidence": 0.85
        },
        {
          "category": "credential_theft",
          "matches": ["verify your account", "verify your identity", "credit card details", "ssn", "otp"],
          "score": 15,
          "confidence": 0.95
        },
        {
          "category": "generic_greeting",
          "matches": ["dear customer"],
          "score": 3,
          "confidence": 0.8
        },
        {
          "category": "short_body",
          "score": 5,
          "confidence": 0.6
        },
        {
          "category": "subject_style",
          "score": 4,
          "confidence": 0.7
        }
      ],
      "analysis_summary": {
        "has_urgency_language": true,
        "has_credential_requests": true,
        "has_financial_language": false,
        "has_threats": true
      }
    },
    "url_analysis": {
      "score": 38,
      "count": 1,
      "results": [
        {
          "url": "http://amazoni-services.xyz/verify-account?user=abc123",
          "host": "amazoni-services.xyz",
          "domain": "amazoni-services",
          "tld": "xyz",
          "score": 38,
          "confidence": 0.92,
          "issues": [
            "URL does not use HTTPS (not encrypted)",
            "Domain uses commonly abused TLD '.xyz'",
            "Possible typosquatting: 'amazoni-services' similar to 'amazon'",
            "URL contains phishing-related keywords"
          ]
        }
      ]
    },
    "attachment_analysis": {
      "score": 0,
      "count": 0,
      "results": [],
      "critical_attachments": 0,
      "suspicious_attachments": 0
    }
  }
}
```

### Detection Breakdown
1. **Header (45 pts)**: Display name mismatch + Wrong TLD + Domain mismatch
2. **Sender Reputation (22 pts)**: Suspicious domain + Brand abuse
3. **Content (42 pts)**: Urgency + Threats + Credential theft + Generic greeting
4. **URLs (38 pts)**: No HTTPS + Typosquatting + Phishing keywords + Suspicious TLD
5. **Final Score**: 87 → CRITICAL

---

## Example 2: Legitimate Corporate Email

### Input Email
```
From: "Sarah Johnson" <sarah.johnson@company.com>
Subject: Q4 Performance Review Scheduled
To: team@company.com
Date: Mon, 1 Jan 2024 10:30:00 +0000

Hi Team,

Your Q4 performance reviews have been scheduled. Please log into the HR portal 
using your company credentials to view the details.

https://hr.company.com/reviews

If you have any questions, please contact HR.

Best regards,
Sarah Johnson
HR Manager
Company Inc.
```

### Analysis Output
```json
{
  "risk": {
    "score": 5,
    "verdict": "Safe - Low Risk",
    "recommendation": "✓ This email appears legitimate. No obvious phishing indicators detected.",
    "risk_level": "Safe",
    "component_breakdown": {
      "headers": {
        "raw_score": 0,
        "normalized_score": 0.0,
        "contribution": 0.0
      },
      "urls": {
        "raw_score": 0,
        "normalized_score": 0.0,
        "contribution": 0.0
      },
      "attachments": {
        "raw_score": 0,
        "normalized_score": 0.0,
        "contribution": 0.0
      },
      "content": {
        "raw_score": 5,
        "normalized_score": 10.0,
        "contribution": 1.5
      }
    }
  },
  "analysis_components": {
    "header_analysis": {
      "score": 0,
      "checks": {
        "spf": "pass",
        "dkim": "pass",
        "dmarc": "pass"
      },
      "findings": []
    },
    "sender_reputation": {
      "score": 0,
      "findings": [
        "No suspicious sender reputation indicators"
      ],
      "risk_indicators": {
        "free_email": false,
        "suspicious_domain": false,
        "display_name_mismatch": false,
        "generic_greeting": false
      }
    },
    "content_analysis": {
      "score": 5,
      "findings": [],
      "analysis_summary": {
        "has_urgency_language": false,
        "has_credential_requests": false,
        "has_financial_language": false,
        "has_threats": false
      }
    },
    "url_analysis": {
      "score": 0,
      "count": 1,
      "results": [
        {
          "url": "https://hr.company.com/reviews",
          "host": "hr.company.com",
          "domain": "company",
          "tld": "com",
          "score": 0,
          "confidence": 0.95,
          "issues": []
        }
      ]
    },
    "attachment_analysis": {
      "score": 0,
      "count": 0,
      "results": [],
      "critical_attachments": 0,
      "suspicious_attachments": 0
    }
  }
}
```

### Detection Summary
- ✅ All authentication checks pass
- ✅ Display name matches domain
- ✅ Legitimate greeting (personalized)
- ✅ HTTPS URL to corporate domain
- ✅ No suspicious patterns
- ✅ Score: 5 → SAFE

---

## Example 3: Suspicious (Medium Risk) Email

### Input Email
```
From: "Banking Alert" <alerts@secure-banking-alerts.com>
Subject: Unusual Activity - Please Verify
To: customer@example.com

Dear Account Holder,

We detected some unusual activity. Please verify by clicking:
http://banking-alerts.info/verify

Thanks
Banking Team
```

### Analysis Output (Summary)
```json
{
  "risk": {
    "score": 58,
    "verdict": "Suspicious - Possible Phishing",
    "recommendation": "⚠️ This email has some phishing characteristics. Be cautious with links and attachments. Verify the sender independently.",
    "risk_level": "Suspicious"
  },
  "analysis_components": {
    "header_analysis": {
      "score": 20,
      "findings": [
        "Display name mentions 'banking' but email is from 'secure-banking-alerts.com' (+15)"
      ]
    },
    "sender_reputation": {
      "score": 15,
      "findings": [
        "Generic greeting used: 'dear account holder' (+8)"
      ]
    },
    "content_analysis": {
      "score": 18,
      "findings": [
        "Urgency language: 'unusual activity', 'verify' (+8)"
      ]
    },
    "url_analysis": {
      "score": 22,
      "findings": [
        "URL does not use HTTPS (+10)",
        "Domain uses commonly abused TLD '.info' (+12)"
      ]
    },
    "attachment_analysis": {
      "score": 0
    }
  }
}
```

---

## Example 4: Dangerous Email with Attachment

### Input Email
```
From: "HR Department" <hr@company-hr-services.xyz>
Subject: Update Your Employee Records - URGENT!!!
Attachment: employee_form.exe

Employee Verification Form

Please execute the attached file to update your records urgently.

HR Team
```

### Key Detections
```
ATTACHMENT ANALYSIS:
- Filename: employee_form.exe
- Double extension: YES ✗
- Extension: .exe (CRITICAL) ✗
- Score: 52

CONTENT ANALYSIS:
- Urgency: "URGENT" (multiple !) ✗
- Legitimate concern: generic greeting ✗
- Score: 35

HEADER ANALYSIS:
- Display name "HR Department" from xyz.com ✗
- Suspicious TLD ✗
- Score: 35

URL ANALYSIS:
- No URLs detected
- Score: 0

FINAL SCORE: 76 → DANGEROUS
```

---

## Pattern Recognition Examples

### Content Patterns Detected

**Urgency Patterns:**
```
"act immediately" ✓
"confirm within 24 hours" ✓
"don't delay" ✓
"final warning" ✓
```

**Credential Theft Patterns:**
```
"verify your password" ✓
"confirm credit card" ✓
"otp required" ✓
"bank details needed" ✓
```

**Brand Impersonation Patterns:**
```
Display: "PayPal Support" | Email: random@domain.xyz ✓
"micros0ft.com" (1 char substitution) ✓
"gooogle.com" (double letter) ✓
"paypa1.xyz" (character substitution + wrong TLD) ✓
```

---

## Scoring Interpretation Guide

### Score 0-20: SAFE ✅
**Characteristics:**
- All auth checks pass
- Professional sender
- No suspicious language
- HTTPS URLs only
- No dangerous attachments

**Action:** Safe to interact with

### Score 20-40: LOW RISK ⚠️
**Characteristics:**
- Minor issues found
- Some suspicious patterns
- But not conclusive

**Action:** Verify independently for critical requests

### Score 40-60: SUSPICIOUS 🟠
**Characteristics:**
- Multiple minor issues OR
- One significant issue
- Generic greeting
- Shortened URLs

**Action:** Do NOT click links/download attachments without verification

### Score 60-80: DANGEROUS 🔴
**Characteristics:**
- Multiple serious issues
- Failed authentication
- Executable attachments OR
- Sophisticated brand impersonation

**Action:** DO NOT interact, report to security

### Score 80-100: CRITICAL 🔴🔴
**Characteristics:**
- Clear phishing indicators
- Failed auth + brand spoofing + malware
- Multiple red flags

**Action:** IMMEDIATE ACTION - Report, block, delete

