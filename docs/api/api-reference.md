# API Reference - Pe Foc de Lemne

> **Complete REST API Documentation for Romanian Local Producer Marketplace**

## Base URL
- **Development**: `http://localhost:8080/api`
- **Production**: `https://yourdomain.com/api`

## Authentication

### Admin Authentication
Most admin endpoints require JWT authentication:

```http
Authorization: Bearer <jwt_token>
```

### Customer Session
Customer orders require SMS verification session:

```http
X-Session-Token: <session_token>
```

## 📊 Health Check

### GET /health
Check API server health status.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-12-14T10:30:00Z",
  "version": "1.0.0"
}
```

## 🛍️ Products API

### GET /products
Retrieve all active products with optional filtering and search.

**Query Parameters:**
- `search` (string): Search in product names and descriptions
- `category` (string): Filter by category name
- `producer` (string): Filter by producer name
- `min_price` (number): Minimum price filter
- `max_price` (number): Maximum price filter
- `limit` (number): Maximum number of results (default: 50)
- `offset` (number): Pagination offset (default: 0)

**Example Request:**
```http
GET /api/products?search=mere&category=Fructe&limit=10
```

**Response:**
```json
{
  "success": true,
  "products": [
    {
      "id": "prod_123",
      "name": "Mere Golden",
      "description": "Mere Golden proaspete, cultivate ecologic în județul Cluj",
      "price": 8.99,
      "category": "Fructe",
      "producer": "Ferma Ionescu",
      "producer_location": "Cluj-Napoca, Cluj",
      "stock": 50,
      "unit": "kg",
      "image_url": "/images/products/mere-golden.jpg",
      "organic": true,
      "harvest_date": "2024-09-15",
      "status": "active",
      "created_at": "2024-09-20T08:30:00Z"
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

### GET /products/:id
Retrieve a specific product by ID.

**Response:**
```json
{
  "success": true,
  "product": {
    "id": "prod_123",
    "name": "Mere Golden",
    "description": "Mere Golden proaspete, cultivate ecologic în județul Cluj",
    "price": 8.99,
    "category": "Fructe",
    "producer": "Ferma Ionescu",
    "producer_info": {
      "name": "Ferma Ionescu",
      "location": "Cluj-Napoca, Cluj",
      "description": "Fermă de familie cu tradiție de 3 generații",
      "certifications": ["Bio", "Eco-Cert"],
      "contact_info": {
        "phone": "+40721***567",
        "email": "contact@***"
      }
    },
    "nutritional_info": {
      "calories_per_100g": 52,
      "vitamins": ["Vitamin C", "Vitamin A"],
      "allergens": []
    },
    "storage_instructions": "Se păstrează la frigider până la 2 săptămâni",
    "stock": 50,
    "unit": "kg",
    "images": [
      "/images/products/mere-golden-1.jpg",
      "/images/products/mere-golden-2.jpg"
    ],
    "reviews": {
      "average_rating": 4.8,
      "review_count": 24
    },
    "status": "active"
  }
}
```

## 📂 Categories API

### GET /categories
Retrieve all active product categories.

**Response:**
```json
{
  "success": true,
  "categories": [
    {
      "id": "cat_fructe",
      "name": "Fructe",
      "description": "Fructe proaspete de sezon de la producători locali",
      "icon": "🍎",
      "product_count": 45,
      "status": "active"
    },
    {
      "id": "cat_legume",
      "name": "Legume",
      "description": "Legume proaspete din grădini românești",
      "icon": "🥕",
      "product_count": 67,
      "status": "active"
    },
    {
      "id": "cat_lactate",
      "name": "Produse lactate",
      "description": "Lapte, brânzeturi și iaurt de la ferme locale",
      "icon": "🧀",
      "product_count": 28,
      "status": "active"
    }
  ]
}
```

## 🛒 Cart API

### POST /cart
Add item to shopping cart session.

**Request Body:**
```json
{
  "product_id": "prod_123",
  "quantity": 2,
  "session_id": "session_abc123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Produsul a fost adăugat în coș",
  "cart_item": {
    "product_id": "prod_123",
    "product_name": "Mere Golden",
    "quantity": 2,
    "unit_price": 8.99,
    "total_price": 17.98,
    "producer": "Ferma Ionescu"
  },
  "cart_total": {
    "items_count": 3,
    "subtotal": 45.97,
    "total": 45.97
  }
}
```

### GET /cart/:session_id
Retrieve cart contents for a session.

**Response:**
```json
{
  "success": true,
  "cart": {
    "session_id": "session_abc123",
    "items": [
      {
        "product_id": "prod_123",
        "product_name": "Mere Golden",
        "quantity": 2,
        "unit_price": 8.99,
        "total_price": 17.98,
        "producer": "Ferma Ionescu",
        "image_url": "/images/products/mere-golden.jpg",
        "stock_available": 50
      }
    ],
    "summary": {
      "items_count": 2,
      "subtotal": 17.98,
      "delivery_fee": 0.00,
      "total": 17.98
    },
    "created_at": "2024-12-14T10:30:00Z",
    "updated_at": "2024-12-14T10:35:00Z"
  }
}
```

### PUT /cart/:session_id/item/:product_id
Update quantity of item in cart.

**Request Body:**
```json
{
  "quantity": 3
}
```

### DELETE /cart/:session_id/item/:product_id
Remove item from cart.

**Response:**
```json
{
  "success": true,
  "message": "Produsul a fost eliminat din coș"
}
```

## 📱 SMS Verification API

### POST /sms/verify
Send SMS verification code to Romanian phone number.

**Request Body:**
```json
{
  "phone_number": "+40721234567"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Codul de verificare a fost trimis cu succes",
  "session_id": "sms_session_abc123",
  "expires_at": "2024-12-14T10:40:00Z"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "invalid_phone",
  "message": "Formatul numărului de telefon nu este valid pentru România",
  "details": {
    "expected_format": "+40XXXXXXXXX sau 07XXXXXXXX"
  }
}
```

### POST /sms/confirm
Confirm SMS verification code.

**Request Body:**
```json
{
  "session_id": "sms_session_abc123",
  "code": "123456",
  "phone_number": "+40721234567"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Codul de verificare este corect",
  "verified": true,
  "customer_session_token": "verified_session_xyz789"
}
```

## 📋 Orders API

### POST /orders
Create new order with verified customer information.

**Request Body:**
```json
{
  "customer_info": {
    "name": "Ion Popescu",
    "phone": "+40721234567",
    "email": "ion.popescu@example.com",
    "address": {
      "street": "Strada Florilor 123",
      "city": "București",
      "county": "București",
      "postal_code": "123456"
    }
  },
  "cart_session_id": "session_abc123",
  "sms_session_token": "verified_session_xyz789",
  "delivery_notes": "Vă rog să sunați înainte de livrare",
  "delivery_time_preference": "weekend"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Comanda a fost plasată cu succes",
  "order": {
    "id": "order_456",
    "order_number": "ORD-2024-001234",
    "status": "pending",
    "customer_info": {
      "name": "Ion Popescu",
      "phone": "+4072***4567",
      "email": "ion.***@***.com"
    },
    "items": [
      {
        "product_id": "prod_123",
        "product_name": "Mere Golden",
        "producer": "Ferma Ionescu",
        "quantity": 2,
        "unit_price": 8.99,
        "total_price": 17.98
      }
    ],
    "summary": {
      "subtotal": 17.98,
      "delivery_fee": 0.00,
      "total": 17.98,
      "currency": "RON"
    },
    "delivery_info": {
      "estimated_delivery": "2024-12-16",
      "delivery_window": "09:00 - 17:00",
      "notes": "Vă rog să sunați înainte de livrare"
    },
    "created_at": "2024-12-14T10:30:00Z"
  }
}
```

### GET /orders/:order_number
Retrieve order details (requires SMS verification for customer orders).

**Headers:**
```http
X-Phone-Number: +40721234567
X-Session-Token: verified_session_xyz789
```

**Response:**
```json
{
  "success": true,
  "order": {
    "order_number": "ORD-2024-001234",
    "status": "confirmed",
    "status_history": [
      {
        "status": "pending",
        "timestamp": "2024-12-14T10:30:00Z",
        "note": "Comandă plasată"
      },
      {
        "status": "confirmed",
        "timestamp": "2024-12-14T11:00:00Z",
        "note": "Comandă confirmată de producător"
      }
    ],
    "estimated_delivery": "2024-12-16",
    "tracking_info": {
      "current_status": "confirmed",
      "next_step": "Pregătirea produselor",
      "contact_producer": "+4072***5678"
    }
  }
}
```

## 🔐 Admin Authentication API

### POST /auth/login
Admin login with username and password.

**Request Body:**
```json
{
  "username": "admin",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Autentificare reușită",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "admin": {
    "id": "admin_123",
    "username": "admin",
    "permissions": ["products", "orders", "categories", "analytics"],
    "last_login": "2024-12-14T10:30:00Z"
  },
  "expires_at": "2024-12-14T18:30:00Z"
}
```

### POST /auth/refresh
Refresh JWT token before expiration.

**Headers:**
```http
Authorization: Bearer <current_jwt_token>
```

**Response:**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2024-12-14T20:30:00Z"
}
```

## 👨‍💼 Admin Products API

### POST /admin/products
Create new product (Admin only).

**Headers:**
```http
Authorization: Bearer <admin_jwt_token>
```

**Request Body:**
```json
{
  "name": "Brânză de capră",
  "description": "Brânză de capră artizanală, maturată 3 luni",
  "price": 35.00,
  "category": "Produse lactate",
  "producer": "Ferma Alpina",
  "producer_info": {
    "location": "Brașov, Brașov",
    "description": "Fermă de familie specializată în produse lactate",
    "certifications": ["Bio"]
  },
  "stock": 15,
  "unit": "bucată",
  "images": ["image1.jpg", "image2.jpg"],
  "nutritional_info": {
    "calories_per_100g": 364,
    "protein": "25g",
    "fat": "29g"
  },
  "storage_instructions": "Se păstrează la frigider",
  "organic": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Produsul a fost adăugat cu succes",
  "product": {
    "id": "prod_789",
    "name": "Brânză de capră",
    "price": 35.00,
    "status": "active",
    "created_at": "2024-12-14T10:30:00Z"
  }
}
```

### PUT /admin/products/:id
Update existing product (Admin only).

### DELETE /admin/products/:id
Delete/deactivate product (Admin only).

## 📋 Admin Orders API

### GET /admin/orders
Retrieve all orders with filtering options (Admin only).

**Query Parameters:**
- `status` (string): Filter by order status
- `producer` (string): Filter by producer name
- `start_date` (string): Filter by creation date (ISO format)
- `end_date` (string): Filter by creation date (ISO format)
- `limit` (number): Maximum number of results
- `offset` (number): Pagination offset

**Response:**
```json
{
  "success": true,
  "orders": [
    {
      "id": "order_456",
      "order_number": "ORD-2024-001234",
      "status": "pending",
      "customer_name": "Ion Popescu",
      "customer_phone": "+4072***4567",
      "total": 17.98,
      "currency": "RON",
      "items_count": 1,
      "created_at": "2024-12-14T10:30:00Z",
      "producers": ["Ferma Ionescu"]
    }
  ],
  "total": 1,
  "statistics": {
    "pending": 5,
    "confirmed": 12,
    "delivered": 8,
    "cancelled": 1
  }
}
```

### PUT /admin/orders/:id/status
Update order status (Admin only).

**Request Body:**
```json
{
  "status": "confirmed",
  "note": "Comandă confirmată - livrare programată pentru mâine"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Statusul comenzii a fost actualizat",
  "order": {
    "id": "order_456",
    "status": "confirmed",
    "updated_at": "2024-12-14T11:00:00Z"
  }
}
```

## 📊 Analytics API

### POST /analytics/events
Store analytics events (batch processing).

**Request Body:**
```json
{
  "events": [
    {
      "type": "product_view",
      "timestamp": "2024-12-14T10:30:00Z",
      "user_session": "session_abc123",
      "data": {
        "product_id": "prod_123",
        "product_name": "Mere Golden",
        "category": "Fructe"
      }
    },
    {
      "type": "add_to_cart",
      "timestamp": "2024-12-14T10:32:00Z",
      "user_session": "session_abc123",
      "data": {
        "product_id": "prod_123",
        "quantity": 2,
        "price": 8.99
      }
    }
  ]
}
```

### GET /admin/analytics/dashboard
Get business analytics dashboard data (Admin only).

**Response:**
```json
{
  "success": true,
  "analytics": {
    "overview": {
      "total_orders": 156,
      "total_revenue": 12450.75,
      "active_customers": 89,
      "active_products": 234
    },
    "trends": {
      "orders_last_7_days": [12, 15, 8, 22, 18, 14, 20],
      "revenue_last_7_days": [450.25, 678.90, 234.50, 890.75, 567.25, 445.80, 723.30]
    },
    "top_products": [
      {
        "product_name": "Mere Golden",
        "orders": 45,
        "revenue": 404.55
      }
    ],
    "top_producers": [
      {
        "producer_name": "Ferma Ionescu",
        "orders": 78,
        "revenue": 2340.50
      }
    ]
  }
}
```

## 🚨 Error Handling

### Error Response Format
```json
{
  "success": false,
  "error": "error_code",
  "message": "Mesaj de eroare în română",
  "details": {
    "field": "validation_error_details"
  },
  "timestamp": "2024-12-14T10:30:00Z"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `validation_error` | 400 | Invalid input data |
| `unauthorized` | 401 | Authentication required |
| `forbidden` | 403 | Insufficient permissions |
| `not_found` | 404 | Resource not found |
| `rate_limit_exceeded` | 429 | Too many requests |
| `server_error` | 500 | Internal server error |

### Romanian Error Messages

All error messages are provided in Romanian for better user experience:

```json
{
  "success": false,
  "error": "validation_error",
  "message": "Datele introduse nu sunt valide",
  "details": {
    "phone": "Formatul numărului de telefon nu este valid pentru România",
    "email": "Adresa de email nu este validă"
  }
}
```

## 🔄 Rate Limiting

### Rate Limits by Endpoint

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| SMS verification | 10 requests | 1 hour |
| Order creation | 5 requests | 1 minute |
| Product search | 100 requests | 1 minute |
| General API | 1000 requests | 1 hour |

### Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1639483200
Retry-After: 60
```

## 📝 Request/Response Examples

### Complete Order Flow Example

1. **Browse Products**
```http
GET /api/products?category=Fructe
```

2. **Add to Cart**
```http
POST /api/cart
{
  "product_id": "prod_123",
  "quantity": 2,
  "session_id": "session_abc123"
}
```

3. **SMS Verification**
```http
POST /api/sms/verify
{
  "phone_number": "+40721234567"
}
```

4. **Confirm SMS Code**
```http
POST /api/sms/confirm
{
  "session_id": "sms_session_abc123",
  "code": "123456",
  "phone_number": "+40721234567"
}
```

5. **Place Order**
```http
POST /api/orders
{
  "customer_info": { ... },
  "cart_session_id": "session_abc123",
  "sms_session_token": "verified_session_xyz789"
}
```

---

**For more detailed documentation:**
- [Database Schema](../database/schema.md)
- [Authentication Guide](../security/authentication.md)
- [Deployment Guide](../deployment/production-setup.md)

**API Support**: tech@pefocdelemne.ro