# Task 49: Create ProductCard component

## Task Details
- **ID**: 49_product_card_component_creation
- **Title**: Create ProductCard component
- **Priority**: High
- **Estimate**: 20 minutes
- **Dependencies**: Tailwind CSS configuration (Task 43)

## Objective
Implement a ProductCard component for displaying individual products in grid layouts, using HeroUI components where appropriate and implementing product-specific functionality for the local producer marketplace.

## Requirements
1. **Product Display**: Show product image, name, price, and basic details
2. **Add to Cart**: Integration with cart functionality
3. **HeroUI Integration**: Use HeroUI Card, Button, and other components
4. **Responsive Design**: Work well in grid layouts on mobile and desktop
5. **Local Producer Theme**: Appropriate styling for agricultural products

## Technical Implementation

### 1. ProductCard Component (frontend/src/components/product/ProductCard.jsx)
```javascript
import React from 'react';
import { Card, CardBody, CardFooter, Button, Image, Chip } from '@heroui/react';
import { useCartContext } from '../../contexts/CartContext';

const ProductCard = ({ product, onAddToCart, className = '' }) => {
  const { addToCart } = useCartContext();
  
  if (!product) return null;

  const {
    id,
    name,
    price,
    image,
    description,
    category,
    unit,
    inStock = true,
    isOrganic = false,
    quantity = 1
  } = product;

  const handleAddToCart = () => {
    if (onAddToCart) {
      onAddToCart(product);
    } else {
      addToCart(product, quantity);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('ro-RO', {
      style: 'currency',
      currency: 'RON'
    }).format(price);
  };

  return (
    <Card 
      className={`max-w-sm ${className}`}
      shadow="sm"
      isPressable
      isHoverable
    >
      <CardBody className="p-0">
        {/* Product Image */}
        <div className="relative">
          <Image
            src={image || '/images/placeholder-product.jpg'}
            alt={name}
            className="w-full h-48 object-cover"
            fallbackSrc="/images/placeholder-product.jpg"
          />
          
          {/* Organic Badge */}
          {isOrganic && (
            <Chip
              className="absolute top-2 left-2"
              color="success"
              variant="solid"
              size="sm"
            >
              🌱 Organic
            </Chip>
          )}
          
          {/* Stock Status */}
          {!inStock && (
            <Chip
              className="absolute top-2 right-2"
              color="danger"
              variant="solid"
              size="sm"
            >
              Out of Stock
            </Chip>
          )}
        </div>

        {/* Product Information */}
        <div className="p-4">
          {/* Category */}
          {category && (
            <Chip
              color="primary"
              variant="flat"
              size="sm"
              className="mb-2"
            >
              {category}
            </Chip>
          )}
          
          {/* Product Name */}
          <h3 className="text-lg font-semibold text-foreground mb-2 line-clamp-2">
            {name}
          </h3>
          
          {/* Description */}
          {description && (
            <p className="text-sm text-foreground-500 mb-3 line-clamp-2">
              {description}
            </p>
          )}
          
          {/* Price and Unit */}
          <div className="flex items-center justify-between mb-3">
            <div>
              <span className="text-xl font-bold text-primary">
                {formatPrice(price)}
              </span>
              {unit && (
                <span className="text-sm text-foreground-500 ml-1">
                  / {unit}
                </span>
              )}
            </div>
          </div>
        </div>
      </CardBody>

      <CardFooter className="pt-0 px-4 pb-4">
        <Button
          color="primary"
          variant="solid"
          fullWidth
          isDisabled={!inStock}
          onPress={handleAddToCart}
          startContent={<span>🛒</span>}
        >
          {inStock ? 'Add to Cart' : 'Out of Stock'}
        </Button>
      </CardFooter>
    </Card>
  );
};

// Skeleton loader for loading states
export const ProductCardSkeleton = () => (
  <Card className="max-w-sm">
    <CardBody className="p-0">
      <div className="w-full h-48 bg-default-200 animate-pulse rounded-t-lg" />
      <div className="p-4 space-y-3">
        <div className="h-4 bg-default-200 rounded animate-pulse w-1/3" />
        <div className="h-6 bg-default-200 rounded animate-pulse w-3/4" />
        <div className="h-4 bg-default-200 rounded animate-pulse w-full" />
        <div className="h-4 bg-default-200 rounded animate-pulse w-2/3" />
        <div className="h-6 bg-default-200 rounded animate-pulse w-1/2" />
      </div>
    </CardBody>
    <CardFooter className="pt-0 px-4 pb-4">
      <div className="h-10 bg-default-200 rounded animate-pulse w-full" />
    </CardFooter>
  </Card>
);

export default ProductCard;
```

### 2. Alternative Compact Card Variant
```javascript
export const CompactProductCard = ({ product, onAddToCart, className = '' }) => {
  const { addToCart } = useCartContext();
  
  const handleAddToCart = () => {
    if (onAddToCart) {
      onAddToCart(product);
    } else {
      addToCart(product, 1);
    }
  };

  return (
    <Card className={`w-full ${className}`} shadow="sm">
      <CardBody className="p-3">
        <div className="flex gap-3">
          {/* Small Product Image */}
          <Image
            src={product.image || '/images/placeholder-product.jpg'}
            alt={product.name}
            className="w-16 h-16 object-cover rounded-md flex-shrink-0"
          />
          
          {/* Product Info */}
          <div className="flex-1 min-w-0">
            <h4 className="font-medium text-foreground truncate">
              {product.name}
            </h4>
            <p className="text-sm text-foreground-500 truncate">
              {product.category}
            </p>
            <div className="flex items-center justify-between mt-2">
              <span className="font-semibold text-primary">
                {formatPrice(product.price)}
              </span>
              <Button
                size="sm"
                color="primary"
                variant="light"
                isIconOnly
                onPress={handleAddToCart}
                isDisabled={!product.inStock}
              >
                🛒
              </Button>
            </div>
          </div>
        </div>
      </CardBody>
    </Card>
  );
};
```

## Component Features

### 1. HeroUI Integration
- **Card Component**: Using HeroUI Card with CardBody and CardFooter
- **Image Component**: HeroUI Image with fallback support
- **Button Component**: HeroUI Button with variants and states
- **Chip Component**: For category, organic, and stock status badges

### 2. Local Producer Specific Features
- **Organic Badge**: Green badge for organic products
- **Category Display**: Product category chips
- **Unit Display**: Price per unit (kg, piece, etc.)
- **Romanian Currency**: RON formatting for prices
- **Stock Status**: Clear indication of availability

### 3. Responsive Design
- **Mobile-First**: Optimized for mobile grid layouts
- **Flexible Sizing**: Works in various grid configurations
- **Image Handling**: Consistent aspect ratios and fallbacks
- **Touch-Friendly**: Appropriate button sizes for mobile

### 4. Cart Integration
- **Cart Context**: Direct integration with useCartContext
- **Add to Cart**: Seamless cart functionality
- **Quantity Handling**: Support for quantity selection
- **Stock Validation**: Prevents adding out-of-stock items

## Usage Examples

### 1. Product Grid Display
```javascript
// In ProductGrid component
import ProductCard from './ProductCard';

const ProductGrid = ({ products }) => (
  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
    {products.map(product => (
      <ProductCard 
        key={product.id} 
        product={product}
        onAddToCart={(product) => console.log('Added:', product)}
      />
    ))}
  </div>
);
```

### 2. Featured Products Section
```javascript
// In HomePage component
const FeaturedProducts = ({ products }) => (
  <section className="py-8">
    <h2 className="text-2xl font-bold mb-6">Featured Products</h2>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {products.slice(0, 3).map(product => (
        <ProductCard 
          key={product.id} 
          product={product}
          className="max-w-none"
        />
      ))}
    </div>
  </section>
);
```

### 3. Loading State
```javascript
// While loading products
const ProductGrid = ({ products, loading }) => (
  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
    {loading ? (
      Array(8).fill(0).map((_, index) => (
        <ProductCardSkeleton key={index} />
      ))
    ) : (
      products.map(product => (
        <ProductCard key={product.id} product={product} />
      ))
    )}
  </div>
);
```

## Implementation Steps

### 1. Install HeroUI Dependencies
```bash
npm install @heroui/react @heroui/theme
```

### 2. Create Component Directory
- Create `/frontend/src/components/product/` directory
- Create `ProductCard.jsx` file
- Add to component exports

### 3. Implement Cart Integration
- Import and use CartContext
- Handle add to cart functionality
- Manage product state and quantities

### 4. Add Romanian Localization
- Implement RON currency formatting
- Add Romanian text if needed
- Handle local number formatting

## Testing Considerations

### 1. Visual Testing
- Product card renders correctly in grid
- Images load with fallbacks
- Badges display appropriately
- Responsive behavior on mobile

### 2. Interaction Testing
- Add to Cart button functionality
- Cart context integration
- Out of stock handling
- Button states and feedback

### 3. Data Handling
- Missing product data gracefully handled
- Price formatting works correctly
- Image fallbacks function properly
- Category and unit display

## Success Criteria
- ProductCard displays product information clearly
- HeroUI components integrate seamlessly
- Add to Cart functionality works with cart context
- Component is responsive and mobile-friendly
- Romanian localization (RON currency) works correctly
- Loading skeleton provides good UX during data fetching