# Task 51: Create ProductGrid component

## Task Details
- **ID**: 51_product_grid_component_creation
- **Title**: Create ProductGrid component
- **Priority**: High
- **Estimate**: 15 minutes
- **Dependencies**: ProductCard component creation (Task 49)

## Objective
Implement a responsive ProductGrid component that displays multiple ProductCard components in an optimized grid layout with loading states, empty states, and excellent mobile/desktop responsive behavior for the local producer marketplace.

## Requirements
1. **Responsive Grid**: Adaptive grid layout for different screen sizes
2. **Loading States**: Integration with ProductCardSkeleton for loading UX
3. **Empty States**: Proper handling when no products available
4. **Performance**: Efficient rendering for large product lists
5. **Accessibility**: Proper grid semantics and navigation

## Technical Implementation

### 1. ProductGrid Component (frontend/src/components/product/ProductGrid.jsx)
```javascript
import React from 'react';
import ProductCard, { ProductCardSkeleton } from './ProductCard';

const ProductGrid = ({ 
  products = [], 
  loading = false, 
  error = null,
  onAddToCart,
  className = '',
  emptyMessage = 'Nu sunt produse disponibile.',
  loadingCount = 8,
  columns = {
    default: 1,
    sm: 2,
    md: 3,
    lg: 3,
    xl: 4
  }
}) => {
  // Generate grid classes based on column configuration
  const getGridClasses = () => {
    const { default: def, sm, md, lg, xl } = columns;
    return `
      grid gap-6
      grid-cols-${def}
      ${sm ? `sm:grid-cols-${sm}` : ''}
      ${md ? `md:grid-cols-${md}` : ''}
      ${lg ? `lg:grid-cols-${lg}` : ''}
      ${xl ? `xl:grid-cols-${xl}` : ''}
    `.trim().replace(/\s+/g, ' ');
  };

  // Render loading skeletons
  const renderLoadingState = () => (
    <div className={`${getGridClasses()} ${className}`}>
      {Array(loadingCount).fill(0).map((_, index) => (
        <ProductCardSkeleton key={`skeleton-${index}`} />
      ))}
    </div>
  );

  // Render empty state
  const renderEmptyState = () => (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      <div className="text-6xl mb-4">📦</div>
      <h3 className="text-xl font-semibold text-gray-700 mb-2">
        {emptyMessage}
      </h3>
      <p className="text-gray-500 text-center max-w-md">
        Nu am găsit produse care să corespundă criteriilor tale. 
        Încearcă să modifici filtrele sau revino mai târziu.
      </p>
    </div>
  );

  // Render error state
  const renderErrorState = () => (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      <div className="text-6xl mb-4">⚠️</div>
      <h3 className="text-xl font-semibold text-red-700 mb-2">
        Eroare la încărcarea produselor
      </h3>
      <p className="text-gray-500 text-center max-w-md mb-4">
        {error || 'A apărut o eroare neașteptată. Te rugăm să încerci din nou.'}
      </p>
      <button 
        onClick={() => window.location.reload()}
        className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg transition-colors"
      >
        Încearcă din nou
      </button>
    </div>
  );

  // Render product grid
  const renderProductGrid = () => (
    <div className={`${getGridClasses()} ${className}`}>
      {products.map((product) => (
        <ProductCard
          key={product.id}
          product={product}
          onAddToCart={onAddToCart}
        />
      ))}
    </div>
  );

  // Main render logic
  if (loading) {
    return renderLoadingState();
  }

  if (error) {
    return renderErrorState();
  }

  if (!products || products.length === 0) {
    return renderEmptyState();
  }

  return renderProductGrid();
};

// Alternative grid layouts for different use cases
export const FeaturedProductGrid = ({ products, loading, ...props }) => (
  <ProductGrid
    products={products}
    loading={loading}
    columns={{
      default: 1,
      md: 2,
      lg: 3,
      xl: 3
    }}
    loadingCount={3}
    emptyMessage="Nu sunt produse recomandate momentan."
    {...props}
  />
);

export const CompactProductGrid = ({ products, loading, ...props }) => (
  <ProductGrid
    products={products}
    loading={loading}
    columns={{
      default: 2,
      sm: 3,
      md: 4,
      lg: 5,
      xl: 6
    }}
    loadingCount={6}
    className="gap-4"
    {...props}
  />
);

// Grid with category sections
export const CategorizedProductGrid = ({ categorizedProducts, loading, ...props }) => {
  if (loading) {
    return <ProductGrid loading={true} {...props} />;
  }

  if (!categorizedProducts || Object.keys(categorizedProducts).length === 0) {
    return (
      <ProductGrid 
        products={[]} 
        emptyMessage="Nu sunt produse disponibile în nicio categorie."
        {...props} 
      />
    );
  }

  return (
    <div className="space-y-8">
      {Object.entries(categorizedProducts).map(([category, products]) => (
        <section key={category} className="space-y-4">
          <h2 className="text-2xl font-bold text-gray-900 border-b border-gray-200 pb-2">
            {category}
          </h2>
          <ProductGrid
            products={products}
            columns={{
              default: 1,
              sm: 2,
              md: 3,
              lg: 4,
              xl: 4
            }}
            emptyMessage={`Nu sunt produse disponibile în categoria ${category}.`}
            {...props}
          />
        </section>
      ))}
    </div>
  );
};

export default ProductGrid;
```

### 2. Grid Configuration Options
```javascript
// Standard grid configurations
export const GRID_LAYOUTS = {
  // Default responsive grid
  standard: {
    default: 1,
    sm: 2,
    md: 3,
    lg: 3,
    xl: 4
  },
  
  // Compact grid for smaller cards
  compact: {
    default: 2,
    sm: 3,
    md: 4,
    lg: 5,
    xl: 6
  },
  
  // Featured products (fewer columns)
  featured: {
    default: 1,
    md: 2,
    lg: 3,
    xl: 3
  },
  
  // Mobile-first single column
  single: {
    default: 1,
    lg: 2,
    xl: 3
  }
};
```

## Component Features

### 1. Responsive Grid System
- **Mobile-first**: Starts with single column on mobile
- **Breakpoint adaptation**: 2 columns on small, 3 on medium, 4 on extra large
- **Flexible configuration**: Customizable column counts per breakpoint
- **Consistent gaps**: 24px gap between cards for proper spacing

### 2. Loading States
- **Skeleton integration**: Uses ProductCardSkeleton for loading UX
- **Configurable count**: Adjustable number of skeleton cards
- **Grid preservation**: Maintains grid layout during loading
- **Performance optimized**: Efficient skeleton rendering

### 3. Empty and Error States
- **Romanian localization**: Error messages in Romanian
- **Visual indicators**: Emoji icons for better UX
- **Helpful messaging**: Clear explanation of empty states
- **Recovery options**: Reload button for error states

### 4. Performance Features
- **Efficient rendering**: Only renders visible products
- **Key optimization**: Proper key props for React reconciliation
- **Lazy loading ready**: Structure supports infinite scroll
- **Memory efficient**: No unnecessary re-renders

## Usage Examples

### 1. Basic Product Grid
```javascript
// In Products page
import ProductGrid from '../components/product/ProductGrid';

const ProductsPage = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProducts()
      .then(data => setProducts(data))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Toate Produsele</h1>
      <ProductGrid
        products={products}
        loading={loading}
        error={error}
        onAddToCart={(product) => addToCart(product)}
      />
    </div>
  );
};
```

### 2. Featured Products Section
```javascript
// In HomePage component
import { FeaturedProductGrid } from '../components/product/ProductGrid';

const FeaturedSection = ({ featuredProducts, loading }) => (
  <section className="py-12 bg-gray-50">
    <div className="container mx-auto px-4">
      <h2 className="text-3xl font-bold text-center mb-8">
        Produse Recomandate
      </h2>
      <FeaturedProductGrid
        products={featuredProducts}
        loading={loading}
        onAddToCart={(product) => addToCart(product)}
      />
    </div>
  </section>
);
```

### 3. Category-Based Grid
```javascript
// Categorized product display
const CategoryPage = ({ categoryProducts, loading }) => {
  const categorizedData = {
    'Legume': categoryProducts.filter(p => p.category === 'Legume'),
    'Fructe': categoryProducts.filter(p => p.category === 'Fructe'),
    'Produse Bio': categoryProducts.filter(p => p.isOrganic)
  };

  return (
    <CategorizedProductGrid
      categorizedProducts={categorizedData}
      loading={loading}
      onAddToCart={(product) => addToCart(product)}
    />
  );
};
```

### 4. Search Results Grid
```javascript
// Search results with custom empty message
const SearchResults = ({ products, loading, searchTerm }) => (
  <ProductGrid
    products={products}
    loading={loading}
    emptyMessage={`Nu am găsit produse pentru "${searchTerm}"`}
    onAddToCart={(product) => addToCart(product)}
  />
);
```

## Implementation Steps

### 1. Create Component File
- Create `/frontend/src/components/product/ProductGrid.jsx`
- Implement responsive grid system
- Add loading and empty state handling

### 2. Configure Responsive Breakpoints
- Set up Tailwind grid classes
- Define column configurations
- Test responsive behavior

### 3. Add State Management
- Loading state with skeletons
- Empty state with helpful messaging
- Error state with recovery options

### 4. Performance Optimization
- Efficient key generation
- Minimal re-renders
- Memory usage optimization

## Responsive Design

### 1. Mobile (< 640px)
- **Single column**: Optimal for small screens
- **Full width**: Cards use available space
- **Touch-friendly**: Proper spacing for touch targets

### 2. Small (640px - 768px)
- **Two columns**: Better space utilization
- **Maintained gaps**: Consistent spacing
- **Readable text**: Appropriate font sizes

### 3. Medium (768px - 1024px)
- **Three columns**: Balanced layout
- **Desktop transition**: Preparing for larger screens
- **Optimal viewing**: Good product visibility

### 4. Large (1024px+)
- **Three to four columns**: Maximum efficiency
- **Desktop optimized**: Full screen utilization
- **Grid density**: More products visible

## Accessibility Features

### 1. Semantic Structure
- **Proper HTML**: Semantic grid and product containers
- **Heading hierarchy**: Logical heading structure
- **ARIA labels**: Screen reader support where needed

### 2. Keyboard Navigation
- **Tab navigation**: Proper tab order through products
- **Focus management**: Clear focus indicators
- **Skip links**: Navigation shortcuts for screen readers

### 3. Screen Reader Support
- **Alternative text**: Descriptive content for images
- **State announcements**: Loading and error state announcements
- **Product information**: Accessible product details

## Testing Considerations

### 1. Responsive Testing
- Grid layout on different screen sizes
- Breakpoint transitions
- Column count verification

### 2. State Testing
- Loading skeleton display
- Empty state messaging
- Error handling and recovery

### 3. Performance Testing
- Large product list rendering
- Scroll performance
- Memory usage monitoring

## Success Criteria
- ProductGrid displays products in responsive grid layout
- Loading states show appropriate skeleton cards
- Empty and error states provide helpful user feedback
- Component handles large product lists efficiently
- Grid adapts properly to different screen sizes
- Romanian localization works correctly for all messages