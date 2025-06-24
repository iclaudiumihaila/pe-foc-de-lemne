# Frontend Product Expectations Analysis

## Date: 2025-06-23

## Summary
Analysis of frontend product structure expectations and how products are consumed in the Pe Foc de Lemne React application.

## Expected Product Object Structure in Frontend

### API Response Structure (from backend)
Based on `Products.jsx` line 129-144, the frontend expects this structure from the API:
```javascript
{
  success: true,
  data: {
    products: [
      {
        id: number,
        name: string,
        price: number,
        description: string,
        images: string[],  // Array of image filenames
        category: {
          name: string
        },
        unit: string,
        is_available: boolean,
        stock_quantity: number
      }
    ],
    pagination: {
      total_pages: number,
      total_items: number
    },
    search: {  // Optional
      total_results: number
    }
  }
}
```

### Transformed Product Structure for ProductCard
The `transformProduct` function (lines 57-72) transforms API products to this format:
```javascript
{
  id: number,           // From apiProduct.id
  name: string,         // From apiProduct.name
  price: number,        // From apiProduct.price
  image: string,        // Computed: `/images/${apiProduct.images[0]}` or placeholder
  description: string,  // From apiProduct.description
  category: string,     // From apiProduct.category?.name || 'General'
  unit: string,         // From apiProduct.unit || 'bucată'
  inStock: boolean,     // Computed: is_available !== false && stock_quantity > 0
  stock_quantity: number, // From apiProduct.stock_quantity
  quantity: number      // Default: 1 (for cart operations)
}
```

## Fields Displayed in UI

### ProductCard Component (lines 10-20)
The ProductCard expects and displays:
- `name` - Product title (line 76)
- `price` - Formatted as RON currency (line 90)
- `image` - Product image with fallback (line 42)
- `description` - Product description (line 81)
- `category` - Category badge (line 70)
- `unit` - Price unit indicator (line 94)
- `inStock` - Stock availability status (line 58)
- `isOrganic` - Optional organic badge (line 52)
- `quantity` - For cart operations (line 19)

### Additional UI Elements
- Stock warning when `stock_quantity < 10` (Products.jsx lines 342-346)
- "Stoc epuizat" (Out of stock) badge when `!inStock`
- Add to cart button disabled when out of stock

## Image Handling

### Image Path Construction
1. **API provides**: Array of image filenames (e.g., `["product1.jpg", "product2.jpg"]`)
2. **Frontend transforms**: Takes first image and prepends `/images/` path
3. **Full path**: `/images/${apiProduct.images[0]}`
4. **Fallback**: `/images/placeholder-product.jpg` if no images or on error

### Image Display
- Primary image displayed at 192px height with object-cover (line 44)
- Error handling with fallback to placeholder (lines 45-47)
- Compact view uses 64x64px thumbnail (line 159)

## API Response Transformations

### Key Transformations Applied
1. **Category**: Flattened from object to string
   - API: `category: { name: "Wood" }`
   - Frontend: `category: "Wood"`

2. **Stock Status**: Computed from two fields
   - API: `is_available` + `stock_quantity`
   - Frontend: `inStock = is_available !== false && stock_quantity > 0`

3. **Default Values**:
   - `unit`: Defaults to "bucată" if not provided
   - `category`: Defaults to "General" if not provided
   - `quantity`: Always set to 1 for initial cart operations

4. **Image Path**: 
   - API: Just filename
   - Frontend: Full path with `/images/` prefix

## Cart Integration

### Product Requirements for Cart
When adding to cart, the product must have:
- `id` - Required for identification
- `name` - For display
- `price` - For calculations
- `inStock` - Must be true to add
- `quantity` - Amount to add (default 1)

### Cart Storage Format
Products in cart include additional fields:
- `addedAt` - ISO timestamp when added
- `quantity` - Current quantity in cart

## API Endpoints Used

### Product Listing
- **Endpoint**: `GET /api/products`
- **Query Parameters**:
  - `page` - Page number
  - `limit` - Items per page (default 12)
  - `available_only` - Filter by availability (always "true")
  - `sort_by` - Sort field
  - `sort_order` - Sort direction
  - `q` - Search query (optional)
  - `category_id` - Category filter (optional)

### Categories
- **Endpoint**: `GET /api/categories`
- **Response**: 
  ```javascript
  {
    success: true,
    data: {
      categories: [...]
    }
  }
  ```

## Key Observations

1. **Frontend expects arrays in `images` field** but only uses the first image
2. **Category is expected as a nested object** with `name` property
3. **Stock status is computed** from two separate fields
4. **All prices are in RON** and formatted client-side
5. **Unit defaults to "bucată"** (piece) if not provided
6. **Frontend adds UI-specific fields** like `quantity` for cart operations
7. **Image paths are relative** and require `/images/` prefix
8. **Placeholder handling is robust** with fallbacks at multiple levels