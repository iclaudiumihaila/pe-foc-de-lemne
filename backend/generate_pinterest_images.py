#!/usr/bin/env python3
"""
Script to generate Pinterest-size images for existing products.
This processes all existing product images to add the new pinterest size variant.
"""

import os
import sys
from PIL import Image
from datetime import datetime
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.image_service import ImageService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_pinterest_sizes():
    """Generate pinterest size for all existing product images"""
    
    image_service = ImageService()
    upload_folder = image_service.UPLOAD_FOLDER
    pinterest_width = image_service.IMAGE_SIZES['pinterest']
    
    processed_count = 0
    error_count = 0
    
    # Walk through all year/month directories
    for root, dirs, files in os.walk(upload_folder):
        for filename in files:
            # Skip if already a size variant
            if any(size in filename for size in ['_thumb', '_medium', '_large', '_pinterest']):
                continue
                
            # Only process jpg/jpeg files
            if not filename.lower().endswith(('.jpg', '.jpeg')):
                continue
            
            file_path = os.path.join(root, filename)
            
            try:
                # Open original image
                with Image.open(file_path) as img:
                    # Convert to RGB if necessary
                    if img.mode in ('RGBA', 'LA', 'P'):
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = rgb_img
                    
                    # Generate pinterest size
                    resized_img, dims = image_service._resize_image_pinterest(img, pinterest_width)
                    
                    # Save pinterest variant
                    name, ext = os.path.splitext(filename)
                    pinterest_filename = f"{name}_pinterest{ext}"
                    pinterest_path = os.path.join(root, pinterest_filename)
                    
                    resized_img.save(pinterest_path, 'JPEG', quality=image_service.JPEG_QUALITY, optimize=True)
                    
                    logger.info(f"Generated pinterest size for {filename}: {dims['width']}x{dims['height']}")
                    processed_count += 1
                    
            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")
                error_count += 1
    
    logger.info(f"Processing complete. Processed: {processed_count}, Errors: {error_count}")

if __name__ == "__main__":
    generate_pinterest_sizes()