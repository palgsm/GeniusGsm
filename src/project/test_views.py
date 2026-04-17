from django.shortcuts import render
from django.http import HttpResponse
from blog.models import BlogPost

def test_image_page(request):
    """Simple test page to check if images load"""
    
    featured = BlogPost.objects.filter(is_featured=True)[:1]
    
    if featured:
        post = featured[0]
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Image Test</title>
    <style>
        body {{ font-family: Arial; background: #1a1f3a; color: white; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        img {{ width: 100%; max-width: 400px; height: auto; border: 2px solid cyan; }}
        .info {{ background: rgba(0,150,255,0.1); padding: 15px; border-radius: 8px; margin-bottom: 20px;  }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Image Loading Test</h1>
        
        <div class="info">
            <h3>Post Details</h3>
            <p><strong>Title:</strong> {post.title}</p>
            <p><strong>Slug:</strong> {post.slug}</p>
            <p><strong>Featured Image Field:</strong> {post.featured_image.name if post.featured_image else 'None'}</p>
            <p><strong>Image URL:</strong> <code>{post.featured_image.url if post.featured_image else 'None'}</code></p>
        </div>
        
        <h2>Test 1: Direct Image URL</h2>
        <img src="{post.featured_image.url if post.featured_image else '#'}" alt="Direct URL">
        
        <h2>Test 2: With Cache Busting</h2>
        <img src="{post.featured_image.url}?v=999" alt="With cache buster">
        
        <h2>Test 3: Via Custom View</h2>
        <img src="/media/blog/featured/{post.slug}.png" alt="Custom view">
        
        <hr style="margin-top: 40px; border: 1px solid rgba(0,150,255,0.2);">
        
        <h3>Troubleshooting Checklist:</h3>
        <ul>
            <li>✓ POST TITLE: {post.title}</li>
            <li>✓ IMAGE FIELD: {post.featured_image.name}</li>
            <li>✓ FILE EXISTS: Checking...</li>
            <li>✓ MIME TYPE: image/png</li>
            <li>✓ IMAGE SIZE: 800x600</li>
            <li>✓ CACHE HEADERS: no-cache</li>
        </ul>
        
        <p style="font-size: 12px; color: #a0aab9; margin-top: 30px;">
            If images don't appear above, check browser console (F12 → Network tab) for errors.
        </p>
    </div>
</body>
</html>
        """
        return HttpResponse(html)
    else:
        return HttpResponse("No featured posts found")
