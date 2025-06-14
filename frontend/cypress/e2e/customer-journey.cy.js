/**
 * End-to-End Customer Journey Tests
 * 
 * Tests the complete customer workflow from browsing products
 * to completing an order with SMS verification
 */

describe('Customer Journey - Complete Order Flow', () => {
  beforeEach(() => {
    // Clear any existing cart data
    cy.clearLocalStorage();
    cy.clearCookies();
    
    // Visit home page
    cy.visit('/');
    
    // Wait for page to load
    cy.get('[data-testid="header"]').should('be.visible');
  });

  it('completes full customer journey: browse → cart → checkout → order', () => {
    // Step 1: Browse products on home page
    cy.log('Step 1: Browse products');
    
    // Verify home page loads with products
    cy.get('[data-testid="home-page"]').should('be.visible');
    cy.get('[data-testid="featured-products"]').should('be.visible');
    
    // Navigate to products page
    cy.get('[data-testid="nav-products"]').click();
    cy.url().should('include', '/produse');
    
    // Verify products page loads
    cy.get('[data-testid="products-page"]').should('be.visible');
    cy.get('[data-testid="product-grid"]').should('be.visible');
    
    // Wait for products to load
    cy.get('[data-testid="product-card"]').should('have.length.at.least', 1);
    
    // Step 2: Search and filter products
    cy.log('Step 2: Search and filter products');
    
    // Test search functionality
    cy.get('[data-testid="search-input"]').type('mere');
    cy.get('[data-testid="search-button"]').click();
    
    // Verify search results
    cy.get('[data-testid="product-card"]').should('contain.text', 'mere');
    
    // Test category filter
    cy.get('[data-testid="category-filter"]').select('Fructe');
    cy.get('[data-testid="product-card"]').each(($card) => {
      cy.wrap($card).should('contain.text', 'Fructe');
    });
    
    // Step 3: Add products to cart
    cy.log('Step 3: Add products to cart');
    
    // Add first product to cart
    cy.get('[data-testid="product-card"]').first().within(() => {
      cy.get('[data-testid="product-name"]').invoke('text').as('firstProductName');
      cy.get('[data-testid="product-price"]').invoke('text').as('firstProductPrice');
      cy.get('[data-testid="add-to-cart-button"]').click();
    });
    
    // Verify cart counter updates
    cy.get('[data-testid="cart-counter"]').should('contain', '1');
    
    // Add second product to cart
    cy.get('[data-testid="product-card"]').eq(1).within(() => {
      cy.get('[data-testid="add-to-cart-button"]').click();
    });
    
    // Verify cart counter updates
    cy.get('[data-testid="cart-counter"]').should('contain', '2');
    
    // Step 4: View and manage cart
    cy.log('Step 4: View and manage cart');
    
    // Navigate to cart page
    cy.get('[data-testid="cart-icon"]').click();
    cy.url().should('include', '/cos');
    
    // Verify cart page loads with items
    cy.get('[data-testid="cart-page"]').should('be.visible');
    cy.get('[data-testid="cart-item"]').should('have.length', 2);
    
    // Test quantity update
    cy.get('[data-testid="cart-item"]').first().within(() => {
      cy.get('[data-testid="quantity-input"]').clear().type('3');
      cy.get('[data-testid="update-quantity-button"]').click();
    });
    
    // Verify quantity updated and total recalculated
    cy.get('[data-testid="cart-item"]').first().within(() => {
      cy.get('[data-testid="quantity-input"]').should('have.value', '3');
    });
    
    // Remove one item from cart
    cy.get('[data-testid="cart-item"]').last().within(() => {
      cy.get('[data-testid="remove-item-button"]').click();
    });
    
    // Verify item removed
    cy.get('[data-testid="cart-item"]').should('have.length', 1);
    
    // Step 5: Proceed to checkout
    cy.log('Step 5: Proceed to checkout');
    
    // Click checkout button
    cy.get('[data-testid="checkout-button"]').click();
    cy.url().should('include', '/comanda');
    
    // Verify checkout page loads
    cy.get('[data-testid="checkout-page"]').should('be.visible');
    cy.get('[data-testid="customer-form"]').should('be.visible');
    
    // Step 6: Fill customer information
    cy.log('Step 6: Fill customer information');
    
    // Fill customer form with Romanian data
    cy.get('[data-testid="customer-name"]').type('Ion Popescu');
    cy.get('[data-testid="customer-phone"]').type('0721234567');
    cy.get('[data-testid="customer-email"]').type('ion.popescu@example.com');
    
    // Fill address information
    cy.get('[data-testid="customer-address"]').type('Strada Florilor 123');
    cy.get('[data-testid="customer-city"]').type('București');
    cy.get('[data-testid="customer-county"]').select('București');
    cy.get('[data-testid="customer-postal-code"]').type('123456');
    
    // Add delivery notes
    cy.get('[data-testid="delivery-notes"]').type('Vă rog să sunați înainte de livrare');
    
    // Step 7: Request SMS verification
    cy.log('Step 7: Request SMS verification');
    
    // Submit form to trigger SMS verification
    cy.get('[data-testid="submit-customer-form"]').click();
    
    // Verify SMS verification component appears
    cy.get('[data-testid="sms-verification"]').should('be.visible');
    cy.get('[data-testid="verification-message"]')
      .should('contain', 'Un cod de verificare a fost trimis');
    
    // Step 8: Complete SMS verification (mock)
    cy.log('Step 8: Complete SMS verification');
    
    // In a real test, we would need to mock the SMS service
    // For now, we'll simulate entering the verification code
    cy.get('[data-testid="verification-code-input"]').type('123456');
    cy.get('[data-testid="verify-code-button"]').click();
    
    // Mock successful verification response
    cy.intercept('POST', '/api/sms/confirm', {
      statusCode: 200,
      body: {
        success: true,
        message: 'Codul de verificare este corect',
        session_id: 'mock-session-123'
      }
    }).as('smsVerification');
    
    cy.wait('@smsVerification');
    
    // Step 9: Complete order
    cy.log('Step 9: Complete order');
    
    // Verify order summary appears
    cy.get('[data-testid="order-summary"]').should('be.visible');
    cy.get('[data-testid="order-total"]').should('be.visible');
    
    // Mock order creation
    cy.intercept('POST', '/api/orders', {
      statusCode: 201,
      body: {
        success: true,
        order_number: 'ORD-2024-001',
        message: 'Comanda a fost plasată cu succes',
        order: {
          id: 'order-123',
          order_number: 'ORD-2024-001',
          status: 'pending',
          total: 75.50,
          items: [
            {
              product_name: 'Mere Golden',
              quantity: 3,
              price: 25.17
            }
          ]
        }
      }
    }).as('createOrder');
    
    // Place order
    cy.get('[data-testid="place-order-button"]').click();
    cy.wait('@createOrder');
    
    // Step 10: Verify order confirmation
    cy.log('Step 10: Verify order confirmation');
    
    // Should redirect to order confirmation page
    cy.url().should('include', '/confirmare-comanda/ORD-2024-001');
    
    // Verify order confirmation page
    cy.get('[data-testid="order-confirmation"]').should('be.visible');
    cy.get('[data-testid="order-number"]').should('contain', 'ORD-2024-001');
    cy.get('[data-testid="success-message"]')
      .should('contain', 'Comanda dumneavoastră a fost plasată cu succes');
    
    // Verify order details are displayed
    cy.get('[data-testid="order-details"]').should('be.visible');
    cy.get('[data-testid="customer-info"]').should('contain', 'Ion Popescu');
    cy.get('[data-testid="delivery-address"]').should('contain', 'Strada Florilor 123');
    
    // Verify next steps information
    cy.get('[data-testid="next-steps"]').should('be.visible');
    cy.get('[data-testid="contact-info"]').should('be.visible');
  });

  it('handles cart persistence across page refreshes', () => {
    cy.log('Testing cart persistence');
    
    // Add product to cart
    cy.visit('/produse');
    cy.get('[data-testid="product-card"]').first().within(() => {
      cy.get('[data-testid="add-to-cart-button"]').click();
    });
    
    // Verify cart has item
    cy.get('[data-testid="cart-counter"]').should('contain', '1');
    
    // Refresh page
    cy.reload();
    
    // Verify cart still has item
    cy.get('[data-testid="cart-counter"]').should('contain', '1');
    
    // Navigate to cart and verify item is still there
    cy.get('[data-testid="cart-icon"]').click();
    cy.get('[data-testid="cart-item"]').should('have.length', 1);
  });

  it('validates customer form with Romanian requirements', () => {
    cy.log('Testing Romanian form validation');
    
    // Add item to cart and go to checkout
    cy.visit('/produse');
    cy.get('[data-testid="product-card"]').first().within(() => {
      cy.get('[data-testid="add-to-cart-button"]').click();
    });
    cy.get('[data-testid="cart-icon"]').click();
    cy.get('[data-testid="checkout-button"]').click();
    
    // Test empty form submission
    cy.get('[data-testid="submit-customer-form"]').click();
    cy.get('[data-testid="form-errors"]').should('be.visible');
    
    // Test invalid Romanian phone number
    cy.get('[data-testid="customer-phone"]').type('123');
    cy.get('[data-testid="submit-customer-form"]').click();
    cy.get('[data-testid="phone-error"]')
      .should('contain', 'Formatul numărului de telefon nu este valid');
    
    // Test valid Romanian phone number formats
    const validPhoneFormats = ['0721234567', '+40721234567', '0040721234567'];
    
    validPhoneFormats.forEach((phone) => {
      cy.get('[data-testid="customer-phone"]').clear().type(phone);
      cy.get('[data-testid="customer-name"]').type('Test Name');
      cy.get('[data-testid="customer-email"]').type('test@example.com');
      cy.get('[data-testid="customer-address"]').type('Test Address');
      cy.get('[data-testid="customer-city"]').type('București');
      cy.get('[data-testid="customer-county"]').select('București');
      cy.get('[data-testid="customer-postal-code"]').type('123456');
      
      cy.get('[data-testid="submit-customer-form"]').click();
      cy.get('[data-testid="phone-error"]').should('not.exist');
      
      // Reset form
      cy.reload();
      cy.get('[data-testid="customer-form"]').should('be.visible');
    });
  });

  it('handles network errors gracefully', () => {
    cy.log('Testing network error handling');
    
    // Mock network error for products
    cy.intercept('GET', '/api/products', {
      statusCode: 500,
      body: { error: 'Server error' }
    }).as('productsError');
    
    cy.visit('/produse');
    cy.wait('@productsError');
    
    // Verify error message is displayed
    cy.get('[data-testid="error-message"]')
      .should('be.visible')
      .should('contain', 'Eroare la încărcarea produselor');
    
    // Verify retry functionality
    cy.get('[data-testid="retry-button"]').should('be.visible');
  });

  it('works correctly on mobile devices', () => {
    cy.log('Testing mobile responsiveness');
    
    // Set mobile viewport
    cy.viewport(375, 667); // iPhone SE size
    
    // Test mobile navigation
    cy.visit('/');
    cy.get('[data-testid="mobile-menu-button"]').should('be.visible');
    cy.get('[data-testid="mobile-menu-button"]').click();
    cy.get('[data-testid="mobile-menu"]').should('be.visible');
    
    // Test mobile product grid
    cy.visit('/produse');
    cy.get('[data-testid="product-grid"]').should('be.visible');
    cy.get('[data-testid="product-card"]').should('be.visible');
    
    // Verify touch-friendly buttons
    cy.get('[data-testid="add-to-cart-button"]').should('have.css', 'min-height');
    
    // Test mobile cart
    cy.get('[data-testid="product-card"]').first().within(() => {
      cy.get('[data-testid="add-to-cart-button"]').click();
    });
    
    cy.get('[data-testid="cart-icon"]').click();
    cy.get('[data-testid="cart-page"]').should('be.visible');
    
    // Test mobile checkout form
    cy.get('[data-testid="checkout-button"]').click();
    cy.get('[data-testid="customer-form"]').should('be.visible');
    
    // Verify form is mobile-optimized
    cy.get('[data-testid="customer-name"]').should('be.visible');
    cy.get('[data-testid="customer-phone"]').should('have.attr', 'type', 'tel');
  });

  it('supports Romanian language and formatting', () => {
    cy.log('Testing Romanian localization');
    
    cy.visit('/');
    
    // Verify Romanian text content
    cy.get('[data-testid="welcome-message"]')
      .should('contain', 'Bun venit la Pe Foc de Lemne');
    
    // Test Romanian product categories
    cy.visit('/produse');
    cy.get('[data-testid="category-filter"]').within(() => {
      cy.get('option').should('contain', 'Fructe');
      cy.get('option').should('contain', 'Legume');
      cy.get('option').should('contain', 'Produse lactate');
    });
    
    // Test Romanian currency formatting
    cy.get('[data-testid="product-card"]').first().within(() => {
      cy.get('[data-testid="product-price"]').should('contain', 'RON');
    });
    
    // Test Romanian form labels and messages
    cy.get('[data-testid="product-card"]').first().within(() => {
      cy.get('[data-testid="add-to-cart-button"]').click();
    });
    
    cy.get('[data-testid="cart-icon"]').click();
    cy.get('[data-testid="checkout-button"]').click();
    
    cy.get('[data-testid="customer-form"]').within(() => {
      cy.get('label[for="customer-name"]').should('contain', 'Nume complet');
      cy.get('label[for="customer-phone"]').should('contain', 'Număr de telefon');
      cy.get('label[for="customer-email"]').should('contain', 'Adresa de email');
    });
  });
});