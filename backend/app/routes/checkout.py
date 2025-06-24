"""
Checkout Routes for Simplified Phone-Based Flow
Task ID: 08

Handles phone verification, address management, and order placement
without traditional user accounts.
"""

from flask import Blueprint, request, jsonify, current_app, g
from datetime import datetime, timedelta
import logging
from app.models.customer_phone import CustomerPhone
from app.services.sms.sms_manager import get_sms_manager
from app.services.sms.provider_interface import SmsMessage
from app.utils.checkout_rate_limiter import (
    get_checkout_rate_limiter,
    check_sms_limit_phone,
    check_sms_limit_ip,
    record_sms_sent
)
from app.utils.checkout_auth import checkout_auth_required, checkout_auth_optional

logger = logging.getLogger(__name__)

checkout_bp = Blueprint('checkout', __name__, url_prefix='/api/checkout')


@checkout_bp.route('/session', methods=['GET'])
@checkout_auth_optional
def get_session_info():
    """
    Get current session info - authentication optional.
    Used to check if user is already authenticated.
    """
    if g.is_authenticated:
        # Find customer to get latest info
        customer = CustomerPhone.find_by_phone(g.customer_phone)
        if customer:
            return jsonify({
                'success': True,
                'authenticated': True,
                'customer': {
                    'phone_masked': f"****{g.customer_phone[-4:]}",
                    'name': customer.name or '',
                    'address_count': len(customer.addresses),
                    'has_ordered_before': customer.total_orders > 0
                }
            }), 200
    
    return jsonify({
        'success': True,
        'authenticated': False,
        'message': 'Nu sunteți autentificat'
    }), 200


def get_client_ip():
    """Get client IP address from request"""
    # Check for forwarded IP first
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
    return request.environ.get('REMOTE_ADDR', 'unknown')


@checkout_bp.route('/phone/send-code', methods=['POST'])
def send_verification_code():
    """
    Send SMS verification code to phone number.
    
    Rate limits:
    - 3 SMS per phone per day
    - 5 SMS per IP per hour
    """
    logger.info(f"=== SEND VERIFICATION CODE START ===")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request headers: {dict(request.headers)}")
    logger.info(f"Request data: {request.get_data()}")
    
    try:
        data = request.get_json()
        logger.info(f"Parsed JSON data: {data}")
        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Date lipsă în cerere'
                }
            }), 400
        
        phone = data.get('phone')
        logger.info(f"Phone from request: {phone}")
        if not phone:
            logger.error("Phone not provided in request")
            return jsonify({
                'success': False,
                'error': {
                    'code': 'PHONE_REQUIRED',
                    'message': 'Numărul de telefon este obligatoriu'
                }
            }), 400
        
        # Create temporary instance for validation
        temp_customer = CustomerPhone()
        
        # Validate phone format
        validation_error = temp_customer.validate_phone(phone)
        logger.info(f"Phone validation result: {validation_error}")
        if validation_error:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_PHONE',
                    'message': validation_error
                }
            }), 400
        
        # Normalize phone number
        normalized_phone = temp_customer.normalize_phone(phone)
        logger.info(f"Normalized phone: {normalized_phone}")
        
        # Get client IP
        client_ip = get_client_ip()
        logger.info(f"Client IP: {client_ip}")
        
        # Check rate limits
        rate_limiter = get_checkout_rate_limiter()
        
        # Check phone daily limit
        phone_allowed, phone_info = check_sms_limit_phone(normalized_phone)
        logger.info(f"Phone rate limit check - allowed: {phone_allowed}, info: {phone_info}")
        if not phone_allowed:
            error_info = rate_limiter.get_error_message('sms_per_phone_per_day', phone_info)
            return jsonify({
                'success': False,
                'error': error_info
            }), 429
        
        # Check IP hourly limit
        ip_allowed, ip_info = check_sms_limit_ip(client_ip)
        if not ip_allowed:
            error_info = rate_limiter.get_error_message('sms_per_ip_per_hour', ip_info)
            return jsonify({
                'success': False,
                'error': error_info
            }), 429
        
        # Generate verification code
        sms_manager = get_sms_manager()
        code = sms_manager.generate_verification_code()
        
        # Find or create customer record
        customer = CustomerPhone.find_by_phone(normalized_phone)
        if not customer:
            customer = CustomerPhone({'phone': normalized_phone})
        
        # Store verification code
        if not customer.verification:
            customer.verification = {}
        
        customer.verification['code'] = code
        customer.verification['code_expires'] = datetime.utcnow() + timedelta(minutes=5)
        customer.verification['attempts'] = 0
        customer.verification['last_code_sent'] = datetime.utcnow()
        
        # Update attempts today
        if customer.verification.get('last_code_sent'):
            last_sent = customer.verification['last_code_sent']
            if isinstance(last_sent, str):
                from dateutil import parser
                last_sent = parser.parse(last_sent)
            
            if last_sent.date() == datetime.utcnow().date():
                customer.verification['attempts_today'] = customer.verification.get('attempts_today', 0) + 1
            else:
                customer.verification['attempts_today'] = 1
        else:
            customer.verification['attempts_today'] = 1
        
        # Save to database
        customer.save()
        
        # Create SMS message
        message_body = f"Codul dvs. de verificare este: {code}\nValabil 5 minute.\nPe Foc de Lemne"
        sms_message = SmsMessage(
            to=normalized_phone,
            body=message_body,
            message_type='otp'
        )
        
        # Send SMS
        sms_result = sms_manager.send_sms(sms_message)
        
        if not sms_result.success:
            logger.error(f"SMS send failed: {sms_result.error_message}")
            return jsonify({
                'success': False,
                'error': {
                    'code': sms_result.error_code or 'SMS_SEND_FAILED',
                    'message': sms_result.error_message or 'Nu am putut trimite SMS-ul. Încercați din nou.'
                }
            }), 500
        
        # Record successful SMS for rate limiting
        record_sms_sent(normalized_phone, client_ip)
        
        # Log for monitoring
        logger.info(f"Verification code sent to phone ending in ****{normalized_phone[-4:]}")
        
        # Response
        response = {
            'success': True,
            'message': 'Cod de verificare trimis',
            'phone_masked': f"****{normalized_phone[-4:]}",
            'expires_in_seconds': 300  # 5 minutes
        }
        
        # Include code in development mode
        if current_app.config.get('DEBUG'):
            # In development, the mock provider returns the code
            response['debug_code'] = code
            response['debug_message'] = 'Development mode - check console for SMS'
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Send verification code error: {str(e)}")
        logger.error(f"Exception type: {type(e)}")
        logger.error(f"Traceback: ", exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': 'Eroare de server. Încercați din nou.'
            }
        }), 500


@checkout_bp.route('/phone/verify-code', methods=['POST'])
def verify_code():
    """
    Verify SMS code and create session.
    
    Rate limit: 5 attempts per code
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Date lipsă în cerere'
                }
            }), 400
        
        phone = data.get('phone')
        code = data.get('code')
        
        if not phone:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'PHONE_REQUIRED',
                    'message': 'Numărul de telefon este obligatoriu'
                }
            }), 400
        
        if not code:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'CODE_REQUIRED',
                    'message': 'Codul de verificare este obligatoriu'
                }
            }), 400
        
        # Validate phone format
        temp_customer = CustomerPhone()
        validation_error = temp_customer.validate_phone(phone)
        if validation_error:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_PHONE',
                    'message': validation_error
                }
            }), 400
        
        normalized_phone = temp_customer.normalize_phone(phone)
        
        # Check rate limit for verification attempts
        from app.utils.checkout_rate_limiter import check_verify_attempts, record_verify_attempt
        allowed, info = check_verify_attempts(normalized_phone, code)
        
        if not allowed:
            rate_limiter = get_checkout_rate_limiter()
            error_info = rate_limiter.get_error_message('verify_attempts_per_code', info)
            return jsonify({
                'success': False,
                'error': error_info
            }), 429
        
        # Find customer record
        customer = CustomerPhone.find_by_phone(normalized_phone)
        if not customer:
            # Record failed attempt
            record_verify_attempt(normalized_phone, code)
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_CODE',
                    'message': 'Cod invalid sau expirat'
                }
            }), 400
        
        # Check if code matches and is not expired
        stored_code = customer.verification.get('code')
        code_expires = customer.verification.get('code_expires')
        
        if not stored_code or not code_expires:
            record_verify_attempt(normalized_phone, code)
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NO_PENDING_CODE',
                    'message': 'Nu există cod de verificare activ'
                }
            }), 400
        
        # Check expiry
        if isinstance(code_expires, str):
            from dateutil import parser
            code_expires = parser.parse(code_expires)
        
        if datetime.utcnow() > code_expires:
            record_verify_attempt(normalized_phone, code)
            return jsonify({
                'success': False,
                'error': {
                    'code': 'CODE_EXPIRED',
                    'message': 'Codul a expirat. Solicitați unul nou.'
                }
            }), 400
        
        # Verify code
        if str(stored_code) != str(code):
            record_verify_attempt(normalized_phone, code)
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_CODE',
                    'message': 'Cod invalid'
                }
            }), 400
        
        # Code is valid - clear verification data
        customer.verification['code'] = None
        customer.verification['code_expires'] = None
        customer.verification['attempts'] = 0
        customer.verification['verified_at'] = datetime.utcnow()
        customer.save()
        
        # Generate JWT session token
        import jwt
        from datetime import timedelta
        
        payload = {
            'phone': normalized_phone,
            'customer_id': str(customer._id),
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow(),
            'type': 'checkout_session'
        }
        
        secret_key = current_app.config.get('SECRET_KEY', 'dev-secret-key')
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        
        # Log successful verification
        logger.info(f"Phone verified successfully: ****{normalized_phone[-4:]}")
        
        # Response
        return jsonify({
            'success': True,
            'message': 'Telefon verificat cu succes',
            'token': token,
            'customer': {
                'phone_masked': f"****{normalized_phone[-4:]}",
                'name': customer.name or '',
                'addresses': [
                    {
                        'id': str(addr['_id']),
                        'street': addr['street'],
                        'city': addr['city'],
                        'county': addr['county'],
                        'postal_code': addr['postal_code'],
                        'notes': addr.get('notes', ''),
                        'is_default': addr.get('is_default', False)
                    }
                    for addr in customer.addresses
                ],
                'has_ordered_before': customer.total_orders > 0
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Verify code error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': 'Eroare de server. Încercați din nou.'
            }
        }), 500


@checkout_bp.route('/addresses', methods=['GET'])
@checkout_auth_required
def get_addresses():
    """
    Get customer's saved addresses.
    
    Returns addresses sorted by:
    1. Default address first
    2. Most recently used
    3. Most frequently used
    """
    try:
        # Find customer by authenticated phone
        customer = CustomerPhone.find_by_phone(g.customer_phone)
        
        if not customer:
            logger.error(f"Customer not found for authenticated phone: {g.customer_phone}")
            return jsonify({
                'success': False,
                'error': {
                    'code': 'CUSTOMER_NOT_FOUND',
                    'message': 'Contul nu a fost găsit. Verificați din nou.'
                }
            }), 404
        
        # Format addresses for response
        addresses = []
        for addr in customer.addresses:
            address_data = {
                'id': str(addr['_id']),
                'street': addr['street'],
                'city': addr['city'],
                'county': addr['county'],
                'postal_code': addr['postal_code'],
                'notes': addr.get('notes', ''),
                'is_default': addr.get('is_default', False),
                'usage_count': addr.get('usage_count', 0),
                'last_used': addr.get('last_used').isoformat() if addr.get('last_used') else None,
                'created_at': addr.get('created_at').isoformat() if addr.get('created_at') else None
            }
            addresses.append(address_data)
        
        # Sort addresses: default first, then by usage
        addresses.sort(key=lambda x: (
            not x['is_default'],  # Default comes first
            -x['usage_count'],    # Higher usage count first
            x['created_at'] or '' # Older addresses first if same usage
        ))
        
        # Log request
        logger.info(f"Retrieved {len(addresses)} addresses for customer {g.customer_phone[-4:]}")
        
        return jsonify({
            'success': True,
            'addresses': addresses,
            'count': len(addresses),
            'customer': {
                'phone_masked': f"****{g.customer_phone[-4:]}",
                'name': customer.name or '',
                'has_ordered_before': customer.total_orders > 0
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get addresses error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': 'Eroare la încărcarea adreselor. Încercați din nou.'
            }
        }), 500


@checkout_bp.route('/addresses', methods=['POST'])
@checkout_auth_required
def add_address():
    """
    Add new delivery address.
    
    Validates Romanian address format and enforces 50 address limit.
    First address is automatically set as default.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Date lipsă în cerere'
                }
            }), 400
        
        # Find customer
        customer = CustomerPhone.find_by_phone(g.customer_phone)
        if not customer:
            logger.error(f"Customer not found for authenticated phone: {g.customer_phone}")
            return jsonify({
                'success': False,
                'error': {
                    'code': 'CUSTOMER_NOT_FOUND',
                    'message': 'Contul nu a fost găsit'
                }
            }), 404
        
        # Check address limit
        if len(customer.addresses) >= CustomerPhone.MAX_ADDRESSES:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'ADDRESS_LIMIT_EXCEEDED',
                    'message': f'Ați atins limita maximă de {CustomerPhone.MAX_ADDRESSES} adrese salvate'
                }
            }), 400
        
        # Extract address fields
        address_data = {
            'street': data.get('street', '').strip(),
            'city': data.get('city', '').strip(),
            'county': data.get('county', '').strip(),
            'postal_code': data.get('postal_code', '').strip(),
            'notes': data.get('notes', '').strip()
        }
        
        # Validate address
        validation_errors = customer.validate_address(address_data)
        if validation_errors:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Date invalide',
                    'details': validation_errors
                }
            }), 400
        
        # Create new address
        from bson import ObjectId
        new_address = {
            '_id': ObjectId(),
            'street': address_data['street'],
            'city': address_data['city'],
            'county': address_data['county'],
            'postal_code': address_data['postal_code'],
            'notes': address_data['notes'],
            'is_default': len(customer.addresses) == 0,  # First address is default
            'usage_count': 0,
            'created_at': datetime.utcnow()
        }
        
        # Check if setting as default
        if data.get('set_as_default', False) and len(customer.addresses) > 0:
            # Remove default from other addresses
            for addr in customer.addresses:
                addr['is_default'] = False
            new_address['is_default'] = True
        
        # Add address
        customer.addresses.append(new_address)
        
        # Save customer
        customer.save()
        
        # Log action
        logger.info(f"Address added for customer {g.customer_phone[-4:]}")
        
        # Format response
        response_address = {
            'id': str(new_address['_id']),
            'street': new_address['street'],
            'city': new_address['city'],
            'county': new_address['county'],
            'postal_code': new_address['postal_code'],
            'notes': new_address['notes'],
            'is_default': new_address['is_default'],
            'usage_count': 0,
            'created_at': new_address['created_at'].isoformat()
        }
        
        return jsonify({
            'success': True,
            'message': 'Adresă adăugată cu succes',
            'address': response_address,
            'total_addresses': len(customer.addresses)
        }), 201
        
    except Exception as e:
        logger.error(f"Add address error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': 'Eroare la salvarea adresei. Încercați din nou.'
            }
        }), 500


@checkout_bp.route('/addresses/<address_id>', methods=['PUT'])
@checkout_auth_required
def update_address(address_id):
    """
    Update existing delivery address.
    
    Only the owner can update their addresses.
    Preserves usage statistics and creation date.
    """
    try:
        # Validate address_id format
        from bson import ObjectId
        from bson.errors import InvalidId
        
        try:
            address_obj_id = ObjectId(address_id)
        except InvalidId:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_ADDRESS_ID',
                    'message': 'ID adresă invalid'
                }
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': 'Date lipsă în cerere'
                }
            }), 400
        
        # Find customer
        customer = CustomerPhone.find_by_phone(g.customer_phone)
        if not customer:
            logger.error(f"Customer not found for authenticated phone: {g.customer_phone}")
            return jsonify({
                'success': False,
                'error': {
                    'code': 'CUSTOMER_NOT_FOUND',
                    'message': 'Contul nu a fost găsit'
                }
            }), 404
        
        # Find address in customer's list
        address_index = None
        existing_address = None
        for idx, addr in enumerate(customer.addresses):
            if addr['_id'] == address_obj_id:
                address_index = idx
                existing_address = addr
                break
        
        if address_index is None:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'ADDRESS_NOT_FOUND',
                    'message': 'Adresa nu a fost găsită'
                }
            }), 404
        
        # Extract and validate updated fields
        update_data = {}
        
        # Only update provided fields
        if 'street' in data:
            update_data['street'] = data['street'].strip()
        if 'city' in data:
            update_data['city'] = data['city'].strip()
        if 'county' in data:
            update_data['county'] = data['county'].strip()
        if 'postal_code' in data:
            update_data['postal_code'] = data['postal_code'].strip()
        if 'notes' in data:
            update_data['notes'] = data['notes'].strip()
        
        # Merge with existing data for validation
        validation_data = {
            'street': update_data.get('street', existing_address['street']),
            'city': update_data.get('city', existing_address['city']),
            'county': update_data.get('county', existing_address['county']),
            'postal_code': update_data.get('postal_code', existing_address['postal_code']),
            'notes': update_data.get('notes', existing_address.get('notes', ''))
        }
        
        # Validate updated address
        validation_errors = customer.validate_address(validation_data)
        if validation_errors:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Date invalide',
                    'details': validation_errors
                }
            }), 400
        
        # Update address fields
        for field, value in update_data.items():
            customer.addresses[address_index][field] = value
        
        # Handle set_as_default
        if data.get('set_as_default', False):
            # Remove default from all addresses
            for addr in customer.addresses:
                addr['is_default'] = False
            # Set this one as default
            customer.addresses[address_index]['is_default'] = True
        
        # Update timestamp
        customer.addresses[address_index]['updated_at'] = datetime.utcnow()
        
        # Save customer
        customer.save()
        
        # Log action
        logger.info(f"Address {address_id} updated for customer {g.customer_phone[-4:]}")
        
        # Format response
        updated_address = customer.addresses[address_index]
        response_address = {
            'id': str(updated_address['_id']),
            'street': updated_address['street'],
            'city': updated_address['city'],
            'county': updated_address['county'],
            'postal_code': updated_address['postal_code'],
            'notes': updated_address.get('notes', ''),
            'is_default': updated_address.get('is_default', False),
            'usage_count': updated_address.get('usage_count', 0),
            'created_at': updated_address.get('created_at').isoformat() if updated_address.get('created_at') else None,
            'updated_at': updated_address.get('updated_at').isoformat() if updated_address.get('updated_at') else None
        }
        
        return jsonify({
            'success': True,
            'message': 'Adresă actualizată cu succes',
            'address': response_address
        }), 200
        
    except Exception as e:
        logger.error(f"Update address error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': 'Eroare la actualizarea adresei. Încercați din nou.'
            }
        }), 500


@checkout_bp.route('/addresses/<address_id>', methods=['DELETE'])
@checkout_auth_required
def delete_address(address_id):
    """
    Delete delivery address.
    
    Cannot delete the last address.
    If deleting default address, the next address becomes default.
    """
    try:
        # Validate address_id format
        from bson import ObjectId
        from bson.errors import InvalidId
        
        try:
            address_obj_id = ObjectId(address_id)
        except InvalidId:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_ADDRESS_ID',
                    'message': 'ID adresă invalid'
                }
            }), 400
        
        # Find customer
        customer = CustomerPhone.find_by_phone(g.customer_phone)
        if not customer:
            logger.error(f"Customer not found for authenticated phone: {g.customer_phone}")
            return jsonify({
                'success': False,
                'error': {
                    'code': 'CUSTOMER_NOT_FOUND',
                    'message': 'Contul nu a fost găsit'
                }
            }), 404
        
        # Check if this is the last address
        if len(customer.addresses) <= 1:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'LAST_ADDRESS',
                    'message': 'Nu puteți șterge ultima adresă. Trebuie să aveți cel puțin o adresă salvată.'
                }
            }), 400
        
        # Find address in customer's list
        address_index = None
        address_to_delete = None
        for idx, addr in enumerate(customer.addresses):
            if addr['_id'] == address_obj_id:
                address_index = idx
                address_to_delete = addr
                break
        
        if address_index is None:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'ADDRESS_NOT_FOUND',
                    'message': 'Adresa nu a fost găsită'
                }
            }), 404
        
        # Check if deleting default address
        was_default = address_to_delete.get('is_default', False)
        
        # Remove the address
        customer.addresses.pop(address_index)
        
        # If we deleted the default address, set the first remaining as default
        if was_default and customer.addresses:
            # Find the address with highest usage, or just use the first one
            best_address = max(customer.addresses, 
                             key=lambda x: (x.get('usage_count', 0), 
                                          x.get('created_at', datetime.min)))
            best_address['is_default'] = True
            
            logger.info(f"Reassigned default to address {best_address['_id']}")
        
        # Save customer
        customer.save()
        
        # Log action
        logger.info(f"Address {address_id} deleted for customer {g.customer_phone[-4:]}")
        
        # Return remaining addresses count and new default info
        new_default = None
        for addr in customer.addresses:
            if addr.get('is_default', False):
                new_default = {
                    'id': str(addr['_id']),
                    'street': addr['street'],
                    'city': addr['city']
                }
                break
        
        return jsonify({
            'success': True,
            'message': 'Adresă ștearsă cu succes',
            'remaining_addresses': len(customer.addresses),
            'new_default': new_default
        }), 200
        
    except Exception as e:
        logger.error(f"Delete address error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': 'Eroare la ștergerea adresei. Încercați din nou.'
            }
        }), 500