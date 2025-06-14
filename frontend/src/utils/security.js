/**
 * Frontend Security Utilities for Local Producer Web Application
 * 
 * This module provides comprehensive frontend security utilities including
 * input validation, sanitization, and security-focused user interactions.
 */

// Romanian phone number validation regex
const ROMANIAN_PHONE_REGEX = /^(\+4|0040|0)([0-9]{9})$/;

// Romanian postal code validation regex
const ROMANIAN_POSTAL_CODE_REGEX = /^[0-9]{6}$/;

// Strong password requirements
export const PASSWORD_REQUIREMENTS = {
  minLength: 8,
  maxLength: 128,
  requireUppercase: true,
  requireLowercase: true,
  requireDigits: true,
  requireSpecial: true,
  forbiddenPatterns: [
    'password', 'parola', '123456', 'qwerty', 'admin',
    'test', 'user', 'guest', 'demo'
  ]
};

// Allowed file extensions for uploads
export const ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.gif'];
export const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

/**
 * Frontend Security Validator Class
 */
export class SecurityValidator {
  /**
   * Validate password strength according to security requirements
   * @param {string} password - Password to validate
   * @returns {Object} Validation result with details
   */
  static validatePassword(password) {
    const result = {
      isValid: true,
      errors: [],
      strengthScore: 0,
      recommendations: []
    };

    if (!password) {
      result.isValid = false;
      result.errors.push("Parola este obligatorie");
      return result;
    }

    // Length validation
    if (password.length < PASSWORD_REQUIREMENTS.minLength) {
      result.isValid = false;
      result.errors.push(`Parola trebuie să aibă cel puțin ${PASSWORD_REQUIREMENTS.minLength} caractere`);
    }

    if (password.length > PASSWORD_REQUIREMENTS.maxLength) {
      result.isValid = false;
      result.errors.push(`Parola nu poate avea mai mult de ${PASSWORD_REQUIREMENTS.maxLength} caractere`);
    }

    // Character requirements
    if (PASSWORD_REQUIREMENTS.requireUppercase && !/[A-Z]/.test(password)) {
      result.isValid = false;
      result.errors.push("Parola trebuie să conțină cel puțin o literă mare");
      result.recommendations.push("Adaugă cel puțin o literă mare (A-Z)");
    }

    if (PASSWORD_REQUIREMENTS.requireLowercase && !/[a-z]/.test(password)) {
      result.isValid = false;
      result.errors.push("Parola trebuie să conțină cel puțin o literă mică");
      result.recommendations.push("Adaugă cel puțin o literă mică (a-z)");
    }

    if (PASSWORD_REQUIREMENTS.requireDigits && !/[0-9]/.test(password)) {
      result.isValid = false;
      result.errors.push("Parola trebuie să conțină cel puțin o cifră");
      result.recommendations.push("Adaugă cel puțin o cifră (0-9)");
    }

    if (PASSWORD_REQUIREMENTS.requireSpecial && !/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      result.isValid = false;
      result.errors.push("Parola trebuie să conțină cel puțin un caracter special");
      result.recommendations.push("Adaugă cel puțin un caracter special (!@#$%^&*)");
    }

    // Forbidden patterns
    const passwordLower = password.toLowerCase();
    for (const pattern of PASSWORD_REQUIREMENTS.forbiddenPatterns) {
      if (passwordLower.includes(pattern)) {
        result.isValid = false;
        result.errors.push(`Parola nu poate conține '${pattern}'`);
      }
    }

    // Calculate strength score
    let strengthScore = 0;
    if (password.length >= 8) strengthScore += 20;
    if (password.length >= 12) strengthScore += 10;
    if (/[A-Z]/.test(password)) strengthScore += 15;
    if (/[a-z]/.test(password)) strengthScore += 15;
    if (/[0-9]/.test(password)) strengthScore += 15;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strengthScore += 15;
    if (new Set(password).size > password.length * 0.7) strengthScore += 10; // Character diversity

    result.strengthScore = Math.min(strengthScore, 100);

    return result;
  }

  /**
   * Validate email address format
   * @param {string} email - Email address to validate
   * @returns {Object} Validation result
   */
  static validateEmail(email) {
    const result = {
      isValid: true,
      errors: [],
      normalizedEmail: null
    };

    if (!email) {
      result.isValid = false;
      result.errors.push("Adresa de email este obligatorie");
      return result;
    }

    // Basic email format validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      result.isValid = false;
      result.errors.push("Formatul adresei de email nu este valid");
      return result;
    }

    // Additional validation
    const [localPart, domain] = email.split('@');
    
    if (localPart.length > 64) {
      result.isValid = false;
      result.errors.push("Partea locală a email-ului este prea lungă");
    }

    if (domain.length > 253) {
      result.isValid = false;
      result.errors.push("Domeniul email-ului este prea lung");
    }

    result.normalizedEmail = email.toLowerCase().trim();
    return result;
  }

  /**
   * Validate Romanian phone number format
   * @param {string} phone - Phone number to validate
   * @returns {Object} Validation result
   */
  static validateRomanianPhone(phone) {
    const result = {
      isValid: true,
      errors: [],
      normalizedPhone: null
    };

    if (!phone) {
      result.isValid = false;
      result.errors.push("Numărul de telefon este obligatoriu");
      return result;
    }

    // Remove spaces and dashes
    const cleanPhone = phone.replace(/[\s\-\(\)]/g, '');

    if (!ROMANIAN_PHONE_REGEX.test(cleanPhone)) {
      result.isValid = false;
      result.errors.push("Formatul numărului de telefon nu este valid pentru România");
      return result;
    }

    // Normalize to +40 format
    if (cleanPhone.startsWith('0040')) {
      result.normalizedPhone = '+4' + cleanPhone.slice(4);
    } else if (cleanPhone.startsWith('+4')) {
      result.normalizedPhone = cleanPhone;
    } else if (cleanPhone.startsWith('0')) {
      result.normalizedPhone = '+4' + cleanPhone.slice(1);
    } else {
      result.normalizedPhone = '+4' + cleanPhone;
    }

    return result;
  }

  /**
   * Sanitize user input to prevent XSS attacks
   * @param {string} input - Input text to sanitize
   * @param {number} maxLength - Maximum allowed length
   * @returns {string} Sanitized text
   */
  static sanitizeInput(input, maxLength = 1000) {
    if (!input) return '';

    // Truncate if too long
    if (input.length > maxLength) {
      input = input.slice(0, maxLength);
    }

    // HTML escape
    const htmlEscapeMap = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#x27;',
      '/': '&#x2F;'
    };

    let sanitized = input.replace(/[&<>"'/]/g, (char) => htmlEscapeMap[char]);

    // Remove null bytes and control characters
    sanitized = sanitized.replace(/[\x00-\x1f\x7f-\x9f]/g, '');

    return sanitized.trim();
  }

  /**
   * Validate product name with Romanian context
   * @param {string} name - Product name to validate
   * @returns {Object} Validation result
   */
  static validateProductName(name) {
    const result = {
      isValid: true,
      errors: [],
      sanitizedName: null
    };

    if (!name) {
      result.isValid = false;
      result.errors.push("Numele produsului este obligatoriu");
      return result;
    }

    // Sanitize
    const sanitizedName = this.sanitizeInput(name, 100);

    if (sanitizedName.length < 2) {
      result.isValid = false;
      result.errors.push("Numele produsului trebuie să aibă cel puțin 2 caractere");
    }

    if (sanitizedName.length > 100) {
      result.isValid = false;
      result.errors.push("Numele produsului nu poate depăși 100 de caractere");
    }

    // Check for inappropriate content (basic filter)
    const forbiddenWords = ['test', 'spam', 'fake'];
    const nameLower = sanitizedName.toLowerCase();
    for (const word of forbiddenWords) {
      if (nameLower.includes(word)) {
        result.isValid = false;
        result.errors.push("Numele produsului conține conținut neadecvat");
        break;
      }
    }

    result.sanitizedName = sanitizedName;
    return result;
  }

  /**
   * Validate product price
   * @param {string|number} price - Price to validate
   * @returns {Object} Validation result
   */
  static validatePrice(price) {
    const result = {
      isValid: true,
      errors: [],
      normalizedPrice: null
    };

    try {
      const priceFloat = parseFloat(price);

      if (isNaN(priceFloat)) {
        result.isValid = false;
        result.errors.push("Prețul trebuie să fie un număr valid");
      } else if (priceFloat < 0) {
        result.isValid = false;
        result.errors.push("Prețul nu poate fi negativ");
      } else if (priceFloat === 0) {
        result.isValid = false;
        result.errors.push("Prețul trebuie să fie mai mare decât 0");
      } else if (priceFloat > 99999.99) {
        result.isValid = false;
        result.errors.push("Prețul nu poate depăși 99,999.99 RON");
      } else {
        // Round to 2 decimal places
        result.normalizedPrice = Math.round(priceFloat * 100) / 100;
      }
    } catch (error) {
      result.isValid = false;
      result.errors.push("Prețul trebuie să fie un număr valid");
    }

    return result;
  }

  /**
   * Validate file upload security
   * @param {File} file - File to validate
   * @returns {Object} Validation result
   */
  static validateFileUpload(file) {
    const result = {
      isValid: true,
      errors: [],
      safeFilename: null
    };

    if (!file) {
      result.isValid = false;
      result.errors.push("Fișierul este obligatoriu");
      return result;
    }

    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      result.isValid = false;
      result.errors.push(`Fișierul este prea mare. Mărimea maximă permisă este ${MAX_FILE_SIZE / (1024 * 1024)}MB`);
    }

    // Check extension
    const fileName = file.name.toLowerCase();
    const fileExt = '.' + fileName.split('.').pop();
    if (!ALLOWED_IMAGE_EXTENSIONS.includes(fileExt)) {
      result.isValid = false;
      result.errors.push(`Tipul de fișier nu este permis. Extensii permise: ${ALLOWED_IMAGE_EXTENSIONS.join(', ')}`);
    }

    // Generate safe filename
    const safeName = this.sanitizeInput(file.name, 255);
    const sanitizedName = safeName.replace(/[^a-zA-Z0-9._-]/g, '_');
    
    // Prevent directory traversal
    const finalName = sanitizedName.replace(/\.\./g, '_').replace(/[\/\\]/g, '_');

    result.safeFilename = finalName;
    return result;
  }
}

/**
 * Client-side CSRF token management
 */
export class CSRFProtection {
  static getMetaToken() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    return metaTag ? metaTag.getAttribute('content') : null;
  }

  static setRequestHeaders(headers = {}) {
    const token = this.getMetaToken();
    if (token) {
      headers['X-CSRF-Token'] = token;
    }
    return headers;
  }

  static createSecureForm(formElement) {
    const token = this.getMetaToken();
    if (token && formElement) {
      const csrfInput = document.createElement('input');
      csrfInput.type = 'hidden';
      csrfInput.name = 'csrf_token';
      csrfInput.value = token;
      formElement.appendChild(csrfInput);
    }
  }
}

/**
 * Secure data masking for display
 */
export class DataMasking {
  static maskPhoneNumber(phoneNumber) {
    if (!phoneNumber) return '';

    // Remove country code and formatting
    const cleanPhone = phoneNumber.replace(/^\+40/, '').replace(/[\s\-]/g, '');
    
    if (cleanPhone.length >= 4) {
      return `+40***${cleanPhone.slice(-4)}`;
    } else {
      return '+40***';
    }
  }

  static maskEmail(email) {
    if (!email || !email.includes('@')) return '***';

    const [local, domain] = email.split('@');
    
    if (local.length <= 2) {
      return '*'.repeat(local.length) + '@' + domain;
    } else {
      return local[0] + '*'.repeat(local.length - 2) + local.slice(-1) + '@' + domain;
    }
  }

  static maskAddress(address) {
    if (!address) return '';

    const words = address.split(' ');
    if (words.length <= 2) return '***';

    // Show first and last word, mask middle
    return `${words[0]} *** ${words[words.length - 1]}`;
  }
}

/**
 * Frontend rate limiting (client-side protection)
 */
export class ClientRateLimit {
  constructor() {
    this.requests = new Map();
    this.cleanupInterval = 60000; // 1 minute
    this.lastCleanup = Date.now();
  }

  isAllowed(identifier, limit, windowMs) {
    const now = Date.now();

    // Cleanup old entries periodically
    if (now - this.lastCleanup > this.cleanupInterval) {
      this.cleanup();
      this.lastCleanup = now;
    }

    // Get request history for identifier
    if (!this.requests.has(identifier)) {
      this.requests.set(identifier, []);
    }

    const requestTimes = this.requests.get(identifier);

    // Remove requests outside the window
    const cutoffTime = now - windowMs;
    const validRequests = requestTimes.filter(time => time > cutoffTime);
    this.requests.set(identifier, validRequests);

    // Check if limit exceeded
    if (validRequests.length >= limit) {
      return {
        allowed: false,
        requestsMade: validRequests.length,
        limit,
        retryAfter: windowMs
      };
    }

    // Record this request
    validRequests.push(now);

    return {
      allowed: true,
      requestsMade: validRequests.length,
      limit,
      remaining: limit - validRequests.length
    };
  }

  cleanup() {
    const cutoffTime = Date.now() - (24 * 60 * 60 * 1000); // 24 hours
    
    for (const [identifier, requestTimes] of this.requests.entries()) {
      const validRequests = requestTimes.filter(time => time > cutoffTime);
      if (validRequests.length === 0) {
        this.requests.delete(identifier);
      } else {
        this.requests.set(identifier, validRequests);
      }
    }
  }
}

/**
 * Secure local storage management
 */
export class SecureStorage {
  static setItem(key, value, encrypt = false) {
    try {
      const data = {
        value,
        timestamp: Date.now(),
        encrypted: encrypt
      };

      if (encrypt) {
        // Simple base64 encoding (not real encryption, just obfuscation)
        data.value = btoa(JSON.stringify(value));
      }

      localStorage.setItem(key, JSON.stringify(data));
      return true;
    } catch (error) {
      console.error('Failed to store data:', error);
      return false;
    }
  }

  static getItem(key, maxAge = null) {
    try {
      const stored = localStorage.getItem(key);
      if (!stored) return null;

      const data = JSON.parse(stored);

      // Check expiration
      if (maxAge && Date.now() - data.timestamp > maxAge) {
        localStorage.removeItem(key);
        return null;
      }

      if (data.encrypted) {
        // Simple base64 decoding
        return JSON.parse(atob(data.value));
      }

      return data.value;
    } catch (error) {
      console.error('Failed to retrieve data:', error);
      localStorage.removeItem(key);
      return null;
    }
  }

  static removeItem(key) {
    localStorage.removeItem(key);
  }

  static clear() {
    localStorage.clear();
  }
}

/**
 * Content Security Policy helper
 */
export class CSPHelper {
  static reportViolation(violationReport) {
    // Log CSP violations for security monitoring
    console.warn('CSP Violation:', violationReport);
    
    // In production, send to security monitoring endpoint
    if (process.env.NODE_ENV === 'production') {
      fetch('/api/security/csp-violation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(violationReport)
      }).catch(console.error);
    }
  }

  static setupViolationReporting() {
    document.addEventListener('securitypolicyviolation', (event) => {
      this.reportViolation({
        documentURI: event.documentURI,
        referrer: event.referrer,
        blockedURI: event.blockedURI,
        violatedDirective: event.violatedDirective,
        effectiveDirective: event.effectiveDirective,
        originalPolicy: event.originalPolicy,
        disposition: event.disposition,
        statusCode: event.statusCode
      });
    });
  }
}

// Initialize CSP violation reporting
if (typeof document !== 'undefined') {
  CSPHelper.setupViolationReporting();
}

// Global rate limiter instance
export const clientRateLimit = new ClientRateLimit();

// Default export with all utilities
export default {
  SecurityValidator,
  CSRFProtection,
  DataMasking,
  ClientRateLimit,
  SecureStorage,
  CSPHelper,
  clientRateLimit,
  PASSWORD_REQUIREMENTS,
  ALLOWED_IMAGE_EXTENSIONS,
  MAX_FILE_SIZE
};