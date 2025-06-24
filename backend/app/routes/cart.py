"""
Shopping Cart Routes for Local Producer Web Application

This module provides shopping cart endpoints including adding items,
retrieving cart contents, and managing cart sessions.
"""

import logging
from flask import Blueprint, request, jsonify
from bson import ObjectId
from app.models.cart import Cart
from app.models.product import Product
from app.utils.validators import validate_json
from app.utils.error_handlers import (
    ValidationError, NotFoundError,
    success_response, create_error_response
)

# Create cart blueprint
cart_bp = Blueprint('cart', __name__)

# Cart item JSON schema for validation
CART_ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "product_id": {
            "type": "string",
            "minLength": 24,
            "maxLength": 24,
            "pattern": "^[0-9a-fA-F]{24}$"
        },
        "quantity": {
            "type": "integer",
            "minimum": 1,
            "maximum": 100
        },
        "session_id": {
            "type": "string",
            "minLength": 24,
            "maxLength": 24
        }
    },
    "required": ["product_id", "quantity"],
    "additionalProperties": False
}


@cart_bp.route('/', methods=['POST'])
@validate_json(CART_ITEM_SCHEMA)
def add_to_cart():
    """
    Add item to shopping cart.
    
    Request Body:
        - product_id (str): Product ObjectId (required)
        - quantity (int): Quantity to add (required, 1-100)
        - session_id (str): Cart session ID (optional)
    
    Response:
        - 200: Item added successfully with updated cart
        - 400: Invalid request data or validation error
        - 404: Product not found
        - 500: Server error
    """
    try:
        data = request.get_json()
        product_id = data['product_id']
        quantity = data['quantity']
        session_id = data.get('session_id')
        
        # Validate product_id format
        try:
            ObjectId(product_id)
        except Exception:
            response, status = create_error_response(
                "VAL_001",
                "Invalid product ID format",
                400
            )
            return jsonify(response), status
        
        # Get or create cart session
        cart = None
        if session_id:
            cart = Cart.find_by_session_id(session_id)
        
        if not cart:
            # Create new cart with the provided session_id
            cart = Cart()
            if session_id:
                cart.session_id = session_id
        
        # Validate product exists and is available
        product = Product.find_by_id(product_id)
        if not product:
            response, status = create_error_response(
                "NOT_001",
                "Product not found",
                404
            )
            return jsonify(response), status
        
        if not product.is_available:
            response, status = create_error_response(
                "VAL_002",
                "Product is not available for purchase",
                400
            )
            return jsonify(response), status
        
        if product.stock_quantity <= 0:
            response, status = create_error_response(
                "VAL_003",
                "Product is out of stock",
                400
            )
            return jsonify(response), status
        
        # Add item to cart
        try:
            cart.add_item(product_id, quantity)
        except ValueError as e:
            response, status = create_error_response(
                "VAL_004",
                str(e),
                400
            )
            return jsonify(response), status
        
        # Save cart to database
        if not cart.save():
            response, status = create_error_response(
                "DB_001",
                "Failed to save cart",
                500
            )
            return jsonify(response), status
        
        # Prepare response with updated cart
        cart_data = cart.to_dict()
        
        response_data = {
            'session_id': cart.session_id,
            'cart': cart_data
        }
        
        logging.info(f"Item added to cart: product_id={product_id}, quantity={quantity}, session_id={cart.session_id}")
        
        return jsonify(success_response(
            response_data,
            "Item added to cart successfully"
        )), 200
        
    except Exception as e:
        logging.error(f"Error adding item to cart: {str(e)}")
        response, status = create_error_response(
            "CART_001",
            "Failed to add item to cart",
            500
        )
        return jsonify(response), status


@cart_bp.route('/<session_id>', methods=['GET'])
def get_cart_contents(session_id):
    """
    Get cart contents by session ID.
    
    Args:
        session_id (str): Cart session ID
    
    Response:
        - 200: Cart contents retrieved successfully
        - 404: Cart session not found or expired
        - 500: Server error
    """
    try:
        # Validate session_id format
        if len(session_id) != 24:
            response, status = create_error_response(
                "VAL_001",
                "Invalid session ID format",
                400
            )
            return jsonify(response), status
        
        # Find cart by session ID
        cart = Cart.find_by_session_id(session_id)
        
        if not cart:
            response, status = create_error_response(
                "NOT_002",
                "Cart session not found or expired",
                404
            )
            return jsonify(response), status
        
        # Check if cart is expired
        if cart.is_expired():
            response, status = create_error_response(
                "CART_002",
                "Cart session has expired",
                404
            )
            return jsonify(response), status
        
        # Return cart contents
        cart_data = cart.to_dict()
        
        logging.info(f"Cart contents retrieved: session_id={session_id}, items={cart.total_items}")
        
        return jsonify(success_response(
            cart_data,
            "Cart contents retrieved successfully"
        )), 200
        
    except Exception as e:
        logging.error(f"Error retrieving cart contents: {str(e)}")
        response, status = create_error_response(
            "CART_003",
            "Failed to retrieve cart contents",
            500
        )
        return jsonify(response), status


@cart_bp.route('/<session_id>/item/<product_id>', methods=['PUT'])
@validate_json({
    "type": "object",
    "properties": {
        "quantity": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100
        }
    },
    "required": ["quantity"],
    "additionalProperties": False
})
def update_cart_item(session_id, product_id):
    """
    Update item quantity in cart.
    
    Args:
        session_id (str): Cart session ID
        product_id (str): Product ObjectId
    
    Request Body:
        - quantity (int): New quantity (0 to remove item)
    
    Response:
        - 200: Item updated successfully
        - 400: Invalid request data
        - 404: Cart or product not found
        - 500: Server error
    """
    try:
        data = request.get_json()
        quantity = data['quantity']
        
        # Validate IDs format
        try:
            ObjectId(product_id)
        except Exception:
            response, status = create_error_response(
                "VAL_001",
                "Invalid product ID format",
                400
            )
            return jsonify(response), status
        
        # Find cart
        cart = Cart.find_by_session_id(session_id)
        if not cart:
            response, status = create_error_response(
                "NOT_002",
                "Cart session not found or expired",
                404
            )
            return jsonify(response), status
        
        # Update item quantity
        try:
            if quantity == 0:
                success = cart.remove_item(product_id)
                message = "Item removed from cart successfully"
            else:
                success = cart.update_item_quantity(product_id, quantity)
                message = "Item quantity updated successfully"
            
            if not success:
                response, status = create_error_response(
                    "NOT_003",
                    "Item not found in cart",
                    404
                )
                return jsonify(response), status
                
        except ValueError as e:
            response, status = create_error_response(
                "VAL_004",
                str(e),
                400
            )
            return jsonify(response), status
        
        # Save updated cart
        if not cart.save():
            response, status = create_error_response(
                "DB_001",
                "Failed to save cart",
                500
            )
            return jsonify(response), status
        
        # Return updated cart
        cart_data = cart.to_dict()
        
        logging.info(f"Cart item updated: session_id={session_id}, product_id={product_id}, quantity={quantity}")
        
        return jsonify(success_response(
            cart_data,
            message
        )), 200
        
    except Exception as e:
        logging.error(f"Error updating cart item: {str(e)}")
        response, status = create_error_response(
            "CART_004",
            "Failed to update cart item",
            500
        )
        return jsonify(response), status


@cart_bp.route('/<session_id>', methods=['DELETE'])
def clear_cart(session_id):
    """
    Clear all items from cart.
    
    Args:
        session_id (str): Cart session ID
    
    Response:
        - 200: Cart cleared successfully
        - 404: Cart session not found
        - 500: Server error
    """
    try:
        # Find cart
        cart = Cart.find_by_session_id(session_id)
        if not cart:
            response, status = create_error_response(
                "NOT_002",
                "Cart session not found or expired",
                404
            )
            return jsonify(response), status
        
        # Clear cart
        cart.clear()
        
        # Save updated cart
        if not cart.save():
            response, status = create_error_response(
                "DB_001",
                "Failed to save cart",
                500
            )
            return jsonify(response), status
        
        # Return empty cart
        cart_data = cart.to_dict()
        
        logging.info(f"Cart cleared: session_id={session_id}")
        
        return jsonify(success_response(
            cart_data,
            "Cart cleared successfully"
        )), 200
        
    except Exception as e:
        logging.error(f"Error clearing cart: {str(e)}")
        response, status = create_error_response(
            "CART_005",
            "Failed to clear cart",
            500
        )
        return jsonify(response), status