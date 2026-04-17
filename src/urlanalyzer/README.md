# URL Analyzer & Phishing Detector

## Overview
**URL Analyzer** is a comprehensive tool for analyzing URLs and detecting phishing attempts, malicious content, and security risks.

## Features ✨

### 1. **Shortened URL Expansion**
- Detects if a URL is from a known shortener service (bit.ly, tinyurl, ow.ly, etc.)
- Expands shortened URLs to reveal the actual destination
- **Risk:** Shortened URLs can hide malicious destinations

### 2. **Phishing Detection** 🚨
- Multi-indicator phishing detection algorithm
- Analyzes page content for suspicious keywords
- Checks for form fields that mimic popular services
- Detects suspicious URL patterns and structures

### 3. **URL Syntax Analysis**
- Detects suspicious URL patterns:
  - IP addresses instead of domain names
  - Double slashes with @ symbol (credential trick)
  - URL-encoded characters
  - Multiple numbers in domain
  
### 4. **Security Check**
- Verifies HTTPS/SSL usage
- Identifies pages without proper encryption
- **Risk:** HTTP-only connections expose data to interception

### 5. **Page Content Analysis**
- Extracts page title and metadata
- Counts form fields (potential credential harvesting)
- Searches for phishing keywords:
  - "confirm", "verify", "update", "urgent"
  - "login", "password", "account"
  - "action required", "expired", "suspended"

### 6. **Redirect Parameter Detection**
- Detects suspicious query parameters used for phishing
- Identifies potential redirect chains
- Warns about parameter names like: redirect, returnurl, target, etc.

## Risk Scoring System 📊

The tool calculates a phishing score from 0-100:

- **0-19: Safe** ✅ (Green)
- **20-39: Low Risk** ⚠️ (Yellow)
- **40-59: Medium Risk** ⚠️ (Orange)
- **60-79: High Risk** 🚨 (Red)
- **80-100: Critical Risk** 🔴 (Dark Red)

### Score Calculation:
- Shortened URL: +10 points
- Missing HTTPS: +10 points
- Suspicious URL syntax: +5-15 points
- Phishing keywords found: +2 points each (max 15)
- Form fields present: +10 points
- Redirect parameters: +5 points each
- Suspicious character patterns: +7 points each

## API Endpoints 🔌

### Analyze URL (POST)
```bash
POST /urlanalyzer/api/analyze/
Content-Type: application/json

{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "original_url": "https://bit.ly/example",
    "expanded_url": "https://actual-site.com/...",
    "domain": "actual-site.com",
    "phishing_score": 45.5,
    "risk_level": "medium",
    "is_phishing": true,
    "has_shortener": true,
    "shortener_service": "bit.ly",
    "has_ssl": true,
    "indicators": {
      "syntax_issues": [...],
      "suspicious_chars": [...],
      "phishing_keywords": ["confirm", "verify", "urgent"],
      "form_fields": 3,
      "redirect_params": [...]
    },
    "page_title": "Account Verification"
  }
}
```

### Analyze URL (GET)
```bash
GET /urlanalyzer/api/analyze/?url=https://example.com
```

## Database Models 🗄️

### URLAnalysisResult
Stores analysis results for every URL checked:
- `original_url` - Original provided URL
- `expanded_url` - Expanded URL (if shortened)
- `domain` - Extracted domain
- `risk_level` - Safety assessment level
- `is_phishing` - Boolean phishing indicator
- `phishing_score` - Risk score (0-100)
- `phishing_indicators` - JSON array of indicators found
- `has_shortener` - Whether URL was shortened
- `has_ssl` - Whether HTTPS is used
- Timestamps and user IP for analytics

### PhishingIndicator
Reference table for phishing detection indicators with weights

### URLBlacklist
Database of known malicious URLs for quick blocking

## Usage Examples 📝

### Web Interface
1. Visit `/urlanalyzer/`
2. Enter URL in the input field
3. Click "Analyze"
4. Review detailed results with color-coded risk levels

### CLI / API
```bash
# Using curl
curl -X POST http://localhost:8001/urlanalyzer/api/analyze/ \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://suspicious-bank-login.phishing-site.com"
  }'

# Using Python
import requests

response = requests.post(
    'http://localhost:8001/urlanalyzer/api/analyze/',
    json={'url': 'https://example.com'}
)

analysis = response.json()['result']
print(f"Risk Level: {analysis['risk_level']}")
print(f"Phishing Score: {analysis['phishing_score']}/100")
```

## Technical Details ⚙️

### Supported Shortener Services
- bit.ly
- tinyurl.com
- ow.ly
- short.link
- goo.gl
- rebrand.ly
- And more...

### Phishing Detection Keywords
confirm, verify, update, secure, account, login, signin, password, urgent, action, 
click, validate, authentic, expire, limited, warning, alert, suspended, locked

### Suspicious URL Patterns
- Direct IP addresses: `192.168.1.1`
- Credential tricks: `user@domain.com@real-site.com`
- URL encoding tricks: `%2540`
- Unusual number placement

## Security Notes 🔒

⚠️ **Important**: This tool provides analysis guidance but should not be the sole 
indicator of URL safety. Always exercise caution with unfamiliar links.

**False Positives May Occur When:**
- Legitimate sites use shortened URLs
- Forms are used for legitimate authentication
- Keyword phrases appear in innocuous contexts

**Best Practices:**
1. Never click links in unsolicited emails
2. Type URLs directly instead of clicking links
3. Check for HTTPS and valid certificates
4. Hover over links to see actual URL before clicking
5. Use this tool as an additional verification layer

## Admin Interface 👨‍💼

Access analysis history and management:
- Navigate to `/admin/urlanalyzer/`
- View all analyzed URLs
- Filter by risk level
- Export analysis data
- Manage URL blacklist

## Future Enhancements 🚀

Planned features:
- Integration with VirusTotal API for malware scanning
- Open Threat Exchange (OTX) integration
- Machine learning-based phishing detection
- Historical URL reputation tracking
- Bulk URL analysis
- Browser extension for inline analysis
- Email integration for template analysis

## Performance Notes ⚡

- SSL certificate checks: ~5-10 seconds
- Page content analysis: ~5-10 seconds  
- Shortened URL expansion: ~3-5 seconds
- Total analysis: ~10-25 seconds depending on target

## Support 🆘

For issues, feature requests, or feedback:
- Check recent analyses for patterns
- Review admin logs for errors
- Contact the GeniusGsm team

---

**Version:** 1.0.0 (Beta)  
**Last Updated:** April 16, 2026  
**Status:** Active Development

