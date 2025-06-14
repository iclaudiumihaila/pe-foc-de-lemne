# Task 09: Create Database Indexes Setup

**Task ID**: 09_database_indexes_setup  
**Title**: Create database indexes setup  
**Phase**: Backend Infrastructure  
**Developer Role**: Active  

## Task Description
Implement index creation for phone_number, category_id, order_number, session_id

## Deliverable
backend/app/database.py with index creation function

## Dependencies
- 08_mongodb_connection_basic

## Acceptance Criteria
- All indexes created successfully in MongoDB
- Indexes match architecture.md specifications
- Index creation is idempotent (safe to run multiple times)
- Performance optimizations for common queries

## Implementation Plan
1. Add index creation function to existing database.py
2. Implement indexes for users collection (phone_number unique)
3. Implement indexes for products collection (category_id, active, featured, name text)
4. Implement indexes for categories collection (name unique, display_order)
5. Implement indexes for orders collection (order_number unique, customer_phone, status, created_at)
6. Implement indexes for cart_sessions collection (session_id unique, TTL)
7. Add function to create all indexes at once
8. Include error handling and logging

## Required Indexes
Based on architecture.md specifications:

**users Collection:**
- phone_number: unique index
- role: non-unique index for admin queries
- created_at: TTL index for cleanup (customers only)

**products Collection:**
- category_id: non-unique index
- active: non-unique index
- featured: non-unique index
- name: text index for search
- price: non-unique index for sorting

**categories Collection:**
- name: unique index
- display_order: non-unique index
- active: non-unique index

**orders Collection:**
- order_number: unique index
- customer_phone: non-unique index
- status: non-unique index
- created_at: non-unique index for date queries
- verification_code: sparse index (TTL: 10 minutes)

**cart_sessions Collection:**
- session_id: unique index
- created_at: TTL index (expires after 24 hours)

## Testing
Verify all indexes created successfully in MongoDB.

## Estimated Time
20 minutes