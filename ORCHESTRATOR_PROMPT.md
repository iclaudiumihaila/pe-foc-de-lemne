# Web Application Development Project for Local Producer

## Business Context
This project is for a local producer who creates various artisanal/handmade products (could be food items, crafts, or other locally-produced goods). They currently sell their products through traditional channels but need to expand their reach by offering online ordering. Their customers are primarily local community members who value quality, locally-sourced products and personal service.

### The Business Need
The producer needs a simple, efficient way to:
- Showcase their products online
- Accept orders from customers without handling online payments (cash on delivery/pickup model)
- Verify customer identity through phone numbers (building trust and preventing fake orders)
- Manage their product catalog and process orders efficiently

### Why This Approach
- **Phone verification instead of complex authentication**: Their customer base prefers simple, familiar processes. Phone numbers are universal and don't require remembering passwords.
- **No payment processing**: Maintains the personal, trust-based relationship with customers. Payment happens on delivery/pickup.
- **Mobile-first**: Most customers will browse and order from their phones while on the go.
- **Simple admin interface**: The producer needs to manage products and orders without technical complexity.

## Project Overview
You are the Orchestrator agent tasked with developing a full-stack web application that enables this local producer to take their business online while maintaining the personal, community-focused approach that makes them successful. This is a long-running project that you will execute autonomously following the methodology defined in claude.md.

## Non-Negotiable Technical Requirements

### Backend
- **Database**: MongoDB (mandatory)
- **Server**: Flask API running on port 8080
- **SMS Service**: Twilio integration for phone number verification
- **API Base**: http://localhost:8080/api

### Frontend
- **Framework**: React (running on port 3000)
- **Styling**: Tailwind CSS with Hero UI components (find and use working versions)
- **Priority**: Mobile-first responsive design
- **Simplicity**: Minimal complexity, focus on user experience

## Key User Stories

### For Customers
- "As a local resident, I want to browse products from my favorite local producer on my phone so I can order for pickup/delivery"
- "As a customer, I want a simple checkout process that doesn't require creating an account"
- "As a customer, I want to verify my order with my phone number so the producer knows it's really me"

### For the Producer
- "As the producer, I want to easily add and update my products so customers always see what's available"
- "As the producer, I want to see and manage incoming orders so I can prepare them for pickup/delivery"
- "As the producer, I want to organize products by categories so customers can find what they're looking for"

## Functional Requirements

### Customer Journey (Mobile-First)
1. **Home Page**
   - Welcoming design that reflects the local, artisanal nature of the business
   - Brief introduction to the producer/business
   - Featured products or categories
   - Clear "Browse Products" call-to-action
   - Contact information visible
   
2. **Product Browsing**
   - View all products
   - Filter by categories
   - Search functionality
   - Product details view
   
3. **Shopping Cart**
   - Add/remove products
   - Update quantities
   - View cart summary
   
4. **Checkout Process**
   - Cart review with clear product images and totals
   - Customer information form:
     - Name
     - Phone number (for verification)
     - Pickup or delivery selection
     - Address (if delivery)
     - Preferred time slot
     - Special instructions (allergies, preferences, etc.)
   - **Phone Verification** (Critical Feature):
     - Customer enters phone number
     - System sends 4-digit code via Twilio SMS
     - Customer enters code to confirm order
     - No payment processing (payment on delivery/pickup)
   
5. **Order Confirmation**
   - Warm thank you message
   - Order summary with pickup/delivery details
   - Order reference number
   - What happens next (e.g., "We'll prepare your order for pickup tomorrow at 3 PM")
   - Producer's contact information for questions

### Admin Panel Requirements
1. **Authentication**
   - Secure admin login
   - Role-based access (Customer vs Admin)
   
2. **Product Management**
   - Add/Edit/Delete products
   - Upload product images
   - Set prices and descriptions
   - Manage inventory
   
3. **Category Management**
   - Create/Edit/Delete categories
   - Assign products to categories
   
4. **Order Management**
   - View all orders
   - Update order status
   - View customer details
   - Export order data

## Data Models

### User
- Phone number (primary identifier)
- Name
- Role (customer/admin)
- Orders history

### Product
- Name
- Description
- Price
- Category
- Images
- Stock quantity
- Active status

### Category
- Name
- Description
- Display order

### Order
- Order number
- Customer phone
- Customer name
- Delivery/pickup preference
- Delivery address (if applicable)
- Special instructions
- Items (products, quantities, prices)
- Total amount
- Status (pending/confirmed/processed/ready/completed)
- Timestamp
- Verification code (for SMS)

### Cart (Session-based)
- Items
- Quantities
- Session ID

## Critical Success Factors
1. **Mobile Responsiveness**: The app MUST work flawlessly on mobile devices
2. **SMS Verification**: Phone number verification MUST work reliably
3. **Simplicity**: UI must be intuitive for non-technical users
4. **Performance**: Fast loading times, especially on mobile networks
5. **Trust Building**: Design should convey quality, locality, and personal service
6. **Order Management**: Producer must be able to efficiently process orders for same-day or next-day fulfillment

## Design Philosophy
- **Warm and Welcoming**: Use colors and imagery that reflect artisanal, handmade quality
- **Photo-Centric**: Products should be showcased with high-quality images
- **Minimal Text**: Use concise descriptions; let the products speak for themselves
- **Clear CTAs**: Every action should be obvious and require minimal thinking
- **Local Focus**: Emphasize the local, community aspect throughout the design

## Project Execution Instructions

Follow the Orchestrator methodology from claude.md:

1. **Initialize the project structure** following the controlled directories pattern
2. **Create comprehensive requirements** in `docs/requirements/spec.md`
3. **Design the architecture** with Architect A/B review cycles
4. **Break down into atomic tasks** in `docs/design/tasks.yaml`
5. **Execute incrementally** with proper logging at each step
6. **Test each component** before moving to the next
7. **Review each implementation** by spawning review tasks

## Additional Constraints
- Keep the frontend as simple as possible
- Prioritize user experience over complex features
- Ensure all forms are mobile-friendly
- Use clear, actionable error messages
- Implement proper loading states
- Handle network failures gracefully

## Security Considerations
- Secure admin authentication
- Rate limiting on SMS verification
- Input validation on all forms
- Secure API endpoints
- Environment variables for sensitive data (Twilio credentials, MongoDB URI)

## Development Priorities
1. Core customer flow (browse → cart → checkout with SMS)
2. Admin authentication and basic product management
3. Category management
4. Order management interface
5. Enhanced features (search, filters, etc.)

Begin by initializing the project structure and creating the detailed requirements specification. Remember to log every decision and action before execution, work in the smallest possible increments, and follow the Architect A/B review cycle for all design decisions.

The project root should be: `/Users/claudiu/Desktop/pe foc de lemne`

**START IMMEDIATELY** by creating the agentic_flow directory structure and logging the initialization.