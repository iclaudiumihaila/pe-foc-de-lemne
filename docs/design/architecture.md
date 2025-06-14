# System Architecture: Local Producer Web Application

## 1. Architecture Overview

### 1.1 System Type
**Monolithic Full-Stack Web Application** with clear separation between frontend and backend services.

### 1.2 Architectural Pattern
- **Frontend**: Single Page Application (SPA) with React
- **Backend**: RESTful API with Flask
- **Database**: Document-oriented with MongoDB
- **Communication**: HTTP/JSON API, SMS via Twilio

### 1.3 High-Level Architecture
```
[Mobile/Desktop Browser] 
    ↓ HTTP/HTTPS
[React Frontend :3000]
    ↓ API Calls
[Flask Backend :8080] 
    ↓ Database Queries
[MongoDB Database]
    ↓ SMS API
[Twilio SMS Service]
```

## 2. Directory Structure

```
/Users/claudiu/Desktop/pe foc de lemne/
├── agentic_flow/           # Orchestrator management (controlled)
├── docs/                   # Documentation (controlled)
├── backend/                # Flask API application
│   ├── app/
│   │   ├── __init__.py     # Flask app factory
│   │   ├── config.py       # Configuration management
│   │   ├── models/         # MongoDB models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── product.py
│   │   │   ├── category.py
│   │   │   ├── order.py
│   │   │   └── cart.py
│   │   ├── routes/         # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py     # Authentication routes
│   │   │   ├── products.py # Product management
│   │   │   ├── categories.py # Category management
│   │   │   ├── orders.py   # Order processing
│   │   │   ├── cart.py     # Shopping cart
│   │   │   └── sms.py      # SMS verification
│   │   ├── services/       # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── product_service.py
│   │   │   ├── order_service.py
│   │   │   ├── sms_service.py
│   │   │   └── cart_service.py
│   │   ├── utils/          # Utility functions
│   │   │   ├── __init__.py
│   │   │   ├── validators.py
│   │   │   ├── helpers.py
│   │   │   └── decorators.py
│   │   └── database.py     # MongoDB connection
│   ├── tests/              # Backend tests
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_routes.py
│   │   └── test_services.py
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment variables template
│   └── run.py              # Application entry point
├── frontend/               # React application
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   │   ├── common/     # Generic components
│   │   │   │   ├── Header.jsx
│   │   │   │   ├── Footer.jsx
│   │   │   │   ├── Loading.jsx
│   │   │   │   └── ErrorMessage.jsx
│   │   │   ├── product/    # Product-related components
│   │   │   │   ├── ProductCard.jsx
│   │   │   │   ├── ProductGrid.jsx
│   │   │   │   ├── ProductDetail.jsx
│   │   │   │   └── ProductFilter.jsx
│   │   │   ├── cart/       # Shopping cart components
│   │   │   │   ├── CartItem.jsx
│   │   │   │   ├── CartSummary.jsx
│   │   │   │   └── CartDrawer.jsx
│   │   │   ├── checkout/   # Checkout flow components
│   │   │   │   ├── CustomerForm.jsx
│   │   │   │   ├── SMSVerification.jsx
│   │   │   │   └── OrderConfirmation.jsx
│   │   │   └── admin/      # Admin panel components
│   │   │       ├── ProductManager.jsx
│   │   │       ├── OrderManager.jsx
│   │   │       └── CategoryManager.jsx
│   │   ├── pages/          # Page components
│   │   │   ├── Home.jsx
│   │   │   ├── Products.jsx
│   │   │   ├── ProductDetail.jsx
│   │   │   ├── Cart.jsx
│   │   │   ├── Checkout.jsx
│   │   │   ├── OrderConfirmation.jsx
│   │   │   ├── AdminLogin.jsx
│   │   │   └── AdminDashboard.jsx
│   │   ├── hooks/          # Custom React hooks
│   │   │   ├── useCart.js
│   │   │   ├── useProducts.js
│   │   │   ├── useOrders.js
│   │   │   └── useAuth.js
│   │   ├── services/       # API communication
│   │   │   ├── api.js      # Base API configuration
│   │   │   ├── productService.js
│   │   │   ├── orderService.js
│   │   │   ├── authService.js
│   │   │   └── smsService.js
│   │   ├── context/        # React context for state
│   │   │   ├── CartContext.jsx
│   │   │   ├── AuthContext.jsx
│   │   │   └── ProductContext.jsx
│   │   ├── utils/          # Frontend utilities
│   │   │   ├── constants.js
│   │   │   ├── helpers.js
│   │   │   └── validators.js
│   │   ├── styles/         # CSS and styling
│   │   │   ├── index.css   # Tailwind imports
│   │   │   └── components.css # Custom component styles
│   │   ├── App.jsx         # Main application component
│   │   └── index.js        # React entry point
│   ├── package.json        # Node.js dependencies
│   └── tailwind.config.js  # Tailwind configuration
└── .gitignore              # Version control exclusions
```

## 3. Component Architecture

### 3.1 Backend Components

#### 3.1.1 Flask Application Structure
- **App Factory Pattern**: Modular app initialization
- **Blueprint Organization**: Logical route grouping
- **Service Layer**: Business logic separation
- **Model Layer**: Data structure definitions

#### 3.1.2 Database Design
**MongoDB Collections and Schemas:**

**users Collection:**
```javascript
{
  _id: ObjectId,
  phone_number: String (required, unique, indexed),
  name: String (required, maxLength: 100),
  role: String (enum: ['customer', 'admin'], default: 'customer'),
  password_hash: String (admin only, bcrypt hashed),
  email: String (optional, for admin notifications),
  created_at: Date (default: Date.now),
  updated_at: Date (default: Date.now),
  last_login: Date
}

// Indexes:
// - phone_number: unique index
// - role: non-unique index for admin queries
// - created_at: TTL index for cleanup (customers only)
```

**products Collection:**
```javascript
{
  _id: ObjectId,
  name: String (required, maxLength: 200),
  description: String (required, maxLength: 1000),
  price: Number (required, min: 0, precision: 2),
  category_id: ObjectId (required, ref: 'categories'),
  images: [String] (array of image URLs, max 5),
  stock_quantity: Number (required, min: 0, integer),
  active: Boolean (default: true),
  featured: Boolean (default: false),
  created_at: Date (default: Date.now),
  updated_at: Date (default: Date.now)
}

// Indexes:
// - category_id: non-unique index
// - active: non-unique index
// - featured: non-unique index
// - name: text index for search
// - price: non-unique index for sorting
```

**categories Collection:**
```javascript
{
  _id: ObjectId,
  name: String (required, unique, maxLength: 100),
  description: String (optional, maxLength: 500),
  display_order: Number (default: 0),
  active: Boolean (default: true),
  created_at: Date (default: Date.now),
  updated_at: Date (default: Date.now)
}

// Indexes:
// - name: unique index
// - display_order: non-unique index
// - active: non-unique index
```

**orders Collection:**
```javascript
{
  _id: ObjectId,
  order_number: String (required, unique, auto-generated),
  customer_phone: String (required, indexed),
  customer_name: String (required, maxLength: 100),
  delivery_type: String (enum: ['pickup', 'delivery'], required),
  delivery_address: {
    street: String (required if delivery),
    city: String (required if delivery),
    postal_code: String (optional),
    notes: String (optional, maxLength: 200)
  },
  preferred_time: String (optional, maxLength: 100),
  special_instructions: String (optional, maxLength: 500),
  items: [{
    product_id: ObjectId (required, ref: 'products'),
    product_name: String (required, snapshot),
    quantity: Number (required, min: 1),
    unit_price: Number (required, min: 0, snapshot),
    total_price: Number (required, calculated)
  }],
  total_amount: Number (required, min: 0, calculated),
  status: String (enum: ['pending', 'confirmed', 'processing', 'ready', 'completed', 'cancelled'], default: 'pending'),
  verification_code: String (4 digits, expires in 10 minutes),
  verified_at: Date (set when SMS verified),
  created_at: Date (default: Date.now),
  updated_at: Date (default: Date.now)
}

// Indexes:
// - order_number: unique index
// - customer_phone: non-unique index
// - status: non-unique index
// - created_at: non-unique index for date queries
// - verification_code: sparse index (TTL: 10 minutes)
```

**cart_sessions Collection:**
```javascript
{
  _id: ObjectId,
  session_id: String (required, unique, indexed),
  items: [{
    product_id: ObjectId (required, ref: 'products'),
    quantity: Number (required, min: 1)
  }],
  created_at: Date (default: Date.now),
  updated_at: Date (default: Date.now)
}

// Indexes:
// - session_id: unique index
// - created_at: TTL index (expires after 24 hours)
```

#### 3.1.3 API Design
**RESTful Endpoints:**
```
GET    /api/products          # List all products
GET    /api/products/:id      # Get product details
GET    /api/categories        # List all categories
POST   /api/cart              # Add to cart
GET    /api/cart/:session     # Get cart contents
POST   /api/orders            # Create new order
POST   /api/sms/verify        # Send SMS verification
POST   /api/sms/confirm       # Confirm SMS code
POST   /api/auth/login        # Admin login
GET    /api/admin/orders      # Admin: List orders
PUT    /api/admin/orders/:id  # Admin: Update order
POST   /api/admin/products    # Admin: Create product
PUT    /api/admin/products/:id # Admin: Update product
DELETE /api/admin/products/:id # Admin: Delete product
```

### 3.2 Frontend Components

#### 3.2.1 Component Hierarchy
```
App
├── Header (navigation, cart icon)
├── Router
│   ├── Home (welcome, featured products)
│   ├── Products (grid view, filtering)
│   ├── ProductDetail (single product view)
│   ├── Cart (cart contents, checkout button)
│   ├── Checkout (customer form, SMS verification)
│   ├── OrderConfirmation (success message)
│   ├── AdminLogin (authentication form)
│   └── AdminDashboard (product/order management)
└── Footer (contact info, links)
```

#### 3.2.2 State Management
- **React Context**: Global state (cart, auth, products)
- **Local State**: Component-specific state
- **Session Storage**: Cart persistence
- **Custom Hooks**: Reusable state logic

#### 3.2.3 Routing Strategy
```
/                    # Home page
/products            # Product listing
/products/:id        # Product detail
/cart                # Shopping cart
/checkout            # Checkout flow
/order/:id           # Order confirmation
/admin               # Admin login
/admin/dashboard     # Admin panel
/admin/products      # Product management
/admin/orders        # Order management
```

## 4. Technology Integration

### 4.1 MongoDB Integration
- **Connection**: MongoDB Atlas or local instance
- **ODM**: PyMongo with custom model classes
- **Indexing**: Optimized queries for products and orders
- **Validation**: Schema validation at model level

### 4.2 Twilio SMS Integration
- **Purpose**: Phone number verification
- **Implementation**: REST API calls
- **Error Handling**: Graceful fallback for SMS failures
- **Rate Limiting**: Prevent abuse with time-based limits

### 4.3 Authentication Strategy
- **Customer**: Session-based with phone verification
- **Admin**: JWT tokens with secure login
- **Session Management**: Secure token storage

## 5. API Standards and Error Handling

### 5.1 Standard Request/Response Format

#### 5.1.1 Success Response Format
```javascript
{
  "success": true,
  "data": {
    // Response payload
  },
  "message": "Optional success message",
  "timestamp": "2025-01-13T10:30:00Z"
}
```

#### 5.1.2 Error Response Format
```javascript
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // Additional error context (validation errors, etc.)
    }
  },
  "timestamp": "2025-01-13T10:30:00Z"
}
```

#### 5.1.3 HTTP Status Code Usage
- **200 OK**: Successful GET, PUT operations
- **201 Created**: Successful POST operations
- **400 Bad Request**: Invalid input, validation errors
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **409 Conflict**: Duplicate resource (phone number, etc.)
- **429 Too Many Requests**: Rate limiting triggered
- **500 Internal Server Error**: Server-side errors

### 5.2 Input Validation Standards

#### 5.2.1 Validation Rules
- **Phone Numbers**: E.164 format, length validation
- **Prices**: Positive numbers, max 2 decimal places
- **Quantities**: Positive integers only
- **Text Fields**: XSS protection, length limits
- **File Uploads**: Type validation, size limits

#### 5.2.2 Validation Error Format
```javascript
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Input validation failed",
    "details": {
      "field_name": ["Error message 1", "Error message 2"]
    }
  }
}
```

### 5.3 Error Code Taxonomy
- **AUTH_001**: Invalid credentials
- **AUTH_002**: Session expired
- **AUTH_003**: Insufficient permissions
- **VAL_001**: Required field missing
- **VAL_002**: Invalid format
- **VAL_003**: Value out of range
- **SMS_001**: SMS service unavailable
- **SMS_002**: Invalid verification code
- **SMS_003**: Verification code expired
- **DB_001**: Database connection error
- **DB_002**: Document not found
- **RATE_001**: Rate limit exceeded

## 6. Security Architecture

### 6.1 Authentication and Session Management

#### 6.1.1 Customer Authentication Flow
1. **Phone Verification Process**:
   - Customer enters phone number during checkout
   - System generates 4-digit verification code (expires in 10 minutes)
   - SMS sent via Twilio with verification code
   - Customer enters code to verify identity
   - System creates session token (24-hour expiry)
   - Session stored in MongoDB with phone number reference

2. **Customer Session Management**:
   - Session token stored in httpOnly cookie
   - Session data includes: phone_number, name, session_id, expires_at
   - Automatic cleanup of expired sessions
   - No password required for customers

#### 6.1.2 Admin Authentication Flow
1. **Admin Login Process**:
   - Admin enters username/password on /admin login page
   - System validates credentials against users collection (role: 'admin')
   - Password verified using bcrypt hashing
   - JWT token generated with 2-hour expiry
   - Refresh token capability for extended sessions

2. **Admin Session Management**:
   - JWT token stored in httpOnly cookie
   - Token payload includes: user_id, role, exp, iat
   - Automatic token refresh on valid requests
   - Secure logout clears token

#### 6.1.3 Token Security Specifications
- **JWT Secret**: 256-bit random secret from environment variables
- **Session Encryption**: AES-256 encryption for session data
- **Cookie Security**: httpOnly, secure, sameSite=strict
- **CSRF Protection**: CSRF tokens for admin forms

### 6.2 API Security
- **Input Validation**: All endpoints validate input using JSON Schema
- **Rate Limiting**: 100 requests/minute per IP, 10 SMS/hour per phone
- **CORS Configuration**: Restricted origins for production
- **SQL Injection Protection**: MongoDB driver handles parameterization
- **XSS Protection**: Input sanitization and output encoding

### 6.3 Data Protection
- **Environment Variables**: All sensitive configuration externalized
- **Password Hashing**: bcrypt with salt rounds = 12
- **Phone Number Storage**: Direct storage (no encryption needed for business use)
- **PII Handling**: Minimal data collection, clear retention policies
- **Backup Security**: Encrypted database backups

## 6. Performance Optimization

### 6.1 Frontend Performance
- **Code Splitting**: Route-based lazy loading
- **Image Optimization**: Responsive images, lazy loading
- **Bundle Optimization**: Minimize JavaScript bundle size
- **Caching Strategy**: Browser caching for static assets

### 6.2 Backend Performance
- **Database Indexing**: Optimized query performance
- **Response Caching**: Cache frequently accessed data
- **Connection Pooling**: Efficient database connections
- **API Response Optimization**: Minimal data transfer

## 7. Mobile-First Design Principles

### 7.1 Responsive Design
- **Breakpoints**: Mobile-first responsive breakpoints
- **Touch Targets**: Minimum 44px touch targets
- **Navigation**: Mobile-friendly navigation patterns
- **Forms**: Mobile-optimized form inputs

### 7.2 Performance on Mobile
- **Network Optimization**: Minimize data usage
- **Loading States**: Clear feedback during operations
- **Offline Handling**: Graceful degradation
- **Battery Efficiency**: Minimize resource usage

## 8. Development Workflow

### 8.1 Development Environment
- **Backend**: Flask development server (port 8080)
- **Frontend**: React development server (port 3000)
- **Database**: MongoDB local or Atlas
- **SMS Testing**: Twilio test credentials

### 8.2 Testing Strategy
- **Backend**: Unit tests with pytest
- **Frontend**: Component tests with React Testing Library
- **Integration**: API endpoint testing
- **E2E**: Cypress for critical user flows

### 8.3 Deployment Considerations
- **Environment Configuration**: Production vs development
- **Database Migration**: Schema and data migration strategy
- **Asset Management**: Static file serving
- **Monitoring**: Error logging and performance monitoring

## 9. Scalability Considerations

### 9.1 Current Scale Requirements
- **Concurrent Users**: Up to 100 customers
- **Order Volume**: Moderate daily order volume
- **Data Growth**: Manageable product catalog size

### 9.2 Future Scaling Options
- **Database Scaling**: MongoDB replica sets
- **Application Scaling**: Horizontal scaling with load balancer
- **CDN Integration**: Static asset delivery
- **Caching Layer**: Redis for session and data caching

## 10. Risk Mitigation

### 10.1 Technical Risks
- **SMS Delivery Failures**: Fallback verification methods
- **Database Downtime**: Connection retry logic
- **API Rate Limits**: Graceful error handling
- **Mobile Compatibility**: Comprehensive device testing

### 10.2 Business Risks
- **Order Processing Errors**: Clear error messages and recovery
- **Customer Data Loss**: Regular backup strategy
- **Performance Degradation**: Monitoring and alerting
- **Security Vulnerabilities**: Regular security audits

This architecture provides a solid foundation for the local producer web application, emphasizing mobile-first design, security, and maintainability while keeping the implementation appropriately simple for the business requirements.