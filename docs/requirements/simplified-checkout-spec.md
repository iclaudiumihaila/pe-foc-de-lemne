# Simplified Checkout Requirements Specification

## Overview
Transform the checkout process into a single-page, phone-centric experience that minimizes friction while maintaining security and user data persistence.

## User Flow

### 1. Cart Review
- User adds products to cart
- Clicks "Checkout" button

### 2. Checkout Page States

#### State 1: Initial Information
- **Name Field**: Single text input (full name)
- **Phone Field**: Romanian phone format
- **Continue Button**: Triggers SMS validation

#### State 2: Phone Verification (Same Page)
- SMS code input appears below phone
- 6-digit verification code
- Resend option after 60 seconds
- No page navigation

#### State 3: Address Selection (After Verification)
- If existing customer: Show saved addresses
- Option: "Use this address" for each saved address
- Option: "Add new address" 
- If new customer: Direct to address form

#### State 4: Address Input (If New)
- Street address
- City
- County (dropdown)
- Postal code
- Delivery notes (optional)
- Checkbox: "Save for future orders"

#### State 5: Order Summary & Confirmation
- Review order details
- Delivery address summary
- Total with delivery
- "Place Order" button

## Technical Requirements

### Backend
1. New collection: `customer_phones`
2. SMS validation without creating traditional user account
3. Address management endpoints
4. Session management post-validation

### Frontend
1. Single-page checkout component with state management
2. Progressive form disclosure
3. Real-time validation
4. Address autocomplete (future enhancement)

### Security
1. Rate limiting on SMS sends
2. Phone number validation
3. Session tokens after verification
4. Address privacy (show partial info)

## Non-Functional Requirements
- Mobile-first responsive design
- Accessibility compliant
- Sub-3 second page loads
- Clear error messaging in Romanian