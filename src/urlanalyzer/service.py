import requests
import re
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import validators
from datetime import datetime, timedelta


class URLAnalyzerService:
    """Service for analyzing URLs and detecting phishing"""
    
    # Common phishing shortener services
    SHORTENER_PATTERNS = {
        'bit.ly': r'bit\.ly',
        'tinyurl': r'tinyurl\.com',
        'ow.ly': r'ow\.ly',
        'short.link': r'short\.link',
        'goo.gl': r'goo\.gl',
        'bl.ink': r'bl\.ink',
        'ifttt.com': r'ifttt\.com',
        'rebrand.ly': r'rebrand\.ly',
        'tiny.cc': r'tiny\.cc',
        'qr.net': r'qr\.net',
    }
    
    # Suspicious URL patterns
    SUSPICIOUS_PATTERNS = [
        (r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', 'IP address used instead of domain'),
        (r'[@]//', 'Double slash with @ symbol (credential trick)'),
        (r'[\w]+%[@]', 'URL encoded @ symbol'),
        (r'https?://[^/]*\d{1,3}[^/]*\d{1,3}[^/]*\d{1,3}', 'Multiple numbers in domain'),
    ]
    
    # Phishing keywords
    PHISHING_KEYWORDS = [
        'confirm', 'verify', 'update', 'secure', 'account',
        'login', 'signin', 'password', 'urgent', 'action',
        'click', 'here', 'validate', 'authentic', 'expire',
        'limited', 'warning', 'alert', 'suspended', 'locked'
    ]
    
    # Suspicious query parameters
    SUSPICIOUS_PARAMS = [
        'redirect', 'return', 'returnurl', 'url', 'target',
        'destination', 'back', 'forward', 'next', 'continue'
    ]
    
    @staticmethod
    def expand_short_url(url):
        """Expand shortened URLs"""
        try:
            response = requests.head(
                url,
                allow_redirects=True,
                timeout=5,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            return response.url if response.history else url
        except:
            return url
    
    @staticmethod
    def get_shortener_service(url):
        """Detect if URL is from a known shortener service"""
        domain = urlparse(url).netloc.lower()
        for service, pattern in URLAnalyzerService.SHORTENER_PATTERNS.items():
            if re.search(pattern, domain):
                return service
        return None
    
    @staticmethod
    def check_domain_age(domain):
        """Check domain age in days (simplified)"""
        try:
            # This is a simplified version - real implementation would use WHOIS
            # For now, return None to indicate we can't determine
            return None
        except:
            return None
    
    @staticmethod
    def analyze_url_syntax(url):
        """Analyze URL for suspicious syntax patterns"""
        indicators = {
            'suspicious_chars': [],
            'suspicious_patterns': [],
            'phishing_score_addition': 0
        }
        
        # Check for suspicious characters/patterns
        for pattern, description in URLAnalyzerService.SUSPICIOUS_PATTERNS:
            if re.search(pattern, url):
                indicators['suspicious_patterns'].append(description)
                indicators['phishing_score_addition'] += 15
        
        # Check for unusual characters
        if '%' in url and '//' in url:
            indicators['suspicious_chars'].append('URL encoding detected')
        
        if '\\' in url:
            indicators['suspicious_chars'].append('Backslashes in URL')
            indicators['phishing_score_addition'] += 10
        
        return indicators
    
    @staticmethod
    def analyze_page_content(url):
        """Analyze page content for phishing indicators"""
        try:
            response = requests.get(
                url,
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0'},
                allow_redirects=True,
                verify=False
            )
            
            # Check if we got HTML
            if 'text/html' not in response.headers.get('Content-Type', ''):
                return {'title': '', 'phishing_keywords': [], 'forms': 0}
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get title
            title = soup.title.string if soup.title else ''
            
            # Count forms
            forms = len(soup.find_all('form'))
            
            # Check for phishing keywords
            page_text = soup.get_text().lower()
            found_keywords = []
            for keyword in URLAnalyzerService.PHISHING_KEYWORDS:
                if keyword in page_text:
                    found_keywords.append(keyword)
            
            return {
                'title': str(title)[:500] if title else '',
                'phishing_keywords': found_keywords,
                'forms': forms
            }
        except:
            return {'title': '', 'phishing_keywords': [], 'forms': 0}
    
    @staticmethod
    def check_https(url):
        """Check if URL uses HTTPS"""
        return url.startswith('https://')
    
    @staticmethod
    def extract_domain(url):
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path.split('/')[0]
            return domain.lower()
        except:
            return ''
    
    @staticmethod
    def check_redirect_urls(url):
        """Check for suspicious redirect parameters"""
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query.lower())
            
            suspicious_redirects = []
            for param_name in URLAnalyzerService.SUSPICIOUS_PARAMS:
                if param_name in params:
                    redirect_target = params[param_name][0]
                    # Check if redirect target seems suspicious
                    if redirect_target.startswith('http'):
                        suspicious_redirects.append({
                            'param': param_name,
                            'target': redirect_target
                        })
            
            return suspicious_redirects
        except:
            return []
    
    @staticmethod
    def calculate_phishing_score(analysis_data):
        """Calculate phishing score based on analysis data"""
        score = 0
        
        # URL syntax indicators (0-20 points)
        if analysis_data.get('has_shortener'):
            score += 10
        
        score += min(20, analysis_data.get('syntax_indicators', {}).get('phishing_score_addition', 0))
        
        # HTTPS check (0-10 points)
        if not analysis_data.get('has_ssl'):
            score += 10
        
        # Phishing keywords (0-15 points)
        keyword_count = len(analysis_data.get('phishing_keywords', []))
        score += min(15, keyword_count * 2)
        
        # Forms on page (0-15 points)
        if analysis_data.get('forms', 0) > 0:
            score += 10
        
        # Redirect parameters (0-15 points)
        if analysis_data.get('suspicious_redirects'):
            score += min(15, len(analysis_data['suspicious_redirects']) * 5)
        
        # Suspicious patterns (0-15 points)
        pattern_count = len(analysis_data.get('suspicious_patterns', []))
        score += min(15, pattern_count * 7)
        
        return min(100, score)  # Cap at 100
    
    @staticmethod
    def determine_risk_level(phishing_score):
        """Determine risk level based on phishing score"""
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
    
    @classmethod
    def analyze_url(cls, url):
        """Main method to analyze URL"""
        
        # Validate URL format
        if not validators.url(url):
            return {
                'error': 'Invalid URL format',
                'is_valid': False
            }
        
        # Extract domain
        domain = cls.extract_domain(url)
        
        # Check for shortener
        shortener_service = cls.get_shortener_service(url)
        expanded_url = url
        
        if shortener_service:
            expanded_url = cls.expand_short_url(url)
        
        # URL syntax analysis
        syntax_indicators = cls.analyze_url_syntax(url)
        
        # HTTPS check
        has_ssl = cls.check_https(url)
        
        # Redirect analysis
        suspicious_redirects = cls.check_redirect_urls(url)
        
        # Page content analysis (try expanded URL if shortened)
        content_analysis = cls.analyze_page_content(expanded_url or url)
        
        # Compile analysis data
        analysis_data = {
            'has_shortener': bool(shortener_service),
            'shortener_service': shortener_service,
            'has_ssl': has_ssl,
            'syntax_indicators': syntax_indicators,
            'suspicious_redirects': suspicious_redirects,
            'phishing_keywords': content_analysis.get('phishing_keywords', []),
            'forms': content_analysis.get('forms', 0),
            'suspicious_patterns': syntax_indicators.get('suspicious_patterns', []),
        }
        
        # Calculate scores
        phishing_score = cls.calculate_phishing_score(analysis_data)
        risk_level = cls.determine_risk_level(phishing_score)
        
        # Compile final report
        report = {
            'is_valid': True,
            'original_url': url,
            'expanded_url': expanded_url if expanded_url != url else None,
            'domain': domain,
            'has_shortener': bool(shortener_service),
            'shortener_service': shortener_service,
            'has_ssl': has_ssl,
            'phishing_score': phishing_score,
            'risk_level': risk_level,
            'is_phishing': phishing_score >= 40,  # Consider 40+ as phishing
            'indicators': {
                'syntax_issues': syntax_indicators.get('suspicious_patterns', []),
                'suspicious_chars': syntax_indicators.get('suspicious_chars', []),
                'phishing_keywords': content_analysis.get('phishing_keywords', []),
                'form_fields': content_analysis.get('forms', 0),
                'redirect_params': suspicious_redirects,
            },
            'page_title': content_analysis.get('title', ''),
        }
        
        return report
