import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import { CartProvider } from '../../../contexts/CartContext';
import ProductCard, { ProductCardSkeleton, CompactProductCard } from '../ProductCard';

// Test wrapper with necessary providers
const TestWrapper = ({ children }) => {
  return (
    <CartProvider>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </CartProvider>
  );
};

// Helper function to render ProductCard with providers
const renderProductCard = (product, props = {}) => {
  return render(
    <TestWrapper>
      <ProductCard product={product} {...props} />
    </TestWrapper>
  );
};

// Mock product data
const mockProduct = {
  id: '1',
  name: 'Fresh Tomatoes',
  price: 12.50,
  image: '/images/tomatoes.jpg',
  description: 'Fresh, locally grown tomatoes',
  category: 'Vegetables',
  unit: 'kg',
  inStock: true,
  isOrganic: false,
  quantity: 1
};

const mockOrganicProduct = {
  ...mockProduct,
  id: '2',
  name: 'Organic Carrots',
  isOrganic: true
};

const mockOutOfStockProduct = {
  ...mockProduct,
  id: '3',
  name: 'Seasonal Berries',
  inStock: false
};

describe('ProductCard Component', () => {
  describe('Basic Rendering', () => {
    test('renders product card with basic information', () => {
      renderProductCard(mockProduct);
      
      expect(screen.getByText('Fresh Tomatoes')).toBeInTheDocument();
      expect(screen.getByText('Fresh, locally grown tomatoes')).toBeInTheDocument();
      expect(screen.getByText('Vegetables')).toBeInTheDocument();
      expect(screen.getByText('12,50 RON')).toBeInTheDocument();
      expect(screen.getByText('/ kg')).toBeInTheDocument();
    });

    test('renders product image with correct attributes', () => {
      renderProductCard(mockProduct);
      
      const image = screen.getByAltText('Fresh Tomatoes');
      expect(image).toBeInTheDocument();
      expect(image).toHaveAttribute('src', '/images/tomatoes.jpg');
    });

    test('renders add to cart button when in stock', () => {
      renderProductCard(mockProduct);
      
      const addButton = screen.getByRole('button', { name: /add to cart/i });
      expect(addButton).toBeInTheDocument();
      expect(addButton).not.toBeDisabled();
    });

    test('returns null when no product provided', () => {
      const { container } = render(
        <TestWrapper>
          <ProductCard product={null} />
        </TestWrapper>
      );
      
      expect(container.firstChild).toBeNull();
    });
  });

  describe('Product Features', () => {
    test('displays organic badge for organic products', () => {
      renderProductCard(mockOrganicProduct);
      
      expect(screen.getByText('🌱 Organic')).toBeInTheDocument();
    });

    test('does not display organic badge for non-organic products', () => {
      renderProductCard(mockProduct);
      
      expect(screen.queryByText('🌱 Organic')).not.toBeInTheDocument();
    });

    test('displays out of stock badge and disabled button for out of stock products', () => {
      renderProductCard(mockOutOfStockProduct);
      
      // Check for out of stock badge
      const outOfStockElements = screen.getAllByText('Out of Stock');
      expect(outOfStockElements.length).toBeGreaterThan(0);
      
      // Check for disabled button
      const button = screen.getByRole('button', { name: /out of stock/i });
      expect(button).toBeInTheDocument();
      expect(button).toBeDisabled();
    });

    test('displays category badge when category is provided', () => {
      renderProductCard(mockProduct);
      
      expect(screen.getByText('Vegetables')).toBeInTheDocument();
    });

    test('does not display category badge when category is not provided', () => {
      const productWithoutCategory = { ...mockProduct, category: null };
      renderProductCard(productWithoutCategory);
      
      expect(screen.queryByText('Vegetables')).not.toBeInTheDocument();
    });
  });

  describe('Price Formatting', () => {
    test('formats price in Romanian RON currency', () => {
      renderProductCard(mockProduct);
      
      expect(screen.getByText('12,50 RON')).toBeInTheDocument();
    });

    test('displays unit information when provided', () => {
      renderProductCard(mockProduct);
      
      expect(screen.getByText('/ kg')).toBeInTheDocument();
    });

    test('does not display unit when not provided', () => {
      const productWithoutUnit = { ...mockProduct, unit: null };
      renderProductCard(productWithoutUnit);
      
      expect(screen.queryByText('/ kg')).not.toBeInTheDocument();
    });

    test('formats different price values correctly', () => {
      const expensiveProduct = { ...mockProduct, price: 99.99 };
      renderProductCard(expensiveProduct);
      
      expect(screen.getByText('99,99 RON')).toBeInTheDocument();
    });
  });

  describe('Image Handling', () => {
    test('uses placeholder image when no image provided', () => {
      const productWithoutImage = { ...mockProduct, image: null };
      renderProductCard(productWithoutImage);
      
      const image = screen.getByAltText('Fresh Tomatoes');
      expect(image).toHaveAttribute('src', '/images/placeholder-product.jpg');
    });

    test('handles image error by setting fallback', () => {
      renderProductCard(mockProduct);
      
      const image = screen.getByAltText('Fresh Tomatoes');
      
      // Simulate image error
      fireEvent.error(image);
      
      expect(image).toHaveAttribute('src', '/images/placeholder-product.jpg');
    });
  });

  describe('Cart Integration', () => {
    test('calls custom onAddToCart handler when provided', () => {
      const mockAddToCart = jest.fn();
      renderProductCard(mockProduct, { onAddToCart: mockAddToCart });
      
      const addButton = screen.getByRole('button', { name: /add to cart/i });
      fireEvent.click(addButton);
      
      expect(mockAddToCart).toHaveBeenCalledWith(mockProduct);
    });

    test('does not call onAddToCart when product is out of stock', () => {
      const mockAddToCart = jest.fn();
      renderProductCard(mockOutOfStockProduct, { onAddToCart: mockAddToCart });
      
      const button = screen.getByRole('button', { name: /out of stock/i });
      fireEvent.click(button);
      
      expect(mockAddToCart).not.toHaveBeenCalled();
    });

    test('integrates with cart context when no custom handler provided', () => {
      // This test verifies the component doesn't crash when using cart context
      expect(() => {
        renderProductCard(mockProduct);
      }).not.toThrow();
    });
  });

  describe('Accessibility', () => {
    test('has proper image alt text', () => {
      renderProductCard(mockProduct);
      
      const image = screen.getByAltText('Fresh Tomatoes');
      expect(image).toBeInTheDocument();
    });

    test('button has proper text content for screen readers', () => {
      renderProductCard(mockProduct);
      
      const button = screen.getByRole('button', { name: /add to cart/i });
      expect(button).toHaveTextContent('Add to Cart');
    });

    test('out of stock button has proper accessibility', () => {
      renderProductCard(mockOutOfStockProduct);
      
      const button = screen.getByRole('button', { name: /out of stock/i });
      expect(button).toBeDisabled();
      expect(button).toHaveTextContent('Out of Stock');
    });

    test('product name uses proper heading structure', () => {
      renderProductCard(mockProduct);
      
      const heading = screen.getByRole('heading', { name: 'Fresh Tomatoes' });
      expect(heading).toBeInTheDocument();
      expect(heading.tagName).toBe('H3');
    });
  });

  describe('Custom Styling', () => {
    test('applies custom className when provided', () => {
      const { container } = renderProductCard(mockProduct, { className: 'custom-class' });
      
      const card = container.querySelector('.custom-class');
      expect(card).toBeInTheDocument();
    });

    test('applies default styling when no className provided', () => {
      const { container } = renderProductCard(mockProduct);
      
      const card = container.querySelector('.max-w-sm');
      expect(card).toBeInTheDocument();
    });
  });

  describe('Optional Fields', () => {
    test('does not display description when not provided', () => {
      const productWithoutDescription = { ...mockProduct, description: null };
      renderProductCard(productWithoutDescription);
      
      expect(screen.queryByText('Fresh, locally grown tomatoes')).not.toBeInTheDocument();
    });

    test('handles missing optional fields gracefully', () => {
      const minimalProduct = {
        id: '1',
        name: 'Basic Product',
        price: 10.00,
        inStock: true
      };
      
      expect(() => {
        renderProductCard(minimalProduct);
      }).not.toThrow();
      
      expect(screen.getByText('Basic Product')).toBeInTheDocument();
      expect(screen.getByText('10,00 RON')).toBeInTheDocument();
    });
  });
});

describe('ProductCardSkeleton Component', () => {
  test('renders skeleton loader correctly', () => {
    render(<ProductCardSkeleton />);
    
    const skeletonElements = document.querySelectorAll('.animate-pulse');
    expect(skeletonElements.length).toBeGreaterThan(0);
  });

  test('has proper structure for loading state', () => {
    const { container } = render(<ProductCardSkeleton />);
    
    expect(container.querySelector('.bg-white')).toBeInTheDocument();
    expect(container.querySelector('.rounded-lg')).toBeInTheDocument();
    expect(container.querySelector('.shadow-md')).toBeInTheDocument();
  });
});

describe('CompactProductCard Component', () => {
  const renderCompactCard = (product, props = {}) => {
    return render(
      <TestWrapper>
        <CompactProductCard product={product} {...props} />
      </TestWrapper>
    );
  };

  test('renders compact layout correctly', () => {
    renderCompactCard(mockProduct);
    
    expect(screen.getByText('Fresh Tomatoes')).toBeInTheDocument();
    expect(screen.getByText('Vegetables')).toBeInTheDocument();
    expect(screen.getByText('12,50 RON')).toBeInTheDocument();
  });

  test('renders smaller image in compact view', () => {
    renderCompactCard(mockProduct);
    
    const image = screen.getByAltText('Fresh Tomatoes');
    expect(image).toBeInTheDocument();
    expect(image).toHaveClass('w-16', 'h-16');
  });

  test('compact add to cart button works', () => {
    const mockAddToCart = jest.fn();
    renderCompactCard(mockProduct, { onAddToCart: mockAddToCart });
    
    const addButton = screen.getByRole('button');
    fireEvent.click(addButton);
    
    expect(mockAddToCart).toHaveBeenCalledWith(mockProduct);
  });

  test('handles out of stock in compact view', () => {
    renderCompactCard(mockOutOfStockProduct);
    
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });

  test('handles image error in compact view', () => {
    renderCompactCard(mockProduct);
    
    const image = screen.getByAltText('Fresh Tomatoes');
    fireEvent.error(image);
    
    expect(image).toHaveAttribute('src', '/images/placeholder-product.jpg');
  });
});

describe('ProductCard Integration', () => {
  test('renders multiple product cards in grid', () => {
    const products = [mockProduct, mockOrganicProduct, mockOutOfStockProduct];
    
    render(
      <TestWrapper>
        <div className="grid grid-cols-3 gap-4">
          {products.map(product => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      </TestWrapper>
    );
    
    expect(screen.getByText('Fresh Tomatoes')).toBeInTheDocument();
    expect(screen.getByText('Organic Carrots')).toBeInTheDocument();
    expect(screen.getByText('Seasonal Berries')).toBeInTheDocument();
  });

  test('all variants render without errors', () => {
    expect(() => {
      render(
        <TestWrapper>
          <div>
            <ProductCard product={mockProduct} />
            <ProductCardSkeleton />
            <CompactProductCard product={mockProduct} />
          </div>
        </TestWrapper>
      );
    }).not.toThrow();
  });
});