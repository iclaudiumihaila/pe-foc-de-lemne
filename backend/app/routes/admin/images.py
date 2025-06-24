"""
Image Upload Routes for Admin Panel

This module provides endpoints for uploading and managing product images.
"""

from flask import request, jsonify, send_from_directory
from app.routes.admin import admin_bp
from app.services.image_service import image_service
from app.utils.auth_middleware import require_admin_auth as admin_required
import os
import logging

logger = logging.getLogger(__name__)

@admin_bp.route('/products/upload-image', methods=['POST'])
@admin_required
def upload_product_image():
    """
    Upload and process product image.
    
    Expects multipart/form-data with 'image' file field.
    
    Returns:
        JSON with image URLs for different sizes
    """
    try:
        # Check if image was provided
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        # Process image
        result = image_service.process_product_image(file)
        
        logger.info(f"Image uploaded successfully: {result['filename']}")
        
        return jsonify({
            'success': True,
            'message': 'Image uploaded successfully',
            'data': {
                'filename': result['filename'],
                'url': result['primary_url'],
                'urls': result['urls'],
                'sizes': result['sizes'],
                'dimensions': result.get('dimensions', {})
            }
        }), 200
        
    except ValueError as e:
        logger.warning(f"Image upload validation error: {str(e)}")
        return jsonify({'error': str(e)}), 400
        
    except Exception as e:
        logger.error(f"Image upload error: {str(e)}")
        return jsonify({'error': 'Failed to upload image'}), 500

@admin_bp.route('/products/upload-images', methods=['POST'])
@admin_required
def upload_multiple_product_images():
    """
    Upload multiple product images at once.
    
    Expects multipart/form-data with multiple 'images' file fields.
    
    Returns:
        JSON with array of image data for each uploaded image
    """
    try:
        # Check if images were provided
        if 'images' not in request.files:
            return jsonify({'error': 'No image files provided'}), 400
        
        files = request.files.getlist('images')
        if not files:
            return jsonify({'error': 'No image files provided'}), 400
        
        # Process each image
        results = []
        errors = []
        
        for i, file in enumerate(files):
            try:
                result = image_service.process_product_image(file)
                results.append({
                    'index': i,
                    'filename': result['filename'],
                    'url': result['primary_url'],
                    'urls': result['urls'],
                    'sizes': result['sizes'],
                    'dimensions': result.get('dimensions', {})
                })
            except Exception as e:
                errors.append({
                    'index': i,
                    'filename': file.filename,
                    'error': str(e)
                })
                logger.error(f"Error processing image {file.filename}: {str(e)}")
        
        # Return results
        response = {
            'success': len(results) > 0,
            'message': f'Uploaded {len(results)} of {len(files)} images successfully',
            'data': {
                'uploaded': results,
                'errors': errors
            }
        }
        
        status_code = 200 if len(errors) == 0 else 207  # 207 Multi-Status
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"Multiple image upload error: {str(e)}")
        return jsonify({'error': 'Failed to upload images'}), 500

@admin_bp.route('/products/delete-image', methods=['DELETE'])
@admin_required
def delete_product_image():
    """
    Delete product image from filesystem.
    
    Expects JSON with image URL or array of URLs.
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'Image URL required'}), 400
        
        # Handle single URL or array of URLs
        urls = data['url'] if isinstance(data['url'], list) else [data['url']]
        
        # Delete images
        image_service.delete_product_images(urls)
        
        return jsonify({
            'success': True,
            'message': f'Deleted {len(urls)} image(s) successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Image deletion error: {str(e)}")
        return jsonify({'error': 'Failed to delete image'}), 500

# Note: In production, you should serve images through Nginx or a CDN
# This endpoint is for development/testing
@admin_bp.route('/uploads/products/<path:filename>')
def serve_product_image(filename):
    """
    Serve product images (development only).
    In production, configure Nginx to serve /uploads directly.
    """
    upload_folder = image_service.UPLOAD_FOLDER
    return send_from_directory(upload_folder, filename)