# Task 16: Create Order Data Model with MongoDB Schema

**Task ID**: 16_order_data_model  
**Title**: Create Order data model with MongoDB schema  
**Phase**: Backend Data Models  
**Developer Role**: Active  

## Task Description
Create Order model class with MongoDB operations and order lifecycle management

## Deliverable
backend/app/models/order.py with Order class and database operations

## Dependencies
- 09_database_indexes_setup
- 10_input_validation_middleware
- 13_user_data_model
- 14_product_data_model

## Acceptance Criteria
- Order model matches architecture MongoDB schema
- Order status lifecycle management
- Order item management with product references
- Total calculation and validation
- MongoDB CRUD operations (create, find, update)
- Customer and delivery information handling
- Order number generation (unique)
- Proper indexing utilization
- Input validation integration
- Order history and tracking

## Implementation Plan
1. Create backend/app/models/order.py file
2. Import required dependencies (pymongo, datetime, decimal)
3. Implement Order class with schema-compliant structure
4. Add order status management and lifecycle
5. Add order item validation and management
6. Add total calculation and validation
7. Implement CRUD operations (create, find, update)
8. Add order number generation
9. Add customer and delivery information handling
10. Integrate with validation middleware
11. Add proper error handling and logging

## Order Schema Requirements
Based on architecture.md MongoDB schema:

```json
{
  "_id": "ObjectId",
  "order_number": "string (unique indexed, auto-generated)",
  "customer_phone": "string (E.164 format, indexed)",
  "customer_name": "string (2-50 chars)",
  "status": "string (enum: pending, confirmed, preparing, ready, delivered, cancelled)",
  "items": [
    {
      "product_id": "ObjectId (reference to products)",
      "product_name": "string (snapshot)",
      "quantity": "integer (> 0)",
      "unit_price": "decimal (2 decimal places)",
      "total_price": "decimal (calculated)"
    }
  ],
  "subtotal": "decimal (calculated from items)",
  "total": "decimal (subtotal, no tax/delivery for now)",
  "delivery_type": "string (enum: pickup, delivery)",
  "delivery_address": "object (for delivery orders)",
  "delivery_phone": "string (E.164 format, optional)",
  "requested_time": "datetime (pickup/delivery time)",
  "special_instructions": "string (optional, max 500 chars)",
  "created_at": "datetime",
  "updated_at": "datetime",
  "confirmed_at": "datetime (optional)",
  "ready_at": "datetime (optional)",
  "delivered_at": "datetime (optional)"
}
```

## Required Methods
- `Order.__init__()` - Initialize Order object
- `Order.create()` - Create new order in database
- `Order.find_by_id()` - Find order by ObjectId
- `Order.find_by_order_number()` - Find order by order number
- `Order.find_by_customer()` - Find orders by customer phone
- `Order.find_by_status()` - Find orders by status
- `Order.update()` - Update order data
- `Order.update_status()` - Update order status with timestamp
- `Order.calculate_totals()` - Calculate subtotal and total
- `Order.add_item()` - Add item to order
- `Order.to_dict()` - Convert to dictionary representation
- `Order.generate_order_number()` - Generate unique order number

## Order Status Lifecycle
- **pending**: Initial status when order created
- **confirmed**: Order confirmed and accepted
- **preparing**: Order being prepared
- **ready**: Order ready for pickup/delivery
- **delivered**: Order completed
- **cancelled**: Order cancelled

## Order Item Management
- Product reference validation
- Quantity validation (positive integers)
- Unit price validation (decimal precision)
- Total price calculation per item
- Product name snapshot for order history

## Total Calculation
- Subtotal calculation from all items
- Total calculation (subtotal only for now)
- Decimal precision handling
- Validation of calculated amounts

## Order Number Generation
- Unique order number generation
- Format: ORD-YYYYMMDD-NNNN (e.g., ORD-20250113-0001)
- Daily counter reset
- Collision handling

## Delivery Information
- Pickup vs delivery type validation
- Delivery address handling for delivery orders
- Phone number validation
- Requested time validation

## Testing
Verify Order model CRUD operations and business logic work correctly.

## Estimated Time
35 minutes

## Notes
This creates the core Order model for order management. Includes status lifecycle, item management, and total calculation following MongoDB schema from architecture.