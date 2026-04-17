import requests
import re
import json
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup


class PhishingDetectorService:
    """Advanced phishing detection service"""
    
    # Phishing keywords commonly found on phishing pages
    PHISHING_KEYWORDS = [
        'confirm', 'verify', 'update', 'secure', 'account',
        'login', 'signin', 'password', 'urgent', 'action',
        'click', 'here', 'validate', 'authentic', 'expire',
        'limited', 'warning', 'alert', 'suspended', 'locked',
        'compromised', 'unusual', 'immediately', 'confirm identity',
        'verify account', 'update payment', 'confirm password',
        'billing', 'credit card', 'bank', 'paypal', 'amazon'
    ]
    
    # Suspicious domain patterns
    SUSPICIOUS_DOMAIN_PATTERNS = [
        r'paypa1\.',  # Letter 'l' instead of '1'
        r'amaz0n\.',  # '0' instead of 'o'
        r'g00gle\.',  # '0' instead of 'o'
        r'fac3book\.',  # '3' instead of 'e'
        r'micr0soft\.',  # '0' instead of 'o'
    ]
    
    # Known phishing domains (simplified)
    KNOWN_PHISHING_DOMAINS = [
        'phishing.com',
        'fake-login.com',
    ]
    
    @staticmethod
    def check_domain_credibility(domain):
        """Check if domain looks suspicious"""
        score = 0
        indicators = []
        
        domain_lower = domain.lower()
        
        # Check for suspicious patterns
        for pattern in PhishingDetectorService.SUSPICIOUS_DOMAIN_PATTERNS:
            if re.search(pattern, domain_lower):
                score += 20
                indicators.append(f"Suspicious domain pattern detected")
        
        # Check if domain length is unusual
        if len(domain) > 50:
            score += 10
            indicators.append("Domain name is unusually long")
        
        # Check for excessive hyphens
        if domain.count('-') > 3:
            score += 15
            indicators.append("Domain has excessive hyphens (typosquatting)")
        
        # Check for IP address in domain
        if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain):
            score += 25
            indicators.append("Domain is an IP address (no proper domain)")
        
        return {
            'score': min(100, score),
            'is_suspicious': score > 30,
            'indicators': indicators
        }
    
    @staticmethod
    def check_ssl_certificate(url):
        """Check SSL certificate validity"""
        score = 0
        indicators = []
        
        # Check if HTTPS is used
        if not url.startswith('https'):
            score += 30
            indicators.append("URL does not use HTTPS (not encrypted)")
        else:
            try:
                response = requests.head(
                    url,
                    timeout=5,
                    verify=True,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                indicators.append("SSL certificate is valid and secure")
            except requests.exceptions.SSLError:
                score += 35
                indicators.append("SSL certificate is invalid or self-signed")
            except:
                pass
        
        return {
            'score': score,
            'indicators': indicators
        }
    
    @staticmethod
    def check_page_content(url):
        """Analyze page content for phishing indicators"""
        score = 0
        indicators = []
        form_fields = 0
        page_title = ""
        phishing_keywords_found = []
        
        try:
            response = requests.get(
                url,
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0'},
                verify=False
            )
            
            if 'text/html' not in response.headers.get('Content-Type', ''):
                return {
                    'score': 0,
                    'indicators': ['Not an HTML page'],
                    'form_fields': 0,
                    'page_title': '',
                    'phishing_keywords': []
                }
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get page title
            if soup.title:
                page_title = soup.title.string[:200] if soup.title.string else ""
            
            # Count forms
            forms = soup.find_all('form')
            form_fields = len(forms)
            
            if form_fields > 0:
                score += 15
                for i, form in enumerate(forms):
                    inputs = form.find_all('input')
                    password_fields = [inp for inp in inputs if inp.get('type') == 'password']
                    
                    if password_fields:
                        score += 10
                        indicators.append(f"Form with password field detected")
            
            # Check for phishing keywords
            page_text = soup.get_text().lower()
            for keyword in PhishingDetectorService.PHISHING_KEYWORDS:
                if keyword.lower() in page_text:
                    phishing_keywords_found.append(keyword)
                    score += 2
            
            if len(phishing_keywords_found) > 5:
                score += 10
                indicators.append(f"Multiple phishing keywords found")
            
            # Check for suspicious meta tags
            meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
            if meta_refresh:
                score += 20
                indicators.append("Page has automatic redirect (meta refresh)")
            
            # Check for basic content
            if len(page_text) < 100:
                score += 10
                indicators.append("Page has minimal content")
        
        except Exception as e:
            indicators.append(f"Could not analyze page: {str(e)[:100]}")
        
        return {
            'score': min(100, score),
            'indicators': indicators,
            'form_fields': form_fields,
            'page_title': page_title,
            'phishing_keywords': phishing_keywords_found
        }
    
    @staticmethod
    def check_url_structure(url):
        """Analyze URL structure for anomalies"""
        score = 0
        indicators = []
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # Check for unusual characters in URL
            if '%' in url:
                score += 10
                indicators.append("URL contains encoded characters")
            
            # Check for @ symbol (credential trick)
            if '@' in domain:
                score += 25
                indicators.append("URL contains @ symbol (credential trick)")
            
            # Check for long URL
            if len(url) > 100:
                score += 5
                indicators.append("URL is unusually long")
            
            # Check query parameters for suspicious values
            if parsed.query:
                params = parse_qs(parsed.query)
                suspicious_params = ['redirect', 'return', 'url', 'target', 'login', 'email']
                for param in suspicious_params:
                    if param in params:
                        score += 5
                        indicators.append(f"Suspicious URL parameter: {param}")
        
        except:
            pass
        
        return {
            'score': score,
            'indicators': indicators
        }
    
    @staticmethod
    def calculate_phishing_score(results):
        """Calculate overall phishing score"""
        total_score = 0
        total_score += results.get('domain_score', 0) * 0.25  # 25% weight
        total_score += results.get('ssl_score', 0) * 0.25    # 25% weight
        total_score += results.get('content_score', 0) * 0.35  # 35% weight
        total_score += results.get('url_score', 0) * 0.15    # 15% weight
        
        return int(min(100, total_score))
    
    @staticmethod
    def determine_risk_level(phishing_score):
        """Determine risk level based on score"""
        if phishing_score >= 80:
            return 'critical'
        elif phishing_score >= 60:
            return 'high'
        elif phishing_score >= 40:
            return 'medium'
        elif phishing_score >= 20:
            return 'low'
        else:
            return 'safe'
    
    @staticmethod
    def detect_phishing(url):
        """Main method to detect phishing"""
        domain = urlparse(url).netloc.lower()
        
        # Perform all checks
        domain_check = PhishingDetectorService.check_domain_credibility(domain)
        ssl_check = PhishingDetectorService.check_ssl_certificate(url)
        content_check = PhishingDetectorService.check_page_content(url)
        url_check = PhishingDetectorService.check_url_structure(url)
        
        # Compile results
        results = {
            'domain_score': domain_check['score'],
            'ssl_score': ssl_check['score'],
            'content_score': content_check['score'],
            'url_score': url_check['score'],
        }
        
        # Calculate overall phishing score
        phishing_score = PhishingDetectorService.calculate_phishing_score(results)
        risk_level = PhishingDetectorService.determine_risk_level(phishing_score)
        
        # Compile all indicators
        all_indicators = []
        for ind in domain_check['indicators']:
            all_indicators.append(f"[Domain] {ind}")
        for ind in ssl_check['indicators']:
            all_indicators.append(f"[SSL] {ind}")
        for ind in content_check['indicators']:
            all_indicators.append(f"[Content] {ind}")
        for ind in url_check['indicators']:
            all_indicators.append(f"[URL] {ind}")
        
        return {
            'url': url,
            'domain': domain,
            'phishing_score': phishing_score,
            'risk_level': risk_level,
            'is_phishing': phishing_score >= 50,
            'indicators': all_indicators,
            'page_title': content_check['page_title'],
            'form_fields': content_check['form_fields'],
            'phishing_keywords': content_check['phishing_keywords'],
            'domain_warnings': domain_check['is_suspicious'],
            'ssl_warnings': ssl_check['score'] > 0,
            'method': 'Advanced Detection Engine'
        }
