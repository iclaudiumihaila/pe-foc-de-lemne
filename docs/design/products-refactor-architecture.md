# Products Page Refactor Architecture

## Overview
Refactor Products.jsx to use the existing ProductCard component for consistency and to enable add-to-cart animations.

## Current State
- Products.jsx renders inline product cards (lines 304-369)
- Duplicate code for product display logic
- No animation support for add-to-cart

## Target State
- Products.jsx uses ProductCard component
- Consistent product display across the app
- Add-to-cart animations work everywhere
- Single source of truth for product card UI

## Technical Design

### 1. Component Integration
- Import ProductCard from components/product/ProductCard.jsx
- Replace inline product rendering with ProductCard
- Map product data to ProductCard props format

### 2. Data Transformation
Products API returns:
```javascript
{
  id: string,  // Note: API returns 'id' not '_id'
  name: string,
  price: number,
  images: string[],
  description: string,
  category: { name: string },
  stock_quantity: number,
  is_available: boolean,
  unit: string
}
```

ProductCard expects a single product prop:
```javascript
<ProductCard 
  product={{
    id: string,
    name: string,
    price: number,
    image: string,  // Single image URL with /images/ prefix
    description: string,
    category: string,  // Category name, not object
    unit: string,
    inStock: boolean,
    quantity: number,
    stock_quantity: number  // Added for stock warnings
  }}
  onAddToCart={handleAddToCart}  // Optional override
/>
```

### 3. Implementation Steps
1. Import ProductCard component
2. Create product transformation function
3. Replace inline grid items with ProductCard
4. Add stock warning display (below ProductCard)
5. Remove duplicate formatPrice function
6. Use ProductGridSkeleton from existing components
7. Test all functionality including animations and warnings

### 4. Stock Warning Feature
Since ProductCard doesn't display stock warnings, we'll add them below the card:
```javascript
<div>
  <ProductCard product={transformedProduct} />
  {product.stock_quantity < 10 && product.stock_quantity > 0 && (
    <p className="text-sm text-orange-600 mt-2 px-4">
      Doar {product.stock_quantity} în stoc
    </p>
  )}
</div>
```

## Benefits
- Consistent UI across all product displays
- Animation support on all pages
- Reduced code duplication
- Easier maintenance
- Better user experience