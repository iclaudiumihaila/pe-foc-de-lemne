"""
Image Service for Product Image Management

This service handles image upload, processing, and storage for product images.
Uses local filesystem storage with multiple size generation and optimization.
"""

import os
import hashlib
from datetime import datetime
from PIL import Image
from werkzeug.utils import secure_filename
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class ImageService:
    """Service for handling product image uploads and processing"""
    
    # Configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads', 'products')
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Image sizes configuration
    IMAGE_SIZES = {
        'thumb': (150, 150),
        'medium': (600, 600),
        'large': (1200, 1200),
        'pinterest': 300  # Width constraint only, height preserved
    }
    
    # Quality settings
    JPEG_QUALITY = 85
    PNG_COMPRESS_LEVEL = 6
    
    def __init__(self):
        """Initialize image service and ensure upload directories exist"""
        self._ensure_upload_directories()
    
    def _ensure_upload_directories(self):
        """Create upload directories if they don't exist"""
        if not os.path.exists(self.UPLOAD_FOLDER):
            os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
            logger.info(f"Created upload directory: {self.UPLOAD_FOLDER}")
    
    def allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    def validate_file_size(self, file) -> bool:
        """Validate file size is within limits"""
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)  # Reset file pointer
        return size <= self.MAX_FILE_SIZE
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """Generate unique filename using timestamp and hash"""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        name, ext = os.path.splitext(secure_filename(original_filename))
        
        # Create hash of original name + timestamp for uniqueness
        hash_input = f"{name}{timestamp}".encode('utf-8')
        file_hash = hashlib.md5(hash_input).hexdigest()[:8]
        
        return f"{timestamp}_{file_hash}{ext.lower()}"
    
    def get_file_path(self, filename: str, size: str = None) -> str:
        """Get full file path for given filename and size"""
        # Organize by year/month
        now = datetime.utcnow()
        year_month = now.strftime('%Y/%m')
        
        if size:
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{size}{ext}"
        
        return os.path.join(self.UPLOAD_FOLDER, year_month, filename)
    
    def get_url_path(self, filename: str, size: str = None) -> str:
        """Get URL path for given filename and size"""
        now = datetime.utcnow()
        year_month = now.strftime('%Y/%m')
        
        if size:
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{size}{ext}"
        
        return f"/uploads/products/{year_month}/{filename}"
    
    def process_image(self, file, filename: str) -> Dict[str, str]:
        """
        Process uploaded image: validate, resize, optimize, and save.
        
        Args:
            file: Uploaded file object
            filename: Unique filename for the image
            
        Returns:
            Dictionary of URLs for different image sizes
        """
        urls = {}
        
        try:
            # Open and validate image
            img = Image.open(file)
            
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            
            # Ensure directory exists for current year/month
            year_month_dir = os.path.join(self.UPLOAD_FOLDER, datetime.utcnow().strftime('%Y/%m'))
            os.makedirs(year_month_dir, exist_ok=True)
            
            # Save original image
            original_path = self.get_file_path(filename)
            img.save(original_path, 'JPEG', quality=self.JPEG_QUALITY, optimize=True)
            urls['original'] = self.get_url_path(filename)
            
            # Generate different sizes
            dimensions_info = {}
            for size_name, dimensions in self.IMAGE_SIZES.items():
                if size_name == 'pinterest':
                    # Special handling for pinterest size
                    resized_img, dims = self._resize_image_pinterest(img.copy(), dimensions)
                    dimensions_info[size_name] = dims
                else:
                    # Standard square resize
                    resized_img = self._resize_image(img.copy(), dimensions)
                
                size_path = self.get_file_path(filename, size_name)
                resized_img.save(size_path, 'JPEG', quality=self.JPEG_QUALITY, optimize=True)
                urls[size_name] = self.get_url_path(filename, size_name)
            
            logger.info(f"Successfully processed image: {filename}")
            return {
                'urls': urls,
                'dimensions': dimensions_info
            }
            
        except Exception as e:
            logger.error(f"Error processing image {filename}: {str(e)}")
            # Clean up any partially saved files
            self._cleanup_failed_upload(filename)
            raise
    
    def _resize_image_pinterest(self, img: Image.Image, max_width: int) -> Tuple[Image.Image, Dict[str, int]]:
        """
        Resize image for Pinterest layout - constrain width, preserve aspect ratio.
        
        Args:
            img: PIL Image object
            max_width: Maximum width constraint
            
        Returns:
            Tuple of (resized image, dimensions dict)
        """
        # Calculate new dimensions maintaining aspect ratio
        aspect_ratio = img.height / img.width
        new_width = min(img.width, max_width)
        new_height = int(new_width * aspect_ratio)
        
        # Resize image with high quality
        if img.width != new_width:
            resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        else:
            resized = img
        
        return resized, {'width': new_width, 'height': new_height}
    
    def _resize_image(self, img: Image.Image, size: Tuple[int, int]) -> Image.Image:
        """
        Resize image maintaining aspect ratio, fitting within given dimensions.
        
        Args:
            img: PIL Image object
            size: Tuple of (width, height) maximum dimensions
            
        Returns:
            Resized PIL Image object
        """
        # Calculate aspect ratio
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Create new image with white background if needed
        if img.size != size:
            new_img = Image.new('RGB', size, (255, 255, 255))
            # Paste resized image centered
            x = (size[0] - img.size[0]) // 2
            y = (size[1] - img.size[1]) // 2
            new_img.paste(img, (x, y))
            return new_img
        
        return img
    
    def _cleanup_failed_upload(self, filename: str):
        """Remove any files created during failed upload"""
        for size in ['', 'thumb', 'medium', 'large', 'pinterest']:
            try:
                file_path = self.get_file_path(filename, size if size else None)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Cleaned up failed upload: {file_path}")
            except Exception as e:
                logger.error(f"Error cleaning up file {file_path}: {str(e)}")
    
    def delete_product_images(self, image_urls: List[str]):
        """
        Delete product images from filesystem.
        
        Args:
            image_urls: List of image URLs to delete
        """
        for url in image_urls:
            try:
                # Convert URL to filesystem path
                if url.startswith('/uploads/products/'):
                    relative_path = url.replace('/uploads/products/', '')
                    file_path = os.path.join(self.UPLOAD_FOLDER, relative_path)
                    
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f"Deleted image: {file_path}")
                        
            except Exception as e:
                logger.error(f"Error deleting image {url}: {str(e)}")
    
    def process_product_image(self, file) -> Dict[str, any]:
        """
        Main method to process product image upload.
        
        Args:
            file: Uploaded file from request.files
            
        Returns:
            Dictionary with image URLs and metadata
        """
        # Validate file
        if not file or file.filename == '':
            raise ValueError("No file provided")
        
        if not self.allowed_file(file.filename):
            raise ValueError(f"File type not allowed. Allowed types: {', '.join(self.ALLOWED_EXTENSIONS)}")
        
        if not self.validate_file_size(file):
            raise ValueError(f"File size exceeds maximum allowed size of {self.MAX_FILE_SIZE / 1024 / 1024}MB")
        
        # Generate unique filename
        filename = self.generate_unique_filename(file.filename)
        
        # Process and save image
        result = self.process_image(file, filename)
        urls = result['urls']
        dimensions = result.get('dimensions', {})
        
        # Return image data
        return {
            'filename': filename,
            'urls': urls,
            'primary_url': urls.get('large', urls.get('original')),
            'sizes': {
                'thumb': urls.get('thumb'),
                'medium': urls.get('medium'),
                'large': urls.get('large'),
                'original': urls.get('original'),
                'pinterest': urls.get('pinterest')
            },
            'dimensions': dimensions
        }

# Create singleton instance
image_service = ImageService()