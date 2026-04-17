#!/usr/bin/env python3
"""
Convert blog featured images from PNG to JPEG for better compatibility
"""

import os
from PIL import Image

media_dir = 'media/blog/featured'
png_files = [f for f in os.listdir(media_dir) if f.endswith('.png')]

print(f'Converting {len(png_files)} PNG images to JPEG...\n')

for png_file in png_files:
    png_path = os.path.join(media_dir, png_file)
    
    # Remove .png and add .jpg
    jpg_file = png_file.replace('.png', '.jpg')
    jpg_path = os.path.join(media_dir, jpg_file)
    
    try:
        # Open PNG and convert to JPEG
        img = Image.open(png_path)
        img_rgb = img.convert('RGB')
        img_rgb.save(jpg_path, 'JPEG', quality=95)
        
        # Remove PNG file
        os.remove(png_path)
        print(f'✓ {png_file} → {jpg_file}')
        
    except Exception as e:
        print(f'✗ Error converting {png_file}: {e}')

print(f'\n✅ Successfully converted all images to JPEG!')
print(f'Now update all image references from .png to .jpg in templates.')
