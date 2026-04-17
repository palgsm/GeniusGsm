import requests
import re
import time
from urllib.parse import urlparse


class ShortenerExpanderService:
    """Service for expanding shortened URLs"""
    
    # Common shortener patterns
    SHORTENER_PATTERNS = {
        'bitly': r'bit\.ly|bitly\.com',
        'tinyurl': r'tinyurl\.com|tinyurl\.at',
        'owly': r'ow\.ly',
        'googl': r'goo\.gl',
        'shortlink': r'short\.link|short\.link/',
        'blinkk': r'bl\.ink',
        'rebrantly': r'rebrand\.ly',
        'tinycc': r'tiny\.cc',
        'qrnet': r'qr\.net',
    }
    
    @staticmethod
    def get_shortener_service(url):
        """Detect if URL is from a known shortener service"""
        domain = urlparse(url).netloc.lower()
        for service, pattern in ShortenerExpanderService.SHORTENER_PATTERNS.items():
            if re.search(pattern, domain):
                return service
        return 'unknown'
    
    @staticmethod
    def is_shortened_url(url):
        """Check if URL appears to be shortened"""
        service = ShortenerExpanderService.get_shortener_service(url)
        return service != 'unknown'
    
    @staticmethod
    def expand_url(url):
        """Expand a shortened URL and return the final URL"""
        try:
            start_time = time.time()
            
            response = requests.head(
                url,
                allow_redirects=True,
                timeout=10,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                },
                verify=False
            )
            
            expansion_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
            final_url = response.url
            
            # Get page title
            title = ""
            try:
                content_response = requests.get(
                    final_url,
                    timeout=10,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    },
                    verify=False
                )
                if 'text/html' in content_response.headers.get('Content-Type', ''):
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(content_response.text, 'html.parser')
                    title = soup.title.string if soup.title else ""
            except:
                pass
            
            return {
                'success': True,
                'expanded_url': final_url,
                'title': title[:500] if title else "",
                'expansion_time_ms': expansion_time,
                'is_valid': True
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'expanded_url': url,
                'title': '',
                'expansion_time_ms': 0,
                'is_valid': False,
                'error': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'expanded_url': url,
                'title': '',
                'expansion_time_ms': 0,
                'is_valid': False,
                'error': str(e)
            }
    
    @classmethod
    def expand_with_details(cls, url):
        """Expand URL with complete details"""
        # Check if it's actually a shortened URL
        shortener = cls.get_shortener_service(url)
        is_shortened = cls.is_shortened_url(url)
        
        if not is_shortened:
            return {
                'original_url': url,
                'expanded_url': url,
                'is_shortened': False,
                'shortener_service': None,
                'title': '',
                'expansion_time_ms': 0,
                'error': 'This does not appear to be a shortened URL'
            }
        
        expansion_result = cls.expand_url(url)
        
        return {
            'original_url': url,
            'expanded_url': expansion_result.get('expanded_url', url),
            'is_shortened': True,
            'shortener_service': shortener,
            'title': expansion_result.get('title', ''),
            'expansion_time_ms': expansion_result.get('expansion_time_ms', 0),
            'is_valid': expansion_result.get('is_valid', False),
            'success': expansion_result.get('success', False),
            'error': expansion_result.get('error')
        }
