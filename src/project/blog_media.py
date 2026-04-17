"""
Blog media serving view with proper cache headers
"""

from django.http import FileResponse, Http404
from django.views.decorators.cache import never_cache
from django.views.decorators.http import condition
import os

@never_cache
def serve_blog_image(request, filename):
    """Serve blog featured images with no-cache headers"""
    
    file_path = os.path.join('media/blog/featured', filename)
    
    # Security: ensure file is in the blog/featured directory
    if '..' in file_path or not filename.endswith(('.png', '.jpg', '.jpeg')):
        raise Http404("File not found")
    
    # Check file exists
    if not os.path.exists(file_path):
        raise Http404("File not found")
    
    # Open and serve file
    try:
        response = FileResponse(open(file_path, 'rb'))
        
        # Set content type
        if filename.endswith('.png'):
            response['Content-Type'] = 'image/png'
        elif filename.endswith(('.jpg', '.jpeg')):
            response['Content-Type'] = 'image/jpeg'
        
        # Force no caching
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response
    except IOError:
        raise Http404("File not found")
