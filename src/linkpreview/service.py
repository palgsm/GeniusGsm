import requests
import json
import time
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re


class LinkPreviewService:
    """Service for generating link previews"""
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    @staticmethod
    def generate_preview(url):
        """Generate a preview for a given URL"""
        start_time = time.time()
        
        try:
            # Fetch the page
            response = requests.get(
                url,
                timeout=10,
                headers=LinkPreviewService.HEADERS,
                verify=False,
                allow_redirects=True
            )
            
            load_time = time.time() - start_time
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'HTTP Error {response.status_code}',
                    'is_valid': False
                }
            
            # Check content type
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type:
                return {
                    'success': False,
                    'error': 'Not an HTML page',
                    'is_valid': False,
                    'content_type': content_type
                }
            
            # Parse the page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract domain
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            # Extract title
            title = ""
            if soup.title:
                title = soup.title.string
            elif soup.find('meta', attrs={'property': 'og:title'}):
                title = soup.find('meta', attrs={'property': 'og:title'}).get('content', '')
            
            # Extract description
            description = ""
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content', '')
            elif soup.find('meta', attrs={'property': 'og:description'}):
                description = soup.find('meta', attrs={'property': 'og:description'}).get('content', '')
            
            # Extract image
            image_url = ""
            og_image = soup.find('meta', attrs={'property': 'og:image'})
            if og_image:
                image_url = og_image.get('content', '')
            else:
                # Look for first image
                img = soup.find('img')
                if img:
                    img_src = img.get('src', '')
                    if img_src.startswith('http'):
                        image_url = img_src
                    elif img_src.startswith('/'):
                        image_url = f"{parsed_url.scheme}://{domain}{img_src}"
            
            # Extract favicon
            favicon_url = ""
            favicon = soup.find('link', attrs={'rel': 'icon'})
            if favicon:
                favicon_url = favicon.get('href', '')
                if favicon_url and not favicon_url.startswith('http'):
                    if favicon_url.startswith('/'):
                        favicon_url = f"{parsed_url.scheme}://{domain}{favicon_url}"
                    else:
                        favicon_url = f"{parsed_url.scheme}://{domain}/{favicon_url}"
            
            # Extract OG data
            og_data = {}
            for meta in soup.find_all('meta', attrs={'property': True}):
                prop = meta.get('property', '')
                if prop.startswith('og:'):
                    og_data[prop] = meta.get('content', '')
            
            # Extract Twitter Card data
            twitter_data = {}
            for meta in soup.find_all('meta', attrs={'name': True}):
                name = meta.get('name', '')
                if name.startswith('twitter:'):
                    twitter_data[name] = meta.get('content', '')
            
            # Calculate page size
            page_size = len(response.text) / 1024  # KB
            
            # Get dominant color (simple version)
            dominant_color = LinkPreviewService.get_dominant_color(image_url)
            
            return {
                'success': True,
                'url': url,
                'title': title[:500] if title else '',
                'description': description[:1000] if description else '',
                'image_url': image_url,
                'favicon_url': favicon_url,
                'domain': domain,
                'page_size': int(page_size),
                'load_time': round(load_time, 2),
                'content_type': content_type.split(';')[0],
                'og_data': og_data,
                'twitter_data': twitter_data,
                'dominant_color': dominant_color,
                'is_valid': True
            }
        
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Request timeout (page too slow)',
                'is_valid': False
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': 'Connection error (unable to reach server)',
                'is_valid': False
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)[:200],
                'is_valid': False
            }
    
    @staticmethod
    def get_dominant_color(image_url):
        """Get dominant color from image (simplified)"""
        try:
            if not image_url:
                return '#3498db'
            
            # Try to get image and extract color
            response = requests.get(image_url, timeout=5, headers=LinkPreviewService.HEADERS, verify=False)
            if response.status_code == 200:
                # Simple approach: return a color based on image presence
                return '#2980b9'
            else:
                return '#3498db'
        except:
            return '#3498db'
    
    @staticmethod
    def get_preview_summary(preview_data):
        """Get a formatted summary of preview data"""
        return {
            'url': preview_data.get('url', ''),
            'title': preview_data.get('title', 'No title'),
            'description': preview_data.get('description', 'No description available'),
            'image_url': preview_data.get('image_url', ''),
            'favicon_url': preview_data.get('favicon_url', ''),
            'domain': preview_data.get('domain', ''),
            'page_size': preview_data.get('page_size', 0),
            'load_time': preview_data.get('load_time', 0),
            'content_type': preview_data.get('content_type', 'text/html'),
            'og_data': preview_data.get('og_data', {}),
            'twitter_data': preview_data.get('twitter_data', {}),
            'dominant_color': preview_data.get('dominant_color', '#3498db'),
            'is_valid': preview_data.get('is_valid', False),
            'error': preview_data.get('error', '')
        }
