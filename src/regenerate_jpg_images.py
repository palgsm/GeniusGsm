#!/usr/bin/env python3
"""
Regenerate blog featured images as JPG with bright, visible colors
"""

import os
import django
from PIL import Image, ImageDraw, ImageFont

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from blog.models import BlogPost

# Bright, high-contrast color schemes
COLORS = [
    {
        'bg': (255, 140, 0),       # Orange background
        'primary': (255, 255, 255), # White text
        'accent': (0, 0, 0),        # Black accents
    },
    {
        'bg': (0, 150, 255),        # Bright cyan
        'primary': (255, 255, 255), # White text
        'accent': (0, 0, 0),        # Black
    },
    {
        'bg': (76, 175, 80),        # Green
        'primary': (255, 255, 255), # White
        'accent': (0, 0, 0),
    },
    {
        'bg': (244, 67, 54),        # Red
        'primary': (255, 255, 255), # White
        'accent': (0, 0, 0),
    },
    {
        'bg': (156, 39, 176),       # Purple
        'primary': (255, 255, 255), # White
        'accent': (255, 255, 255),
    },
    {
        'bg': (33, 150, 243),       # Blue
        'primary': (255, 255, 255), # White
        'accent': (0, 0, 0),
    },
]

media_dir = 'media/blog/featured'
os.makedirs(media_dir, exist_ok=True)

posts = BlogPost.objects.all()
print(f'Regenerating {posts.count()} blog images as JPG with bright colors...\n')

for idx, post in enumerate(posts):
    color = COLORS[idx % len(COLORS)]
    
    # Create bright image
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color['bg'])
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Draw large, bold text in center
    title = post.title
    
    # Wrap text
    words = title.split()
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        test_line = ' '.join(current_line)
        bbox = draw.textbbox((0, 0), test_line, font=title_font)
        line_width = bbox[2] - bbox[0]
        
        if line_width > width - 60:
            if len(current_line) > 1:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(test_line)
                current_line = []
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Draw title centered
    y = height // 3
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        line_width = bbox[2] - bbox[0]
        x = (width - line_width) // 2
        draw.text((x, y), line, fill=color['primary'], font=title_font)
        y += 70
    
    # Draw category at bottom
    subtitle = post.category.name if post.category else "Blog"
    bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = bbox[2] - bbox[0]
    x = (width - subtitle_width) // 2
    draw.text((x, height - 120), subtitle, fill=color['accent'], font=subtitle_font)
    
    # Save as JPG
    jpg_path = os.path.join(media_dir, f'{post.slug}.jpg')
    img.save(jpg_path, 'JPEG', quality=95)
    
    # Delete old PNG if exists
    png_path = os.path.join(media_dir, f'{post.slug}.png')
    if os.path.exists(png_path):
        os.remove(png_path)
    
    print(f'✓ {post.title[:45]}...')
    print(f'  → {jpg_path}')

# Now update database to use JPG instead of PNG
print('\nUpdating database to use JPG images...\n')

for post in BlogPost.objects.all():
    if post.featured_image:
        old_name = post.featured_image.name
        if old_name.endswith('.png'):
            new_name = old_name.replace('.png', '.jpg')
            post.featured_image.name = new_name
            post.save()
            print(f'✓ Updated: {post.slug}')

print(f'\n✅ Successfully regenerated all images as JPG!')
print(f'All images are now bright and highly visible!')
