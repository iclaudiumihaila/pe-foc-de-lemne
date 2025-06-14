// Custom Cypress commands for the Local Producer Web Application

// Authentication commands
Cypress.Commands.add('loginAsAdmin', (username = 'admin', password = 'admin123') => {
  cy.session([username, password], () => {
    cy.request({
      method: 'POST',
      url: '/api/auth/login',
      body: { username, password }
    }).then((response) => {
      window.localStorage.setItem('adminToken', response.body.token);
      window.localStorage.setItem('adminUser', JSON.stringify(response.body.admin));
    });
  });
});

// Cart management commands
Cypress.Commands.add('clearCart', () => {
  cy.window().then((win) => {
    win.localStorage.removeItem('cart');
    win.localStorage.removeItem('cartSession');
  });
});

Cypress.Commands.add('addProductToCart', (productId, quantity = 1) => {
  cy.request({
    method: 'POST',
    url: '/api/cart',
    body: {
      product_id: productId,
      quantity: quantity,
      session_id: 'test-session-123'
    }
  });
});

// Database management commands
Cypress.Commands.add('seedDatabase', () => {
  cy.task('seedDatabase', {
    categories: [
      { id: 'cat-1', name: 'Fructe', description: 'Fructe proaspete de sezon' },
      { id: 'cat-2', name: 'Legume', description: 'Legume proaspete din grădină' },
      { id: 'cat-3', name: 'Produse lactate', description: 'Lapte, brânzeturi și alte produse lactate' }
    ],
    products: [
      {
        id: 'prod-1',
        name: 'Mere Golden',
        category_id: 'cat-1',
        price: 8.99,
        producer: 'Ferma Ionescu',
        description: 'Mere Golden proaspete, cultivate ecologic',
        stock: 50,
        status: 'active'
      },
      {
        id: 'prod-2',
        name: 'Roșii cherry',
        category_id: 'cat-2',
        price: 12.50,
        producer: 'Grădina Verde',
        description: 'Roșii cherry dulci și aromate',
        stock: 25,
        status: 'active'
      },
      {
        id: 'prod-3',
        name: 'Brânză de capră',
        category_id: 'cat-3',
        price: 35.00,
        producer: 'Ferma Alpina',
        description: 'Brânză de capră artizanală, maturată 3 luni',
        stock: 15,
        status: 'active'
      }
    ]
  });
});

Cypress.Commands.add('clearDatabase', () => {
  cy.task('clearDatabase');
});

// Romanian-specific commands
Cypress.Commands.add('fillRomanianCustomerForm', (customerData = {}) => {
  const defaultData = {
    name: 'Ion Popescu',
    phone: '0721234567',
    email: 'ion.popescu@example.com',
    address: 'Strada Florilor 123',
    city: 'București',
    county: 'București',
    postalCode: '123456',
    notes: 'Vă rog să sunați înainte de livrare'
  };
  
  const data = { ...defaultData, ...customerData };
  
  cy.get('[data-testid="customer-name"]').type(data.name);
  cy.get('[data-testid="customer-phone"]').type(data.phone);
  cy.get('[data-testid="customer-email"]').type(data.email);
  cy.get('[data-testid="customer-address"]').type(data.address);
  cy.get('[data-testid="customer-city"]').type(data.city);
  cy.get('[data-testid="customer-county"]').select(data.county);
  cy.get('[data-testid="customer-postal-code"]').type(data.postalCode);
  
  if (data.notes) {
    cy.get('[data-testid="delivery-notes"]').type(data.notes);
  }
});

Cypress.Commands.add('verifyRomanianPhoneFormat', (phoneSelector) => {
  const testCases = [
    { input: '0721234567', expected: '+40721234567', valid: true },
    { input: '+40721234567', expected: '+40721234567', valid: true },
    { input: '0040721234567', expected: '+40721234567', valid: true },
    { input: '072123456', expected: null, valid: false },
    { input: '123456', expected: null, valid: false }
  ];
  
  testCases.forEach(testCase => {
    cy.get(phoneSelector).clear().type(testCase.input);
    
    if (testCase.valid) {
      cy.get('[data-testid*="phone-error"]').should('not.exist');
    } else {
      cy.get('form').submit();
      cy.get('[data-testid*="phone-error"]').should('be.visible');
    }
  });
});

// SMS verification mock commands
Cypress.Commands.add('mockSMSVerification', (phoneNumber, verificationCode = '123456') => {
  // Mock SMS send request
  cy.intercept('POST', '/api/sms/verify', {
    statusCode: 200,
    body: {
      success: true,
      message: 'Codul de verificare a fost trimis cu succes',
      session_id: 'test-sms-session-123'
    }
  }).as('sendSMS');
  
  // Mock SMS confirmation request
  cy.intercept('POST', '/api/sms/confirm', (req) => {
    if (req.body.code === verificationCode) {
      req.reply({
        statusCode: 200,
        body: {
          success: true,
          message: 'Codul de verificare este corect',
          verified: true,
          session_id: 'verified-session-123'
        }
      });
    } else {
      req.reply({
        statusCode: 400,
        body: {
          success: false,
          message: 'Codul de verificare este incorect'
        }
      });
    }
  }).as('confirmSMS');
});

// Product management commands
Cypress.Commands.add('createProduct', (productData) => {
  const defaultProduct = {
    name: 'Produs Test',
    category: 'Fructe',
    price: 10.00,
    producer: 'Producător Test',
    description: 'Descriere produs test',
    stock: 100
  };
  
  const product = { ...defaultProduct, ...productData };
  
  cy.get('[data-testid="add-product-button"]').click();
  cy.get('[data-testid="product-name"]').type(product.name);
  cy.get('[data-testid="product-category"]').select(product.category);
  cy.get('[data-testid="product-price"]').type(product.price.toString());
  cy.get('[data-testid="product-producer"]').type(product.producer);
  cy.get('[data-testid="product-description"]').type(product.description);
  cy.get('[data-testid="product-stock"]').type(product.stock.toString());
  cy.get('[data-testid="save-product-button"]').click();
});

// Order management commands
Cypress.Commands.add('createTestOrder', (orderData = {}) => {
  const defaultOrder = {
    customer_name: 'Test Customer',
    customer_phone: '+40721234567',
    customer_email: 'test@example.com',
    items: [
      { product_id: 'prod-1', quantity: 2, price: 8.99 }
    ],
    total: 17.98,
    status: 'pending'
  };
  
  const order = { ...defaultOrder, ...orderData };
  
  cy.request({
    method: 'POST',
    url: '/api/orders',
    body: order
  }).then((response) => {
    return response.body.order;
  });
});

// Performance testing commands
Cypress.Commands.add('measureLoadTime', (url) => {
  cy.visit(url);
  cy.window().then((win) => {
    cy.wrap(win.performance.timing).should((timing) => {
      const loadTime = timing.loadEventEnd - timing.navigationStart;
      expect(loadTime).to.be.lessThan(5000); // 5 seconds
    });
  });
});

// Accessibility testing commands
Cypress.Commands.add('checkA11y', () => {
  // Check for images without alt text
  cy.get('img:not([alt])').should('not.exist');
  
  // Check for form inputs without labels
  cy.get('input, select, textarea').each(($el) => {
    const id = $el.attr('id');
    if (id) {
      cy.get(`label[for="${id}"]`).should('exist');
    }
  });
  
  // Check for buttons without accessible text
  cy.get('button').each(($btn) => {
    const text = $btn.text().trim();
    const ariaLabel = $btn.attr('aria-label');
    const title = $btn.attr('title');
    
    expect(text || ariaLabel || title).to.not.be.empty;
  });
  
  // Check color contrast (basic check)
  cy.get('*').each(($el) => {
    const computedStyle = window.getComputedStyle($el[0]);
    const bgColor = computedStyle.backgroundColor;
    const textColor = computedStyle.color;
    
    // Skip elements with transparent backgrounds
    if (bgColor !== 'rgba(0, 0, 0, 0)' && textColor !== 'rgba(0, 0, 0, 0)') {
      // Basic contrast check - this is simplified
      // In a real scenario, you'd use a proper contrast calculation
      expect(bgColor).to.not.equal(textColor);
    }
  });
});

// Mobile testing commands
Cypress.Commands.add('testMobileLayout', (viewports = [375, 768, 1024]) => {
  viewports.forEach((width) => {
    cy.viewport(width, 667);
    
    // Check that content doesn't overflow
    cy.get('body').should(($body) => {
      expect($body[0].scrollWidth).to.be.lte(width + 1);
    });
    
    // Check navigation layout
    if (width <= 768) {
      cy.get('[data-testid="mobile-menu-button"]').should('be.visible');
      cy.get('[data-testid="desktop-nav"]').should('not.be.visible');
    } else {
      cy.get('[data-testid="desktop-nav"]').should('be.visible');
      cy.get('[data-testid="mobile-menu-button"]').should('not.be.visible');
    }
  });
});

// Error handling commands
Cypress.Commands.add('testErrorStates', (apiEndpoint) => {
  // Test 500 server error
  cy.intercept('GET', apiEndpoint, {
    statusCode: 500,
    body: { error: 'Internal server error' }
  }).as('serverError');
  
  cy.reload();
  cy.wait('@serverError');
  cy.get('[data-testid*="error"]').should('be.visible');
  cy.get('[data-testid*="retry"]').should('be.visible');
  
  // Test network error
  cy.intercept('GET', apiEndpoint, { forceNetworkError: true }).as('networkError');
  
  cy.get('[data-testid*="retry"]').click();
  cy.wait('@networkError');
  cy.get('[data-testid*="error"]').should('contain', 'eroare de conexiune');
});

// Form validation commands
Cypress.Commands.add('testRequiredFields', (formSelector, requiredFields) => {
  requiredFields.forEach(fieldSelector => {
    // Clear the field and try to submit
    cy.get(formSelector).within(() => {
      cy.get(fieldSelector).clear();
      cy.get('[type="submit"], [data-testid*="submit"]').click();
      
      // Should show validation error
      cy.get('[data-testid*="error"]').should('be.visible');
    });
  });
});

// Search functionality commands
Cypress.Commands.add('testSearch', (searchTerm, expectedResults) => {
  cy.get('[data-testid="search-input"]').type(searchTerm);
  cy.get('[data-testid="search-button"]').click();
  
  // Verify search results
  if (expectedResults > 0) {
    cy.get('[data-testid="product-card"]').should('have.length.at.least', expectedResults);
    cy.get('[data-testid="product-card"]').each(($card) => {
      cy.wrap($card).should('contain', searchTerm);
    });
  } else {
    cy.get('[data-testid="no-results"]').should('be.visible');
  }
});

// Romanian currency formatting command
Cypress.Commands.add('verifyRONCurrency', (priceSelector, expectedAmount) => {
  cy.get(priceSelector).should(($price) => {
    const text = $price.text();
    expect(text).to.include('RON');
    expect(text).to.include(expectedAmount.toFixed(2));
  });
});

// Cookie consent commands
Cypress.Commands.add('acceptCookies', () => {
  cy.get('[data-testid="cookie-consent"]').should('be.visible');
  cy.get('[data-testid="accept-cookies"]').click();
  cy.get('[data-testid="cookie-consent"]').should('not.exist');
});

Cypress.Commands.add('rejectCookies', () => {
  cy.get('[data-testid="cookie-consent"]').should('be.visible');
  cy.get('[data-testid="reject-cookies"]').click();
  cy.get('[data-testid="cookie-consent"]').should('not.exist');
});

// Wait for page to be fully loaded
Cypress.Commands.add('waitForPageLoad', () => {
  cy.get('[data-testid*="loading"]').should('not.exist');
  cy.get('body').should('be.visible');
});

// Custom assertion for Romanian text content
Cypress.Commands.add('shouldHaveRomanianContent', { prevSubject: true }, (subject) => {
  const romanianWords = ['și', 'sau', 'cu', 'de', 'la', 'în', 'pe', 'pentru'];
  const text = subject.text().toLowerCase();
  
  const hasRomanianWords = romanianWords.some(word => text.includes(word));
  expect(hasRomanianWords).to.be.true;
  
  return subject;
});