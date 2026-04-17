#!/usr/bin/env python3
"""
Regenerate blog post featured images with better colors and visibility
"""

import os
import django
from PIL import Image, ImageDraw, ImageFont
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from blog.models import BlogPost

# Define colors (dark backgrounds with contrasting text)
COLORS = [
    {
        'bg': (20, 25, 50),      # Dark blue background
        'primary': (0, 150, 255),  # Cyan text
        'accent': (0, 212, 255),   # Light cyan
        'text': (255, 255, 255),   # White text
    },
    {
        'bg': (30, 15, 50),        # Dark purple background
        'primary': (100, 200, 255), # Light blue
        'accent': (150, 100, 255),  # Purple
        'text': (255, 255, 255),    # White text
    },
    {
        'bg': (20, 40, 30),        # Dark teal background
        'primary': (0, 200, 150),   # Teal
        'accent': (100, 255, 200),  # Light teal
        'text': (255, 255, 255),    # White text
    },
    {
        'bg': (50, 20, 20),        # Dark red background
        'primary': (255, 100, 100), # Light red
        'accent': (255, 150, 150),  # Lighter red
        'text': (255, 255, 255),    # White text
    },
]

media_dir = 'media/blog/featured'
os.makedirs(media_dir, exist_ok=True)

posts = BlogPost.objects.all()
print(f'Regenerating {posts.count()} blog post featured images...\n')

for idx, post in enumerate(posts):
    # Select color scheme
    color = COLORS[idx % len(COLORS)]
    
    # Create image
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color['bg'])
    draw = ImageDraw.Draw(img)
    
    # Try to load a nice font, fallback to default
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Draw decorative circles
    circle_colors = [color['primary'], color['accent']]
    for i in range(3):
        x = random.randint(0, width)
        y = random.randint(0, height)
        r = random.randint(50, 150)
        draw.ellipse(
            [(x-r, y-r), (x+r, y+r)],
            outline=circle_colors[i % 2],
            width=2
        )
    
    # Draw title with word wrapping
    title = post.title
    margin = 40
    y_position = height // 3
    
    # Wrap text
    words = title.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        test_line = ' '.join(current_line)
        bbox = draw.textbbox((0, 0), test_line, font=title_font)
        line_width = bbox[2] - bbox[0]
        if line_width > width - 2 * margin:
            if len(current_line) > 1:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(test_line)
                current_line = []
    if current_line:
        lines.append(' '.join(current_line))
    
    # Draw wrapped title
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        line_width = bbox[2] - bbox[0]
        x = (width - line_width) // 2
        draw.text((x, y_position), line, fill=color['primary'], font=title_font)
        y_position += 60
    
    # Draw subtitle (category or description)
    subtitle = post.category.name if post.category else "Blog Post"
    bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = bbox[2] - bbox[0]
    x = (width - subtitle_width) // 2
    draw.text((x, height - 100), subtitle, fill=color['accent'], font=subtitle_font)
    
    # Save image
    image_path = os.path.join(media_dir, f'{post.slug}.png')
    img.save(image_path)
    print(f'✓ {post.title[:50]}...')
    print(f'  → {image_path}')

print(f'\n✅ Successfully regenerated {posts.count()} featured images!')
print(f'Images saved to: {media_dir}/')
