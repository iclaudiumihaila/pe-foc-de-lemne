/**
 * Mobile Responsiveness End-to-End Tests
 * 
 * Tests the application's responsiveness and mobile-specific functionality
 * across different device sizes and orientations
 */

describe('Mobile Responsiveness Tests', () => {
  const viewports = [
    { name: 'iPhone SE', width: 375, height: 667 },
    { name: 'iPhone 12', width: 390, height: 844 },
    { name: 'Samsung Galaxy S21', width: 384, height: 854 },
    { name: 'iPad Mini', width: 768, height: 1024 },
    { name: 'iPad Pro', width: 1024, height: 1366 },
    { name: 'Small Mobile', width: 320, height: 568 }
  ];

  beforeEach(() => {
    cy.clearLocalStorage();
    cy.clearCookies();
  });

  viewports.forEach((viewport) => {
    context(`${viewport.name} (${viewport.width}x${viewport.height})`, () => {
      beforeEach(() => {
        cy.viewport(viewport.width, viewport.height);
      });

      it('displays responsive home page layout', () => {
        cy.log(`Testing home page on ${viewport.name}`);
        
        cy.visit('/');
        
        // Verify page loads
        cy.get('[data-testid="home-page"]').should('be.visible');
        
        // Check header responsiveness
        if (viewport.width <= 768) {
          // Mobile: hamburger menu should be visible
          cy.get('[data-testid="mobile-menu-button"]').should('be.visible');
          cy.get('[data-testid="desktop-nav"]').should('not.be.visible');
        } else {
          // Desktop/Tablet: desktop nav should be visible
          cy.get('[data-testid="desktop-nav"]').should('be.visible');
          cy.get('[data-testid="mobile-menu-button"]').should('not.be.visible');
        }
        
        // Check hero section responsiveness
        cy.get('[data-testid="hero-section"]').should('be.visible');
        cy.get('[data-testid="hero-title"]').should('be.visible');
        
        // Verify text is readable (not cut off)
        cy.get('[data-testid="hero-title"]').then(($title) => {
          expect($title[0].scrollWidth).to.be.lte($title[0].clientWidth + 5);
        });
        
        // Check featured products section
        cy.get('[data-testid="featured-products"]').should('be.visible');
        
        // Verify product grid adapts to screen size
        if (viewport.width <= 640) {
          // Mobile: 1 column
          cy.get('[data-testid="product-grid"]')
            .should('have.class', 'grid-cols-1');
        } else if (viewport.width <= 1024) {
          // Tablet: 2 columns
          cy.get('[data-testid="product-grid"]')
            .should('have.class', 'md:grid-cols-2');
        } else {
          // Desktop: 3+ columns
          cy.get('[data-testid="product-grid"]')
            .should('have.class', 'lg:grid-cols-3');
        }
      });

      it('provides accessible mobile navigation', () => {
        cy.log(`Testing mobile navigation on ${viewport.name}`);
        
        cy.visit('/');
        
        if (viewport.width <= 768) {
          // Test mobile menu
          cy.get('[data-testid="mobile-menu-button"]').should('be.visible');
          cy.get('[data-testid="mobile-menu"]').should('not.be.visible');
          
          // Open mobile menu
          cy.get('[data-testid="mobile-menu-button"]').click();
          cy.get('[data-testid="mobile-menu"]').should('be.visible');
          
          // Verify menu items are accessible
          cy.get('[data-testid="mobile-nav-home"]').should('be.visible');
          cy.get('[data-testid="mobile-nav-products"]').should('be.visible');
          cy.get('[data-testid="mobile-nav-cart"]').should('be.visible');
          
          // Test navigation
          cy.get('[data-testid="mobile-nav-products"]').click();
          cy.url().should('include', '/produse');
          
          // Verify menu closes after navigation
          cy.get('[data-testid="mobile-menu"]').should('not.be.visible');
          
          // Test cart icon accessibility
          cy.get('[data-testid="cart-icon"]').should('be.visible');
          cy.get('[data-testid="cart-counter"]').should('be.visible');
        }
      });

      it('displays responsive product listing', () => {
        cy.log(`Testing product listing on ${viewport.name}`);
        
        cy.visit('/produse');
        
        // Mock products API
        cy.intercept('GET', '/api/products*', {
          statusCode: 200,
          body: {
            success: true,
            products: Array.from({ length: 12 }, (_, i) => ({
              id: `product-${i + 1}`,
              name: `Produs ${i + 1}`,
              category: 'Fructe',
              price: (i + 1) * 5.99,
              producer: `Producător ${i + 1}`,
              image: '/images/placeholder.jpg'
            }))
          }
        }).as('getProducts');
        
        cy.wait('@getProducts');
        
        // Verify products page loads
        cy.get('[data-testid="products-page"]').should('be.visible');
        
        // Check search and filter responsiveness
        if (viewport.width <= 640) {
          // Mobile: filters should be collapsible
          cy.get('[data-testid="filter-toggle"]').should('be.visible');
          cy.get('[data-testid="product-filters"]').should('not.be.visible');
          
          // Toggle filters
          cy.get('[data-testid="filter-toggle"]').click();
          cy.get('[data-testid="product-filters"]').should('be.visible');
          
          // Search should be full width
          cy.get('[data-testid="search-input"]')
            .should('be.visible')
            .and('have.class', 'w-full');
        } else {
          // Desktop/Tablet: filters should be visible
          cy.get('[data-testid="product-filters"]').should('be.visible');
        }
        
        // Test product grid responsiveness
        cy.get('[data-testid="product-grid"]').should('be.visible');
        cy.get('[data-testid="product-card"]').should('have.length.at.least', 1);
        
        // Verify product cards fit properly
        cy.get('[data-testid="product-card"]').first().then(($card) => {
          const cardWidth = $card[0].offsetWidth;
          const containerWidth = $card.parent()[0].offsetWidth;
          
          // Card should not exceed container width
          expect(cardWidth).to.be.lte(containerWidth);
        });
        
        // Test add to cart button accessibility
        cy.get('[data-testid="product-card"]').first().within(() => {
          cy.get('[data-testid="add-to-cart-button"]')
            .should('be.visible')
            .and('have.css', 'min-height')
            .and('not.have.css', 'min-height', '0px'); // Should have minimum touch target
        });
      });

      it('provides responsive cart experience', () => {
        cy.log(`Testing cart experience on ${viewport.name}`);
        
        // Add some items to cart first
        cy.visit('/produse');
        
        cy.intercept('GET', '/api/products*', {
          statusCode: 200,
          body: {
            success: true,
            products: [
              {
                id: 'product-1',
                name: 'Mere Golden',
                category: 'Fructe',
                price: 8.99,
                producer: 'Ferma Ionescu'
              }
            ]
          }
        }).as('getProducts');
        
        cy.wait('@getProducts');
        
        // Add product to cart
        cy.get('[data-testid="product-card"]').first().within(() => {
          cy.get('[data-testid="add-to-cart-button"]').click();
        });
        
        // Navigate to cart
        cy.get('[data-testid="cart-icon"]').click();
        cy.url().should('include', '/cos');
        
        // Verify cart page responsiveness
        cy.get('[data-testid="cart-page"]').should('be.visible');
        
        if (viewport.width <= 640) {
          // Mobile: cart items should stack vertically
          cy.get('[data-testid="cart-item"]').should('have.class', 'flex-col');
          
          // Quantity controls should be touch-friendly
          cy.get('[data-testid="quantity-controls"]').within(() => {
            cy.get('button').should('have.css', 'min-width');
            cy.get('button').should('have.css', 'min-height');
          });
        } else {
          // Desktop/Tablet: cart items can be horizontal
          cy.get('[data-testid="cart-item"]').should('not.have.class', 'flex-col');
        }
        
        // Test cart summary responsiveness
        cy.get('[data-testid="cart-summary"]').should('be.visible');
        
        if (viewport.width <= 768) {
          // Mobile: summary should be at bottom or full width
          cy.get('[data-testid="checkout-button"]')
            .should('be.visible')
            .and('have.class', 'w-full');
        }
        
        // Test quantity updates
        cy.get('[data-testid="quantity-input"]').clear().type('2');
        cy.get('[data-testid="update-quantity-button"]').click();
        
        // Verify total updates
        cy.get('[data-testid="cart-total"]').should('contain', '17.98');
      });

      it('handles responsive checkout flow', () => {
        cy.log(`Testing checkout flow on ${viewport.name}`);
        
        // Add item to cart and proceed to checkout
        cy.visit('/produse');
        
        cy.intercept('GET', '/api/products*', {
          body: {
            success: true,
            products: [{ id: '1', name: 'Test Product', price: 10.00 }]
          }
        });
        
        cy.get('[data-testid="product-card"]').first().within(() => {
          cy.get('[data-testid="add-to-cart-button"]').click();
        });
        
        cy.get('[data-testid="cart-icon"]').click();
        cy.get('[data-testid="checkout-button"]').click();
        
        // Verify checkout page responsiveness
        cy.get('[data-testid="checkout-page"]').should('be.visible');
        cy.get('[data-testid="customer-form"]').should('be.visible');
        
        // Check form layout
        if (viewport.width <= 640) {
          // Mobile: form fields should be full width and stacked
          cy.get('[data-testid="customer-name"]')
            .should('have.class', 'w-full');
          
          cy.get('[data-testid="customer-phone"]')
            .should('have.attr', 'type', 'tel'); // Mobile-optimized input
        }
        
        // Test form field accessibility
        cy.get('input, select, textarea').each(($field) => {
          // All form fields should have adequate touch targets
          cy.wrap($field).should('have.css', 'min-height');
        });
        
        // Fill form
        cy.get('[data-testid="customer-name"]').type('Test User');
        cy.get('[data-testid="customer-phone"]').type('0721234567');
        cy.get('[data-testid="customer-email"]').type('test@example.com');
        cy.get('[data-testid="customer-address"]').type('Test Address');
        cy.get('[data-testid="customer-city"]').type('București');
        cy.get('[data-testid="customer-county"]').select('București');
        cy.get('[data-testid="customer-postal-code"]').type('123456');
        
        // Submit form
        cy.get('[data-testid="submit-customer-form"]').click();
        
        // Verify SMS verification appears
        cy.get('[data-testid="sms-verification"]').should('be.visible');
        
        if (viewport.width <= 640) {
          // Mobile: verification code input should be optimized
          cy.get('[data-testid="verification-code-input"]')
            .should('have.attr', 'type', 'tel')
            .and('have.attr', 'inputmode', 'numeric');
        }
      });

      it('maintains touch-friendly interactions', () => {
        cy.log(`Testing touch interactions on ${viewport.name}`);
        
        cy.visit('/');
        
        // Check button sizes meet accessibility guidelines (44px minimum)
        const checkTouchTarget = ($element) => {
          const rect = $element[0].getBoundingClientRect();
          expect(rect.width).to.be.at.least(44);
          expect(rect.height).to.be.at.least(44);
        };
        
        // Test navigation buttons
        if (viewport.width <= 768) {
          cy.get('[data-testid="mobile-menu-button"]').then(checkTouchTarget);
        }
        
        cy.get('[data-testid="cart-icon"]').then(checkTouchTarget);
        
        // Test product interactions
        cy.visit('/produse');
        
        cy.intercept('GET', '/api/products*', {
          body: {
            success: true,
            products: [{ id: '1', name: 'Test Product', price: 10.00 }]
          }
        });
        
        // Add to cart buttons should be touch-friendly
        cy.get('[data-testid="add-to-cart-button"]').then(checkTouchTarget);
        
        // Test spacing between interactive elements
        cy.get('[data-testid="product-card"]').first().within(() => {
          cy.get('button, a').should('have.length.at.least', 1);
          
          // Elements should have adequate spacing
          cy.get('button, a').each(($el, index, $list) => {
            if (index > 0) {
              const currentRect = $el[0].getBoundingClientRect();
              const prevRect = $list[index - 1].getBoundingClientRect();
              
              // Should have at least 8px spacing
              const verticalSpacing = Math.abs(currentRect.top - prevRect.bottom);
              const horizontalSpacing = Math.abs(currentRect.left - prevRect.right);
              
              expect(Math.min(verticalSpacing, horizontalSpacing)).to.be.at.least(8);
            }
          });
        });
      });

      it('displays content without horizontal scroll', () => {
        cy.log(`Testing content overflow on ${viewport.name}`);
        
        const pages = ['/', '/produse', '/cos'];
        
        pages.forEach((page) => {
          cy.visit(page);
          
          // Mock API responses as needed
          if (page === '/produse') {
            cy.intercept('GET', '/api/products*', {
              body: {
                success: true,
                products: [{ id: '1', name: 'Test Product', price: 10.00 }]
              }
            });
          }
          
          // Wait for page to load
          cy.get('body').should('be.visible');
          
          // Check that body doesn't exceed viewport width
          cy.get('body').then(($body) => {
            expect($body[0].scrollWidth).to.be.lte(viewport.width + 1); // Allow 1px tolerance
          });
          
          // Check main content container
          cy.get('main, [data-testid*="page"]').first().then(($main) => {
            expect($main[0].scrollWidth).to.be.lte(viewport.width + 1);
          });
          
          // Check that text doesn't overflow
          cy.get('h1, h2, h3, p').each(($text) => {
            expect($text[0].scrollWidth).to.be.lte($text[0].clientWidth + 5);
          });
        });
      });
    });
  });

  context('Orientation Changes', () => {
    it('handles orientation changes gracefully', () => {
      cy.log('Testing orientation changes');
      
      // Start in portrait
      cy.viewport(390, 844);
      cy.visit('/');
      
      // Verify layout in portrait
      cy.get('[data-testid="home-page"]').should('be.visible');
      
      // Switch to landscape
      cy.viewport(844, 390);
      
      // Verify layout adapts to landscape
      cy.get('[data-testid="home-page"]').should('be.visible');
      
      // Navigation should still be accessible
      cy.get('[data-testid="mobile-menu-button"]').should('be.visible');
      
      // Content should still fit
      cy.get('body').then(($body) => {
        expect($body[0].scrollWidth).to.be.lte(844 + 1);
      });
    });
  });

  context('Accessibility on Mobile', () => {
    beforeEach(() => {
      cy.viewport(375, 667); // iPhone SE
    });

    it('maintains accessibility on mobile devices', () => {
      cy.log('Testing mobile accessibility');
      
      cy.visit('/');
      
      // Test keyboard navigation
      cy.get('body').tab();
      cy.focused().should('be.visible');
      
      // Test skip links
      cy.get('body').type('{enter}');
      cy.get('[data-testid="skip-to-content"]').should('be.visible');
      
      // Test aria labels on interactive elements
      cy.get('[data-testid="mobile-menu-button"]')
        .should('have.attr', 'aria-label');
      
      cy.get('[data-testid="cart-icon"]')
        .should('have.attr', 'aria-label');
      
      // Test form labels
      cy.visit('/produse');
      cy.intercept('GET', '/api/products*', {
        body: { success: true, products: [{ id: '1', name: 'Test', price: 10 }] }
      });
      
      cy.get('[data-testid="product-card"]').first().within(() => {
        cy.get('[data-testid="add-to-cart-button"]').click();
      });
      
      cy.get('[data-testid="cart-icon"]').click();
      cy.get('[data-testid="checkout-button"]').click();
      
      // Form fields should have proper labels
      cy.get('input, select, textarea').each(($field) => {
        const id = $field.attr('id');
        if (id) {
          cy.get(`label[for="${id}"]`).should('exist');
        }
      });
      
      // Test focus management
      cy.get('[data-testid="customer-name"]').focus();
      cy.focused().should('have.attr', 'id', 'customer-name');
    });
  });
});