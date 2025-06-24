# Image Handling Documentation - Pe Foc de Lemne

## Overview
This document describes how images are processed, stored, and displayed in the Pe Foc de Lemne e-commerce application.

## Backend Image Processing

### Image Upload Endpoint
- **Location**: `/api/admin/products/upload-image`
- **Handler**: `backend/app/routes/admin/images.py`
- **Service**: `backend/app/services/image_service.py`

### Accepted Formats
- JPG/JPEG
- PNG
- WebP
- **Maximum file size**: 10MB

### Image Processing Pipeline

1. **Validation**
   - File type check (must be jpg, jpeg, png, or webp)
   - File size check (max 10MB)
   - Generates unique filename using timestamp + hash

2. **Size Generation**
   The system automatically generates 4 versions of each uploaded image:
   
   | Size Name | Dimensions | Purpose |
   |-----------|------------|---------|
   | `thumb`   | 150x150    | Thumbnails, admin lists |
   | `medium`  | 600x600    | Product cards, previews |
   | `large`   | 1200x1200  | Product detail pages |
   | `original`| As uploaded| Full resolution backup |

3. **Processing Details**
   - Images are resized to **fit within** the specified dimensions
   - **Aspect ratio is always preserved**
   - If the image doesn't fill the exact square dimensions, it's **centered on a white background**
   - All images are converted to JPEG format with 85% quality
   - Uses PIL (Pillow) library with LANCZOS resampling for high quality

4. **Storage Structure**
   ```
   uploads/products/
   └── 2024/
       └── 01/
           ├── 20240115120000_abc123.jpg (original)
           ├── 20240115120000_abc123_thumb.jpg
           ├── 20240115120000_abc123_medium.jpg
           └── 20240115120000_abc123_large.jpg
   ```

## Frontend Display

### Product Card Display
- **Component**: `frontend/src/components/product/ProductCard.jsx`
- Uses **variable heights** for Pinterest-style masonry layout
- Heights randomly selected from: `h-32`, `h-40`, `h-48`, `h-56`, `h-64` (Tailwind classes)
- These translate to: 128px, 160px, 192px, 224px, 256px

### Image Display Properties
- **CSS Property**: `object-cover`
- This **crops images to fill** the container while maintaining aspect ratio
- Cropping is automatic and centers on the middle of the image
- No specific aspect ratio is enforced

### Responsive Grid Layout
- **Mobile (default)**: 2 columns
- **Small screens (640px+)**: 3 columns
- **Desktop (1024px+)**: 4 columns
- **Large screens (1280px+)**: 5 columns
- Column gap increases with screen size (8px → 12px → 16px)

### Image Loading
- Uses `loading="lazy"` for performance
- Fallback to placeholder image on error
- Image URL helper: `frontend/src/utils/imageUrl.js`

## Key Observations

### Current Limitations
1. **Square containers only** - Backend creates square versions regardless of original aspect ratio
2. **No smart cropping** - Images are center-cropped, which may cut off important parts
3. **White background fill** - Non-square images get white padding instead of maintaining original ratio
4. **Random heights** - Frontend uses random heights for visual variety, not based on actual image dimensions

### Aspect Ratio Behavior
- **No specific aspect ratio is enforced**
- Backend preserves aspect ratio but fits into square containers
- Frontend crops images to fit variable-height containers
- Original aspect ratios are lost in the display process

## Recommendations for Improvement

1. **Aspect Ratio Preservation**
   - Consider generating responsive sizes that maintain original aspect ratios
   - Store image dimensions in database for proper container sizing

2. **Smart Cropping**
   - Implement focal point detection for better cropping
   - Allow manual crop adjustment in admin panel

3. **Performance Optimization**
   - Add WebP format generation for modern browsers
   - Implement responsive images with `srcset` and `sizes` attributes
   - Consider lazy-loading with intersection observer

4. **Pinterest-Style Enhancement**
   - Calculate actual image heights for true masonry layout
   - Avoid random heights - use actual image proportions

5. **Image Quality**
   - Consider different quality settings for different sizes
   - Implement progressive JPEG encoding

## Example Upload Response
```json
{
  "success": true,
  "message": "Image uploaded successfully",
  "data": {
    "filename": "20240115120000_abc123.jpg",
    "url": "/uploads/products/2024/01/20240115120000_abc123_large.jpg",
    "urls": {
      "thumb": "/uploads/products/2024/01/20240115120000_abc123_thumb.jpg",
      "medium": "/uploads/products/2024/01/20240115120000_abc123_medium.jpg",
      "large": "/uploads/products/2024/01/20240115120000_abc123_large.jpg",
      "original": "/uploads/products/2024/01/20240115120000_abc123.jpg"
    },
    "sizes": {
      "thumb": "/uploads/products/2024/01/20240115120000_abc123_thumb.jpg",
      "medium": "/uploads/products/2024/01/20240115120000_abc123_medium.jpg",
      "large": "/uploads/products/2024/01/20240115120000_abc123_large.jpg",
      "original": "/uploads/products/2024/01/20240115120000_abc123.jpg"
    }
  }
}
```

## Admin Panel Behavior
- Multiple images can be uploaded per product (up to 10)
- First image is the primary/default image
- Images can be reordered by setting a different primary
- Drag-and-drop upload interface
- Real-time upload with progress indication

---

*Last updated: January 2024*