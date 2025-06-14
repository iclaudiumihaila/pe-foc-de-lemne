# Technical Handover Documentation - Pe Foc de Lemne

> **Complete Technical Transfer for Development and Operations Teams**

## 🎯 Technical Handover Overview

This document provides comprehensive technical handover information for development teams, system administrators, and technical stakeholders taking over the Pe Foc de Lemne Romanian marketplace.

## 🏗️ System Architecture Overview

### Application Stack
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │   Flask Backend │    │   MongoDB DB    │
│   Port: 3000     │────│   Port: 8080    │────│   Atlas/Local   │
│   Modern UI      │    │   REST API      │    │   Document DB   │
│   Romanian i18n  │    │   SMS Service   │    │   GDPR Ready    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │   Monitoring    │    │    Backup       │
│   Load Balancer │    │   PM2 + Logs    │    │   Automated     │
│   SSL/Security  │    │   Health Checks │    │   GDPR Compliant│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack Details

#### Frontend (React 18.x)
- **Framework**: React with TypeScript
- **State Management**: Context API + useReducer
- **Styling**: CSS Modules with responsive design
- **Build Tool**: Create React App (CRA)
- **Testing**: Jest + React Testing Library
- **E2E Testing**: Cypress

#### Backend (Flask 2.x)
- **Framework**: Flask with Python 3.9+
- **Database**: MongoDB with PyMongo
- **Authentication**: JWT tokens
- **SMS Service**: Twilio integration
- **Testing**: pytest + pytest-flask
- **Security**: Flask-CORS, rate limiting, input validation

#### Infrastructure
- **Web Server**: Nginx (production)
- **Process Manager**: PM2
- **Database**: MongoDB Atlas (recommended) or self-hosted
- **SSL**: Let's Encrypt certificates
- **Monitoring**: PM2 monitoring + custom health checks

## 📁 Project Structure

### Repository Organization
```
pe-foc-de-lemne/
├── backend/                 # Flask API server
│   ├── app/
│   │   ├── routes/         # API endpoints
│   │   ├── models/         # Data models
│   │   ├── services/       # Business logic
│   │   ├── utils/          # Utility functions
│   │   ├── middleware/     # Security middleware
│   │   └── tests/          # Backend tests
│   ├── requirements.txt    # Python dependencies
│   └── app.py             # Application entry point
├── frontend/               # React application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/         # Page components
│   │   ├── contexts/      # State management
│   │   ├── services/      # API integration
│   │   ├── utils/         # Utility functions
│   │   └── tests/         # Frontend tests
│   ├── public/            # Static assets
│   └── package.json       # Node.js dependencies
├── docs/                  # Documentation
│   ├── api/              # API documentation
│   ├── deployment/       # Deployment guides
│   ├── users/           # User guides
│   └── handover/        # Handover documentation
├── agentic_flow/         # Development logs
└── cypress/              # E2E tests
```

## 🔧 Development Environment Setup

### Prerequisites
```bash
# System requirements
- Node.js 18+ and npm
- Python 3.9+ and pip
- MongoDB (local) or MongoDB Atlas account
- Git
- Code editor (VS Code recommended)
```

### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations (if needed)
python -c "from app.database import create_indexes; create_indexes()"

# Start development server
python app.py
# Server runs on http://localhost:8080
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Start development server
npm start
# Application runs on http://localhost:3000
```

### Environment Variables

#### Backend (.env)
```bash
# Application
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# Database
MONGODB_URI=mongodb://localhost:27017/pe_foc_de_lemne_dev

# Twilio SMS
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-phone

# JWT
JWT_SECRET_KEY=your-jwt-secret

# Security
ENCRYPTION_MASTER_KEY=your-32-char-encryption-key
CORS_ORIGINS=http://localhost:3000
```

#### Frontend (.env.local)
```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8080/api

# Analytics (optional)
REACT_APP_GA4_MEASUREMENT_ID=G-XXXXXXXXXX

# Application
REACT_APP_ENV=development
REACT_APP_VERSION=1.0.0
```

## 🗄️ Database Schema

### MongoDB Collections

#### Products Collection
```javascript
{
  _id: ObjectId,
  name: String,                    // Product name (Romanian)
  description: String,             // Product description (Romanian)
  price: Number,                   // Price in RON
  category: String,                // Product category
  producer: String,                // Producer name
  producer_info: {
    location: String,              // Romanian location
    description: String,
    certifications: [String],
    contact_info: Object
  },
  stock: Number,                   // Available quantity
  unit: String,                    // Unit of measurement
  images: [String],                // Image URLs
  nutritional_info: Object,
  storage_instructions: String,
  organic: Boolean,
  harvest_date: Date,
  status: String,                  // active, inactive
  created_at: Date,
  updated_at: Date
}
```

#### Orders Collection
```javascript
{
  _id: ObjectId,
  order_number: String,            // Unique order number (ORD-YYYY-NNNNNN)
  status: String,                  // pending, confirmed, delivered, cancelled
  customer_info: {
    name: String,
    phone: String,                 // Romanian format (+40...)
    email: String,
    address: {
      street: String,
      city: String,
      county: String,              // Romanian county
      postal_code: String          // Romanian postal code
    }
  },
  items: [{
    product_id: ObjectId,
    product_name: String,
    producer: String,
    quantity: Number,
    unit_price: Number,
    total_price: Number
  }],
  summary: {
    subtotal: Number,
    delivery_fee: Number,
    total: Number,
    currency: String               // RON
  },
  delivery_info: {
    estimated_delivery: Date,
    delivery_window: String,
    notes: String
  },
  status_history: [{
    status: String,
    timestamp: Date,
    note: String
  }],
  created_at: Date,
  updated_at: Date
}
```

### Database Indexes
```javascript
// Performance indexes (created automatically)
products: [
  { category: 1, status: 1 },
  { producer: 1, status: 1 },
  { name: "text", description: "text" },
  { price: 1 },
  { created_at: -1 }
]

orders: [
  { order_number: 1 },           // unique
  { "customer_info.phone": 1 },
  { status: 1 },
  { created_at: -1 }
]

cart_sessions: [
  { session_id: 1 },             // unique
  { created_at: 1 }              // TTL index (2 hours)
]
```

## 🔌 API Integration

### Authentication Flow
```typescript
// Admin Authentication
const loginResponse = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: 'password'
  })
});

const { token } = await loginResponse.json();

// Use token in subsequent requests
const response = await fetch('/api/admin/products', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

### Customer Order Flow
```typescript
// 1. Add items to cart
await fetch('/api/cart', {
  method: 'POST',
  body: JSON.stringify({
    product_id: 'prod_123',
    quantity: 2,
    session_id: sessionId
  })
});

// 2. Start SMS verification
const smsResponse = await fetch('/api/sms/verify', {
  method: 'POST',
  body: JSON.stringify({
    phone_number: '+40721234567'
  })
});

// 3. Confirm SMS code
const confirmResponse = await fetch('/api/sms/confirm', {
  method: 'POST',
  body: JSON.stringify({
    session_id: smsSessionId,
    code: '123456',
    phone_number: '+40721234567'
  })
});

// 4. Place order
const orderResponse = await fetch('/api/orders', {
  method: 'POST',
  headers: {
    'X-Session-Token': verifiedSessionToken
  },
  body: JSON.stringify({
    customer_info: customerData,
    cart_session_id: cartSessionId,
    sms_session_token: verifiedSessionToken
  })
});
```

## 🧪 Testing Strategy

### Running Tests

#### Backend Tests
```bash
cd backend

# Install test dependencies
pip install pytest pytest-flask pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_products.py

# Run tests with verbose output
pytest -v
```

#### Frontend Tests
```bash
cd frontend

# Run unit tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run tests in watch mode
npm test -- --watch

# Run specific test file
npm test -- ProductCard.test.js
```

#### End-to-End Tests
```bash
cd frontend

# Install Cypress
npm install cypress --save-dev

# Run Cypress tests (headless)
npx cypress run

# Open Cypress GUI
npx cypress open
```

### Test Structure

#### Backend Test Example
```python
# tests/test_products.py
import pytest
from app import create_app
from app.models import Product

@pytest.fixture
def app():
    app = create_app(testing=True)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_get_products(client):
    response = client.get('/api/products')
    assert response.status_code == 200
    data = response.get_json()
    assert 'products' in data
    assert 'success' in data
    assert data['success'] is True
```

#### Frontend Test Example
```typescript
// components/__tests__/ProductCard.test.tsx
import { render, screen } from '@testing-library/react';
import { ProductCard } from '../ProductCard';

const mockProduct = {
  id: 'prod_123',
  name: 'Mere Golden',
  price: 8.99,
  producer: 'Ferma Ionescu',
  image_url: '/images/mere.jpg'
};

test('renders product information correctly', () => {
  render(<ProductCard product={mockProduct} />);
  
  expect(screen.getByText('Mere Golden')).toBeInTheDocument();
  expect(screen.getByText('8.99 RON')).toBeInTheDocument();
  expect(screen.getByText('Ferma Ionescu')).toBeInTheDocument();
});
```

## 🚀 Deployment Process

### Production Deployment Checklist

#### Pre-Deployment
- [ ] Code review completed
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] SSL certificates valid
- [ ] Backup strategy in place

#### Deployment Steps
```bash
# 1. Update code
cd /home/pefocdelemne/pe-foc-de-lemne
git pull origin main

# 2. Update backend dependencies
cd backend
pip install -r requirements.txt

# 3. Build frontend
cd ../frontend
npm install
npm run build

# 4. Run database migrations (if any)
cd ../backend
python -c "from app.database import run_migrations; run_migrations()"

# 5. Restart services
pm2 restart pe-foc-de-lemne-backend

# 6. Verify deployment
curl -f https://yourdomain.com/api/health
```

#### Post-Deployment
- [ ] Health checks passing
- [ ] SSL certificate valid
- [ ] Performance metrics acceptable
- [ ] Error monitoring active
- [ ] Backup verification

### Rollback Procedure
```bash
# 1. Stop current services
pm2 stop pe-foc-de-lemne-backend

# 2. Restore previous version
git reset --hard <previous_commit_hash>

# 3. Restore database (if needed)
mongorestore --uri="mongodb://..." backup_directory

# 4. Rebuild frontend
cd frontend && npm run build

# 5. Restart services
pm2 start pe-foc-de-lemne-backend

# 6. Verify rollback
curl -f https://yourdomain.com/api/health
```

## 📊 Monitoring and Logging

### Application Monitoring
```bash
# PM2 monitoring
pm2 status                          # Check process status
pm2 logs pe-foc-de-lemne-backend    # View application logs
pm2 monit                           # Real-time monitoring

# System monitoring
htop                                 # CPU and memory usage
iotop                               # Disk I/O monitoring
nethogs                             # Network usage

# Log files
tail -f /var/log/pe-foc-de-lemne/backend.log    # Application logs
tail -f /var/log/nginx/access.log               # Web server logs
tail -f /var/log/nginx/error.log                # Web server errors
```

### Health Checks
```bash
# API health check
curl -f https://yourdomain.com/api/health

# Database health check
mongo "mongodb://..." --eval "db.stats()"

# SSL certificate check
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

### Performance Monitoring
```bash
# Page speed testing
lighthouse https://yourdomain.com --output=html

# Load testing (basic)
ab -n 1000 -c 10 https://yourdomain.com/

# Database performance
mongo "mongodb://..." --eval "db.products.explain().find({})"
```

## 🔐 Security Management

### Security Checklist
- [ ] HTTPS enforced everywhere
- [ ] Security headers configured
- [ ] Rate limiting active
- [ ] Input validation implemented
- [ ] Authentication secure
- [ ] Database access restricted
- [ ] Regular security updates

### Security Monitoring
```bash
# Check for vulnerabilities
npm audit                           # Frontend dependencies
pip-audit                          # Backend dependencies

# SSL certificate monitoring
certbot certificates               # Certificate status
certbot renew --dry-run           # Test renewal

# Log analysis for security
grep "failed\|error\|attack" /var/log/nginx/access.log
grep "ERROR\|WARNING" /var/log/pe-foc-de-lemne/backend.log
```

### Incident Response
1. **Immediate Response**
   - Isolate affected systems
   - Document the incident
   - Assess impact and scope

2. **Investigation**
   - Analyze logs and system state
   - Identify root cause
   - Document findings

3. **Resolution**
   - Apply fixes or patches
   - Test resolution thoroughly
   - Monitor for recurrence

4. **Post-Incident**
   - Update security procedures
   - Communicate with stakeholders
   - Implement preventive measures

## 🔄 Maintenance Procedures

### Regular Maintenance Tasks

#### Daily
- [ ] Monitor system health and performance
- [ ] Check application logs for errors
- [ ] Verify backup completion
- [ ] Monitor SSL certificate status

#### Weekly
- [ ] Review system resource usage
- [ ] Check for security updates
- [ ] Test backup restoration process
- [ ] Review application performance metrics

#### Monthly
- [ ] Update system packages
- [ ] Review and rotate logs
- [ ] Conduct security scan
- [ ] Test disaster recovery procedures

#### Quarterly
- [ ] Review and update documentation
- [ ] Conduct penetration testing
- [ ] Review access controls
- [ ] Plan capacity upgrades

### Backup and Recovery

#### Automated Backup Script
```bash
#!/bin/bash
# /home/pefocdelemne/backup-script.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/pefocdelemne/backups"

# Database backup
mongodump --uri="$MONGODB_URI" --out="$BACKUP_DIR/db_$DATE"

# Application backup
tar -czf "$BACKUP_DIR/app_$DATE.tar.gz" -C /home/pefocdelemne pe-foc-de-lemne

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.gz" -mtime +30 -delete
find "$BACKUP_DIR" -name "db_*" -mtime +30 -exec rm -rf {} \;
```

#### Recovery Procedures
```bash
# Database recovery
mongorestore --uri="$MONGODB_URI" --drop backup_directory

# Application recovery
tar -xzf app_backup.tar.gz -C /home/pefocdelemne
pm2 restart pe-foc-de-lemne-backend
```

## 📞 Support and Escalation

### Development Team Contacts
- **Lead Developer**: tech@pefocdelemne.ro
- **DevOps Engineer**: ops@pefocdelemne.ro
- **Security Officer**: security@pefocdelemne.ro

### Escalation Procedures
1. **Level 1**: Development team (response: 2 hours)
2. **Level 2**: Senior technical lead (response: 1 hour)
3. **Level 3**: Executive team (response: 30 minutes)

### Documentation Resources
- **API Documentation**: `/docs/api/api-reference.md`
- **Deployment Guide**: `/docs/deployment/production-setup.md`
- **User Guides**: `/docs/users/`
- **Architecture Documentation**: `/docs/design/architecture.md`

---

**This technical handover documentation provides comprehensive information for taking over the Pe Foc de Lemne marketplace. For additional questions or clarification, contact the development team at tech@pefocdelemne.ro.**