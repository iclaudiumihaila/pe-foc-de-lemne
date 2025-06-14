# Task 13: Create User Data Model with MongoDB Schema

**Task ID**: 13_user_data_model  
**Title**: Create User data model with MongoDB schema  
**Phase**: Backend Data Models  
**Developer Role**: Active  

## Task Description
Create User model class with MongoDB operations and validation

## Deliverable
backend/app/models/user.py with User class and database operations

## Dependencies
- 09_database_indexes_setup
- 10_input_validation_middleware

## Acceptance Criteria
- User model matches architecture MongoDB schema
- Password hashing and verification methods
- Phone number validation and formatting
- MongoDB CRUD operations (create, find, update)
- User role management (customer, admin)
- Proper indexing utilization
- Input validation integration
- Error handling for duplicate users

## Implementation Plan
1. Create backend/app/models/ directory
2. Create backend/app/models/__init__.py file
3. Create backend/app/models/user.py file
4. Import required dependencies (pymongo, bcrypt, datetime)
5. Implement User class with schema-compliant structure
6. Add password hashing/verification methods
7. Add phone number validation and formatting
8. Implement CRUD operations (create_user, find_user, update_user)
9. Add role management functionality
10. Integrate with validation middleware
11. Add proper error handling and logging

## User Schema Requirements
Based on architecture.md MongoDB schema:

```json
{
  "_id": "ObjectId",
  "phone_number": "string (E.164 format, unique index)",
  "name": "string (2-50 chars)",
  "role": "string (enum: customer, admin)",
  "password_hash": "string (bcrypt)",
  "is_verified": "boolean (default: false)",
  "verification_code": "string (optional, TTL)",
  "verification_expires": "datetime (TTL index)",
  "created_at": "datetime",
  "updated_at": "datetime",
  "last_login": "datetime (optional)"
}
```

## Required Methods
- `User.__init__()` - Initialize User object
- `User.create()` - Create new user in database  
- `User.find_by_phone()` - Find user by phone number
- `User.find_by_id()` - Find user by ObjectId
- `User.update()` - Update user data
- `User.set_password()` - Hash and set password
- `User.verify_password()` - Verify password against hash
- `User.set_verification_code()` - Set SMS verification code
- `User.verify_phone()` - Mark phone as verified
- `User.to_dict()` - Convert to dictionary (exclude sensitive data)

## Security Requirements
- Password hashing with bcrypt (12 rounds minimum)
- No plain text passwords stored
- Sensitive data excluded from dictionary representation
- Phone number normalization to E.164 format
- Verification code TTL handling

## Testing
Verify User model CRUD operations and password handling work correctly.

## Estimated Time
25 minutes

## Notes
This creates the foundational User model for authentication and user management. Follows MongoDB schema from architecture with proper security measures.