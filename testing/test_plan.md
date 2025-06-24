# Pe Foc de Lemne - Frontend Testing Plan

## Test Scope
Full functional testing of the Pe Foc de Lemne e-commerce platform using browser automation.

## Test Environment
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Browser: Chrome/Chromium via MCP

## Test Categories

### 1. Homepage Tests
- [ ] Page loads successfully
- [ ] Hero section displays correctly
- [ ] Featured products are visible
- [ ] Navigation menu works
- [ ] Footer links are functional
- [ ] Responsive design on different viewports

### 2. Product Listing Tests
- [ ] Products page loads
- [ ] Product grid displays correctly
- [ ] Search functionality works
- [ ] Category filtering works
- [ ] Pagination (if applicable)
- [ ] Product cards show correct information

### 3. Product Detail Tests
- [ ] Individual product pages load
- [ ] Product images display
- [ ] Product information is complete
- [ ] Add to cart functionality
- [ ] Quantity selection works
- [ ] Price calculations are correct

### 4. Shopping Cart Tests
- [ ] Cart page loads
- [ ] Items are displayed correctly
- [ ] Quantity can be updated
- [ ] Items can be removed
- [ ] Total price calculations
- [ ] Continue shopping link works
- [ ] Checkout button works

### 5. Checkout Flow Tests
- [ ] Checkout page loads
- [ ] Form validation works
- [ ] Phone number verification
- [ ] Order submission
- [ ] Success/error messages

### 6. Search & Filter Tests
- [ ] Search bar functionality
- [ ] Search results accuracy
- [ ] Filter by category
- [ ] Filter by price (if available)
- [ ] Clear filters functionality

### 7. Navigation Tests
- [ ] All menu links work
- [ ] Logo link returns to homepage
- [ ] Breadcrumbs (if applicable)
- [ ] Mobile menu functionality

### 8. Error Handling Tests
- [ ] 404 page displays correctly
- [ ] Network error handling
- [ ] Form validation errors
- [ ] API error responses

### 9. Performance Tests
- [ ] Page load times
- [ ] Image loading
- [ ] API response times
- [ ] Smooth scrolling and transitions

### 10. Cross-browser Tests
- [ ] Chrome/Chromium
- [ ] Different viewport sizes (mobile, tablet, desktop)

## Issue Logging Format
Each issue will be logged with:
- Timestamp
- Test category
- Page URL
- Issue description
- Severity (Critical, High, Medium, Low)
- Screenshot
- Browser console errors (if any)
- Network errors (if any)

## Success Criteria
- All critical user journeys complete without errors
- No JavaScript errors in console
- All API calls return successful responses
- Page load times under 3 seconds
- Mobile responsiveness verified