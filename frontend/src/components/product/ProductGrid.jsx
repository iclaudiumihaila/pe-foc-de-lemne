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

// Grid configuration presets
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

export default ProductGrid;