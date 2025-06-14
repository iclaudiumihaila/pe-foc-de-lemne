// Cypress E2E support file
// This file is processed and loaded automatically before your test files

import './commands';
import '@cypress/code-coverage/support';

// Hide fetch/XHR requests from command log to reduce noise
const app = window.top;
if (!app.document.head.querySelector('[data-hide-command-log-request]')) {
  const style = app.document.createElement('style');
  style.innerHTML = '.command-name-request, .command-name-xhr { display: none }';
  style.setAttribute('data-hide-command-log-request', '');
  app.document.head.appendChild(style);
}

// Global error handling
Cypress.on('uncaught:exception', (err, runnable) => {
  // Returning false here prevents Cypress from failing the test
  // We'll handle errors through our error boundaries instead
  
  // Allow certain expected errors to not fail the test
  const allowedErrors = [
    'ResizeObserver loop limit exceeded',
    'Non-Error promise rejection captured',
    'Script error'
  ];
  
  const isAllowedError = allowedErrors.some(allowedError => 
    err.message.includes(allowedError)
  );
  
  if (isAllowedError) {
    return false;
  }
  
  // Log the error for debugging
  console.error('Uncaught exception:', err);
  
  // Allow the test to fail for unexpected errors
  return true;
});

// Global configuration
beforeEach(() => {
  // Set up common test environment
  cy.window().then((win) => {
    // Mock Google Analytics to prevent external requests
    win.gtag = cy.stub();
    win.dataLayer = [];
    
    // Mock performance API if not available
    if (!win.performance) {
      win.performance = {
        now: () => Date.now(),
        mark: cy.stub(),
        measure: cy.stub()
      };
    }
    
    // Mock localStorage and sessionStorage methods
    if (!win.localStorage.clear) {
      win.localStorage.clear = cy.stub();
    }
    
    // Set up test data attributes helper
    win.testId = (id) => `[data-testid="${id}"]`;
  });
  
  // Common API mocks
  cy.intercept('GET', '/api/health', {
    statusCode: 200,
    body: { status: 'ok', timestamp: new Date().toISOString() }
  }).as('healthCheck');
  
  // Mock categories for consistent testing
  cy.intercept('GET', '/api/categories', {
    statusCode: 200,
    body: {
      success: true,
      categories: [
        { id: 'cat-1', name: 'Fructe', description: 'Fructe proaspete' },
        { id: 'cat-2', name: 'Legume', description: 'Legume de sezon' },
        { id: 'cat-3', name: 'Produse lactate', description: 'Lapte și brânzeturi' },
        { id: 'cat-4', name: 'Carne', description: 'Carne proaspătă' },
        { id: 'cat-5', name: 'Băuturi', description: 'Băuturi naturale' }
      ]
    }
  }).as('getCategories');
});

// Custom assertions for Romanian locale
Cypress.Commands.add('shouldContainRomanianText', (subject, expectedTexts) => {
  if (Array.isArray(expectedTexts)) {
    expectedTexts.forEach(text => {
      cy.wrap(subject).should('contain', text);
    });
  } else {
    cy.wrap(subject).should('contain', expectedTexts);
  }
});

// Helper for Romanian phone number testing
Cypress.Commands.add('testRomanianPhoneFormats', (selector) => {
  const validFormats = [
    '0721234567',
    '+40721234567', 
    '0040721234567',
    '0722 345 678',
    '+40 723 456 789'
  ];
  
  const invalidFormats = [
    '123',
    '072123456',
    '07212345678',
    '+41721234567',
    'abc1234567'
  ];
  
  // Test valid formats
  validFormats.forEach(phone => {
    cy.get(selector).clear().type(phone);
    cy.get('[data-testid="phone-error"]').should('not.exist');
  });
  
  // Test invalid formats
  invalidFormats.forEach(phone => {
    cy.get(selector).clear().type(phone);
    cy.get('form').submit();
    cy.get('[data-testid="phone-error"]').should('be.visible');
  });
});

// Helper for testing Romanian currency formatting
Cypress.Commands.add('shouldDisplayRomanianPrice', (subject, price) => {
  const formattedPrice = `${price.toFixed(2)} RON`;
  cy.wrap(subject).should('contain', formattedPrice);
});

// Helper for accessibility testing
Cypress.Commands.add('checkAccessibility', () => {
  // Check for basic accessibility issues
  cy.get('img').each(($img) => {
    cy.wrap($img).should('have.attr', 'alt');
  });
  
  cy.get('input, select, textarea').each(($field) => {
    const id = $field.attr('id');
    if (id) {
      cy.get(`label[for="${id}"]`).should('exist');
    }
  });
  
  cy.get('button').each(($button) => {
    const text = $button.text().trim();
    const ariaLabel = $button.attr('aria-label');
    const title = $button.attr('title');
    
    // Button should have accessible text
    expect(text || ariaLabel || title).to.not.be.empty;
  });
});

// Helper for mobile testing
Cypress.Commands.add('testMobileNavigation', () => {
  cy.viewport(375, 667);
  
  // Mobile menu should be present
  cy.get('[data-testid="mobile-menu-button"]').should('be.visible');
  
  // Desktop navigation should be hidden
  cy.get('[data-testid="desktop-nav"]').should('not.be.visible');
  
  // Test mobile menu functionality
  cy.get('[data-testid="mobile-menu-button"]').click();
  cy.get('[data-testid="mobile-menu"]').should('be.visible');
  
  // Test navigation items
  cy.get('[data-testid="mobile-nav-home"]').should('be.visible');
  cy.get('[data-testid="mobile-nav-products"]').should('be.visible');
  cy.get('[data-testid="mobile-nav-cart"]').should('be.visible');
});

// Helper for testing form validation
Cypress.Commands.add('testFormValidation', (formSelector, fields) => {
  fields.forEach(field => {
    const { selector, validValue, invalidValue, errorMessage } = field;
    
    // Test empty field
    cy.get(formSelector).within(() => {
      cy.get(selector).clear();
      cy.get('[type="submit"]').click();
      cy.get('[data-testid*="error"]').should('be.visible');
    });
    
    // Test invalid value
    if (invalidValue) {
      cy.get(formSelector).within(() => {
        cy.get(selector).clear().type(invalidValue);
        cy.get('[type="submit"]').click();
        if (errorMessage) {
          cy.get('[data-testid*="error"]').should('contain', errorMessage);
        }
      });
    }
    
    // Test valid value
    cy.get(formSelector).within(() => {
      cy.get(selector).clear().type(validValue);
      cy.get('[data-testid*="error"]').should('not.exist');
    });
  });
});

// Helper for testing loading states
Cypress.Commands.add('testLoadingStates', (triggerSelector, contentSelector) => {
  // Intercept with delay to see loading state
  cy.intercept('GET', '/api/**', (req) => {
    req.reply((res) => {
      return new Promise((resolve) => {
        setTimeout(() => resolve(res), 1000);
      });
    });
  }).as('delayedRequest');
  
  cy.get(triggerSelector).click();
  
  // Loading indicator should appear
  cy.get('[data-testid*="loading"]').should('be.visible');
  
  cy.wait('@delayedRequest');
  
  // Loading indicator should disappear
  cy.get('[data-testid*="loading"]').should('not.exist');
  
  // Content should be visible
  cy.get(contentSelector).should('be.visible');
});

// Helper for cart testing
Cypress.Commands.add('addToCartAndVerify', (productSelector) => {
  // Get initial cart count
  cy.get('[data-testid="cart-counter"]').invoke('text').then((initialCount) => {
    const initial = parseInt(initialCount) || 0;
    
    // Add product to cart
    cy.get(productSelector).within(() => {
      cy.get('[data-testid="add-to-cart-button"]').click();
    });
    
    // Verify cart count increased
    cy.get('[data-testid="cart-counter"]').should('contain', initial + 1);
  });
});

// Helper for Romanian locale testing
Cypress.Commands.add('verifyRomanianLocale', () => {
  const romanianTexts = [
    'Produse locale românești',
    'Adaugă în coș',
    'Coș de cumpărături',
    'Continua cumpărăturile',
    'Finalizează comanda'
  ];
  
  romanianTexts.forEach(text => {
    cy.get('body').should('contain', text);
  });
  
  // Check Romanian county options
  cy.get('select[data-testid*="county"]').within(() => {
    cy.get('option').should('contain', 'București');
    cy.get('option').should('contain', 'Cluj');
    cy.get('option').should('contain', 'Timiș');
  });
});

// Performance testing helper
Cypress.Commands.add('measurePageLoad', (url) => {
  cy.visit(url);
  
  cy.window().then((win) => {
    cy.wrap(win.performance.timing).then((timing) => {
      const loadTime = timing.loadEventEnd - timing.navigationStart;
      expect(loadTime).to.be.lessThan(5000); // 5 seconds max
      
      const domContentLoaded = timing.domContentLoadedEventEnd - timing.navigationStart;
      expect(domContentLoaded).to.be.lessThan(3000); // 3 seconds max
    });
  });
});