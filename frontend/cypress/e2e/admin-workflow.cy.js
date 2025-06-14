/**
 * End-to-End Admin Workflow Tests
 * 
 * Tests the complete admin workflow including authentication,
 * product management, order management, and category management
 */

describe('Admin Workflow - Complete Management Flow', () => {
  beforeEach(() => {
    // Clear any existing auth data
    cy.clearLocalStorage();
    cy.clearCookies();
    
    // Mock admin authentication
    cy.intercept('POST', '/api/auth/login', {
      statusCode: 200,
      body: {
        success: true,
        token: 'mock-admin-jwt-token',
        admin: {
          id: 'admin-123',
          username: 'admin',
          permissions: ['products', 'orders', 'categories']
        }
      }
    }).as('adminLogin');
  });

  it('completes full admin workflow: login → manage products → process orders', () => {
    // Step 1: Admin login
    cy.log('Step 1: Admin login');
    
    cy.visit('/admin/login');
    cy.get('[data-testid="admin-login-page"]').should('be.visible');
    
    // Fill login form
    cy.get('[data-testid="username-input"]').type('admin');
    cy.get('[data-testid="password-input"]').type('admin123');
    cy.get('[data-testid="login-button"]').click();
    
    cy.wait('@adminLogin');
    
    // Should redirect to admin dashboard
    cy.url().should('include', '/admin/dashboard');
    cy.get('[data-testid="admin-dashboard"]').should('be.visible');
    
    // Step 2: Navigate to product management
    cy.log('Step 2: Navigate to product management');
    
    cy.get('[data-testid="nav-products"]').click();
    cy.get('[data-testid="product-manager"]').should('be.visible');
    
    // Mock products API
    cy.intercept('GET', '/api/products', {
      statusCode: 200,
      body: {
        success: true,
        products: [
          {
            id: 'product-1',
            name: 'Mere Golden',
            category: 'Fructe',
            price: 8.99,
            producer: 'Ferma Ionescu',
            status: 'active',
            stock: 50
          },
          {
            id: 'product-2',
            name: 'Roșii cherry',
            category: 'Legume',
            price: 12.50,
            producer: 'Grădina Verde',
            status: 'active',
            stock: 25
          }
        ]
      }
    }).as('getProducts');
    
    cy.wait('@getProducts');
    
    // Verify products are displayed
    cy.get('[data-testid="product-list"]').should('be.visible');
    cy.get('[data-testid="product-row"]').should('have.length', 2);
    
    // Step 3: Create new product
    cy.log('Step 3: Create new product');
    
    cy.get('[data-testid="add-product-button"]').click();
    cy.get('[data-testid="product-form"]').should('be.visible');
    
    // Fill product form
    cy.get('[data-testid="product-name"]').type('Brânză de capră');
    cy.get('[data-testid="product-category"]').select('Produse lactate');
    cy.get('[data-testid="product-price"]').type('35.00');
    cy.get('[data-testid="product-producer"]').type('Ferma Alpina');
    cy.get('[data-testid="product-description"]').type('Brânză de capră artizanală, maturată 3 luni');
    cy.get('[data-testid="product-stock"]').type('15');
    
    // Mock product creation
    cy.intercept('POST', '/api/admin/products', {
      statusCode: 201,
      body: {
        success: true,
        product: {
          id: 'product-3',
          name: 'Brânză de capră',
          category: 'Produse lactate',
          price: 35.00,
          producer: 'Ferma Alpina',
          description: 'Brânză de capră artizanală, maturată 3 luni',
          stock: 15,
          status: 'active'
        }
      }
    }).as('createProduct');
    
    cy.get('[data-testid="save-product-button"]').click();
    cy.wait('@createProduct');
    
    // Verify success message
    cy.get('[data-testid="success-message"]')
      .should('be.visible')
      .should('contain', 'Produsul a fost adăugat cu succes');
    
    // Step 4: Edit existing product
    cy.log('Step 4: Edit existing product');
    
    // Mock updated products list
    cy.intercept('GET', '/api/products', {
      statusCode: 200,
      body: {
        success: true,
        products: [
          {
            id: 'product-1',
            name: 'Mere Golden',
            category: 'Fructe',
            price: 8.99,
            producer: 'Ferma Ionescu',
            status: 'active',
            stock: 50
          },
          {
            id: 'product-2',
            name: 'Roșii cherry',
            category: 'Legume',
            price: 12.50,
            producer: 'Grădina Verde',
            status: 'active',
            stock: 25
          },
          {
            id: 'product-3',
            name: 'Brânză de capră',
            category: 'Produse lactate',
            price: 35.00,
            producer: 'Ferma Alpina',
            status: 'active',
            stock: 15
          }
        ]
      }
    }).as('getUpdatedProducts');
    
    cy.wait('@getUpdatedProducts');
    
    // Edit first product
    cy.get('[data-testid="product-row"]').first().within(() => {
      cy.get('[data-testid="edit-product-button"]').click();
    });
    
    cy.get('[data-testid="product-form"]').should('be.visible');
    
    // Update price
    cy.get('[data-testid="product-price"]').clear().type('9.50');
    cy.get('[data-testid="product-stock"]').clear().type('75');
    
    // Mock product update
    cy.intercept('PUT', '/api/admin/products/product-1', {
      statusCode: 200,
      body: {
        success: true,
        product: {
          id: 'product-1',
          name: 'Mere Golden',
          category: 'Fructe',
          price: 9.50,
          producer: 'Ferma Ionescu',
          status: 'active',
          stock: 75
        }
      }
    }).as('updateProduct');
    
    cy.get('[data-testid="save-product-button"]').click();
    cy.wait('@updateProduct');
    
    // Verify success message
    cy.get('[data-testid="success-message"]')
      .should('be.visible')
      .should('contain', 'Produsul a fost actualizat cu succes');
    
    // Step 5: Navigate to order management
    cy.log('Step 5: Navigate to order management');
    
    cy.get('[data-testid="nav-orders"]').click();
    cy.get('[data-testid="order-manager"]').should('be.visible');
    
    // Mock orders API
    cy.intercept('GET', '/api/admin/orders', {
      statusCode: 200,
      body: {
        success: true,
        orders: [
          {
            id: 'order-1',
            order_number: 'ORD-2024-001',
            customer_name: 'Maria Popescu',
            customer_phone: '+40721234567',
            status: 'pending',
            total: 45.50,
            created_at: '2024-12-14T10:30:00Z',
            items: [
              {
                product_name: 'Mere Golden',
                quantity: 2,
                price: 8.99
              },
              {
                product_name: 'Roșii cherry',
                quantity: 1,
                price: 12.50
              }
            ]
          },
          {
            id: 'order-2',
            order_number: 'ORD-2024-002',
            customer_name: 'Ion Marinescu',
            customer_phone: '+40722345678',
            status: 'confirmed',
            total: 35.00,
            created_at: '2024-12-14T09:15:00Z',
            items: [
              {
                product_name: 'Brânză de capră',
                quantity: 1,
                price: 35.00
              }
            ]
          }
        ]
      }
    }).as('getOrders');
    
    cy.wait('@getOrders');
    
    // Verify orders are displayed
    cy.get('[data-testid="order-list"]').should('be.visible');
    cy.get('[data-testid="order-row"]').should('have.length', 2);
    
    // Step 6: Update order status
    cy.log('Step 6: Update order status');
    
    // Update first order status
    cy.get('[data-testid="order-row"]').first().within(() => {
      cy.get('[data-testid="order-status"]').should('contain', 'pending');
      cy.get('[data-testid="status-select"]').select('confirmed');
    });
    
    // Mock order status update
    cy.intercept('PUT', '/api/admin/orders/order-1/status', {
      statusCode: 200,
      body: {
        success: true,
        order: {
          id: 'order-1',
          status: 'confirmed'
        }
      }
    }).as('updateOrderStatus');
    
    cy.get('[data-testid="order-row"]').first().within(() => {
      cy.get('[data-testid="update-status-button"]').click();
    });
    
    cy.wait('@updateOrderStatus');
    
    // Verify success message
    cy.get('[data-testid="success-message"]')
      .should('be.visible')
      .should('contain', 'Statusul comenzii a fost actualizat');
    
    // Step 7: View order details
    cy.log('Step 7: View order details');
    
    cy.get('[data-testid="order-row"]').first().within(() => {
      cy.get('[data-testid="view-order-button"]').click();
    });
    
    cy.get('[data-testid="order-details-modal"]').should('be.visible');
    
    // Verify order details
    cy.get('[data-testid="order-number"]').should('contain', 'ORD-2024-001');
    cy.get('[data-testid="customer-name"]').should('contain', 'Maria Popescu');
    cy.get('[data-testid="customer-phone"]').should('contain', '+407***4567'); // Masked
    cy.get('[data-testid="order-total"]').should('contain', '45.50 RON');
    
    // Verify order items
    cy.get('[data-testid="order-items"]').should('be.visible');
    cy.get('[data-testid="order-item"]').should('have.length', 2);
    
    // Close modal
    cy.get('[data-testid="close-modal-button"]').click();
    cy.get('[data-testid="order-details-modal"]').should('not.exist');
    
    // Step 8: Navigate to category management
    cy.log('Step 8: Navigate to category management');
    
    cy.get('[data-testid="nav-categories"]').click();
    cy.get('[data-testid="category-manager"]').should('be.visible');
    
    // Mock categories API
    cy.intercept('GET', '/api/categories', {
      statusCode: 200,
      body: {
        success: true,
        categories: [
          {
            id: 'cat-1',
            name: 'Fructe',
            description: 'Fructe proaspete de sezon',
            status: 'active'
          },
          {
            id: 'cat-2',
            name: 'Legume',
            description: 'Legume proaspete din grădină',
            status: 'active'
          },
          {
            id: 'cat-3',
            name: 'Produse lactate',
            description: 'Lapte, brânzeturi și alte produse lactate',
            status: 'active'
          }
        ]
      }
    }).as('getCategories');
    
    cy.wait('@getCategories');
    
    // Verify categories are displayed
    cy.get('[data-testid="category-list"]').should('be.visible');
    cy.get('[data-testid="category-row"]').should('have.length', 3);
    
    // Step 9: Create new category
    cy.log('Step 9: Create new category');
    
    cy.get('[data-testid="add-category-button"]').click();
    cy.get('[data-testid="category-form"]').should('be.visible');
    
    // Fill category form
    cy.get('[data-testid="category-name"]').type('Băuturi');
    cy.get('[data-testid="category-description"]').type('Băuturi naturale și artizanale');
    
    // Mock category creation
    cy.intercept('POST', '/api/admin/categories', {
      statusCode: 201,
      body: {
        success: true,
        category: {
          id: 'cat-4',
          name: 'Băuturi',
          description: 'Băuturi naturale și artizanale',
          status: 'active'
        }
      }
    }).as('createCategory');
    
    cy.get('[data-testid="save-category-button"]').click();
    cy.wait('@createCategory');
    
    // Verify success message
    cy.get('[data-testid="success-message"]')
      .should('be.visible')
      .should('contain', 'Categoria a fost adăugată cu succes');
    
    // Step 10: Admin logout
    cy.log('Step 10: Admin logout');
    
    cy.get('[data-testid="admin-menu"]').click();
    cy.get('[data-testid="logout-button"]').click();
    
    // Should redirect to login page
    cy.url().should('include', '/admin/login');
    cy.get('[data-testid="admin-login-page"]').should('be.visible');
  });

  it('handles admin authentication and authorization', () => {
    cy.log('Testing admin authentication');
    
    // Test accessing admin area without authentication
    cy.visit('/admin/dashboard');
    cy.url().should('include', '/admin/login');
    
    // Test invalid login credentials
    cy.intercept('POST', '/api/auth/login', {
      statusCode: 401,
      body: {
        success: false,
        message: 'Credențiale invalide'
      }
    }).as('invalidLogin');
    
    cy.get('[data-testid="username-input"]').type('wrong');
    cy.get('[data-testid="password-input"]').type('wrong');
    cy.get('[data-testid="login-button"]').click();
    
    cy.wait('@invalidLogin');
    
    // Verify error message
    cy.get('[data-testid="error-message"]')
      .should('be.visible')
      .should('contain', 'Credențiale invalide');
    
    // Test successful login
    cy.intercept('POST', '/api/auth/login', {
      statusCode: 200,
      body: {
        success: true,
        token: 'valid-jwt-token',
        admin: {
          id: 'admin-123',
          username: 'admin',
          permissions: ['products', 'orders']
        }
      }
    }).as('validLogin');
    
    cy.get('[data-testid="username-input"]').clear().type('admin');
    cy.get('[data-testid="password-input"]').clear().type('correct');
    cy.get('[data-testid="login-button"]').click();
    
    cy.wait('@validLogin');
    
    // Should redirect to dashboard
    cy.url().should('include', '/admin/dashboard');
  });

  it('validates admin forms with Romanian requirements', () => {
    cy.log('Testing admin form validation');
    
    // Login first
    cy.visit('/admin/login');
    cy.get('[data-testid="username-input"]').type('admin');
    cy.get('[data-testid="password-input"]').type('admin123');
    cy.get('[data-testid="login-button"]').click();
    cy.wait('@adminLogin');
    
    // Test product form validation
    cy.get('[data-testid="nav-products"]').click();
    cy.get('[data-testid="add-product-button"]').click();
    
    // Test empty form submission
    cy.get('[data-testid="save-product-button"]').click();
    cy.get('[data-testid="form-errors"]').should('be.visible');
    
    // Test invalid price format
    cy.get('[data-testid="product-name"]').type('Test Product');
    cy.get('[data-testid="product-price"]').type('invalid');
    cy.get('[data-testid="save-product-button"]').click();
    cy.get('[data-testid="price-error"]')
      .should('contain', 'Prețul trebuie să fie un număr valid');
    
    // Test negative price
    cy.get('[data-testid="product-price"]').clear().type('-10');
    cy.get('[data-testid="save-product-button"]').click();
    cy.get('[data-testid="price-error"]')
      .should('contain', 'Prețul nu poate fi negativ');
    
    // Test Romanian specific validations
    cy.get('[data-testid="product-price"]').clear().type('150000');
    cy.get('[data-testid="save-product-button"]').click();
    cy.get('[data-testid="price-error"]')
      .should('contain', 'Prețul nu poate depăși');
  });

  it('handles API errors gracefully', () => {
    cy.log('Testing admin error handling');
    
    // Login first
    cy.visit('/admin/login');
    cy.get('[data-testid="username-input"]').type('admin');
    cy.get('[data-testid="password-input"]').type('admin123');
    cy.get('[data-testid="login-button"]').click();
    cy.wait('@adminLogin');
    
    // Mock API error for products
    cy.intercept('GET', '/api/products', {
      statusCode: 500,
      body: { error: 'Internal server error' }
    }).as('productsError');
    
    cy.get('[data-testid="nav-products"]').click();
    cy.wait('@productsError');
    
    // Verify error message
    cy.get('[data-testid="error-message"]')
      .should('be.visible')
      .should('contain', 'Eroare la încărcarea produselor');
    
    // Test retry functionality
    cy.get('[data-testid="retry-button"]').should('be.visible');
    
    // Mock successful retry
    cy.intercept('GET', '/api/products', {
      statusCode: 200,
      body: {
        success: true,
        products: []
      }
    }).as('productsSuccess');
    
    cy.get('[data-testid="retry-button"]').click();
    cy.wait('@productsSuccess');
    
    // Error message should disappear
    cy.get('[data-testid="error-message"]').should('not.exist');
  });

  it('provides Romanian admin interface', () => {
    cy.log('Testing Romanian admin localization');
    
    // Login
    cy.visit('/admin/login');
    cy.get('[data-testid="username-input"]').type('admin');
    cy.get('[data-testid="password-input"]').type('admin123');
    cy.get('[data-testid="login-button"]').click();
    cy.wait('@adminLogin');
    
    // Verify Romanian dashboard text
    cy.get('[data-testid="dashboard-title"]')
      .should('contain', 'Panou de administrare');
    
    // Check Romanian navigation labels
    cy.get('[data-testid="nav-products"]').should('contain', 'Produse');
    cy.get('[data-testid="nav-orders"]').should('contain', 'Comenzi');
    cy.get('[data-testid="nav-categories"]').should('contain', 'Categorii');
    
    // Test Romanian form labels
    cy.get('[data-testid="nav-products"]').click();
    cy.get('[data-testid="add-product-button"]').click();
    
    cy.get('label[for="product-name"]').should('contain', 'Nume produs');
    cy.get('label[for="product-price"]').should('contain', 'Preț (RON)');
    cy.get('label[for="product-producer"]').should('contain', 'Producător');
    
    // Test Romanian status values
    cy.get('[data-testid="nav-orders"]').click();
    
    cy.intercept('GET', '/api/admin/orders', {
      statusCode: 200,
      body: {
        success: true,
        orders: [
          {
            id: 'order-1',
            order_number: 'ORD-2024-001',
            status: 'pending'
          }
        ]
      }
    }).as('getOrders');
    
    cy.wait('@getOrders');
    
    cy.get('[data-testid="status-select"]').within(() => {
      cy.get('option[value="pending"]').should('contain', 'În așteptare');
      cy.get('option[value="confirmed"]').should('contain', 'Confirmată');
      cy.get('option[value="delivered"]').should('contain', 'Livrată');
    });
  });

  it('handles admin permissions correctly', () => {
    cy.log('Testing admin permissions');
    
    // Mock admin with limited permissions
    cy.intercept('POST', '/api/auth/login', {
      statusCode: 200,
      body: {
        success: true,
        token: 'limited-admin-token',
        admin: {
          id: 'admin-limited',
          username: 'admin_limited',
          permissions: ['orders'] // Only orders permission
        }
      }
    }).as('limitedAdminLogin');
    
    cy.visit('/admin/login');
    cy.get('[data-testid="username-input"]').type('admin_limited');
    cy.get('[data-testid="password-input"]').type('admin123');
    cy.get('[data-testid="login-button"]').click();
    
    cy.wait('@limitedAdminLogin');
    
    // Should redirect to dashboard
    cy.url().should('include', '/admin/dashboard');
    
    // Products navigation should be disabled or hidden
    cy.get('[data-testid="nav-products"]').should('have.attr', 'disabled');
    cy.get('[data-testid="nav-categories"]').should('have.attr', 'disabled');
    
    // Orders navigation should be available
    cy.get('[data-testid="nav-orders"]').should('not.have.attr', 'disabled');
  });
});