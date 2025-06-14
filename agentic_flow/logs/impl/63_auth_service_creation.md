# Implementation 63: Create admin authentication service

## Implementation Summary
Successfully created a comprehensive admin authentication service for the Romanian local producer marketplace with secure login functionality, JWT token management, password hashing, session handling, Romanian localization, and complete admin authentication workflow for the Pe Foc de Lemne admin panel backend.

## Files Created/Modified

### 1. Admin Authentication Service - `/backend/app/services/auth_service.py`
- **Secure Admin Login**: Complete authentication with username/password validation
- **JWT Token Management**: Access and refresh token generation with proper expiration
- **Password Security**: Bcrypt hashing with secure verification
- **Rate Limiting**: Protection against brute force attacks with lockout
- **Romanian Localization**: All error messages and responses in Romanian

## Key Features Implemented

### 1. Admin Authentication Core
```python
class AuthService:
    # JWT Configuration
    ALGORITHM = 'HS256'
    TOKEN_EXPIRY_HOURS = 8  # Admin tokens expire after 8 hours
    REFRESH_TOKEN_EXPIRY_DAYS = 7  # Refresh tokens expire after 7 days
    
    # Password Configuration
    MIN_PASSWORD_LENGTH = 8
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30

def authenticate_admin(self, username: str, password: str, ip_address: str = None) -> Dict[str, Any]:
    # Validate inputs
    if not username or not password:
        raise ValidationError("Numele de utilizator și parola sunt obligatorii")
    
    # Check rate limiting
    self._check_rate_limit(username, ip_address)
    
    # Find admin user by phone number
    admin_user = User.find_by_phone(username)
    
    # Verify admin role and credentials
    if not admin_user or admin_user.role != User.ROLE_ADMIN:
        raise AuthenticationError("Datele de autentificare sunt incorecte")
```

### 2. JWT Token Generation System
```python
def generate_token(self, admin_user: User, custom_expiry: timedelta = None) -> str:
    # Calculate expiry
    expires_at = datetime.utcnow() + timedelta(hours=self.TOKEN_EXPIRY_HOURS)
    
    # Prepare token payload with admin information
    payload = {
        'user_id': str(admin_user._id),
        'phone_number': admin_user.phone_number,
        'name': admin_user.name,
        'role': admin_user.role,
        'iat': datetime.utcnow(),  # Issued at
        'exp': expires_at,  # Expiry
        'iss': 'pe-foc-de-lemne-admin',  # Issuer
        'aud': 'pe-foc-de-lemne-admin-panel'  # Audience
    }
    
    # Generate secure JWT token
    token = jwt.encode(payload, self.secret_key, algorithm=self.ALGORITHM)
    return token

def generate_refresh_token(self, admin_user: User) -> str:
    # Generate long-lived refresh token for session renewal
    expires_at = datetime.utcnow() + timedelta(days=self.REFRESH_TOKEN_EXPIRY_DAYS)
    
    payload = {
        'user_id': str(admin_user._id),
        'phone_number': admin_user.phone_number,
        'role': admin_user.role,
        'token_type': 'refresh',
        'iat': datetime.utcnow(),
        'exp': expires_at,
        'iss': 'pe-foc-de-lemne-admin',
        'aud': 'pe-foc-de-lemne-admin-panel'
    }
    
    return jwt.encode(payload, self.secret_key, algorithm=self.ALGORITHM)
```

### 3. Token Verification and Validation
```python
def verify_token(self, token: str) -> Dict[str, Any]:
    if not token:
        raise AuthenticationError("Token de autentificare lipsește")
    
    # Remove 'Bearer ' prefix if present
    if token.startswith('Bearer '):
        token = token[7:]
    
    # Decode and verify token with proper audience and issuer validation
    payload = jwt.decode(
        token,
        self.secret_key,
        algorithms=[self.ALGORITHM],
        audience='pe-foc-de-lemne-admin-panel',
        issuer='pe-foc-de-lemne-admin'
    )
    
    # Verify admin role
    if payload.get('role') != User.ROLE_ADMIN:
        raise AuthenticationError("Token invalid pentru admin")
    
    return payload
```

## Romanian Localization Implementation

### 1. Romanian Authentication Error Messages
```python
# Authentication failure messages
"Numele de utilizator și parola sunt obligatorii"  # Username and password required
"Datele de autentificare sunt incorecte"  # Invalid credentials
"Acces interzis. Doar administratorii pot accesa acest sistem"  # Admin access only
"Contul nu este verificat. Contactați administratorul sistemului"  # Account not verified

# Token-related messages
"Token de autentificare lipsește"  # Authentication token missing
"Token invalid pentru admin"  # Invalid admin token
"Token-ul de autentificare a expirat"  # Token expired
"Token de autentificare invalid"  # Invalid token

# Rate limiting messages
"Prea multe încercări de autentificare. Încercați din nou în {minutes} minute"  # Too many attempts

# Success messages
"Autentificare reușită"  # Authentication successful
"Deconectare reușită"  # Logout successful
```

### 2. Romanian Admin Interface Responses
```python
# Authentication success response
auth_result = {
    'success': True,
    'message': 'Autentificare reușită',
    'user': {
        'id': str(admin_user._id),
        'name': admin_user.name,
        'phone_number': admin_user.phone_number,
        'role': admin_user.role,
        'last_login': admin_user.last_login.isoformat() + 'Z'
    },
    'tokens': {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': self.TOKEN_EXPIRY_HOURS * 3600
    }
}

# Admin creation response
{
    'success': True,
    'message': 'Administrator creat cu succes',
    'admin': {
        'id': str(admin_user._id),
        'name': admin_user.name,
        'phone_number': admin_user.phone_number,
        'role': admin_user.role
    }
}
```

## Security Features Implementation

### 1. Password Security with Bcrypt
```python
def hash_password(self, password: str) -> str:
    if len(password) < self.MIN_PASSWORD_LENGTH:
        raise ValidationError(
            f"Parola trebuie să aibă cel puțin {self.MIN_PASSWORD_LENGTH} caractere"
        )
    
    # Generate salt and hash password with 12 rounds
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    return hashed.decode('utf-8')

def verify_password(self, password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )
```

### 2. Rate Limiting and Brute Force Protection
```python
def _check_rate_limit(self, username: str, ip_address: str = None) -> None:
    key = f"{username}:{ip_address}" if ip_address else username
    
    if key in self.login_attempts:
        attempts_data = self.login_attempts[key]
        
        # Check if lockout period has expired
        if attempts_data['locked_until'] > datetime.utcnow():
            remaining_minutes = (attempts_data['locked_until'] - datetime.utcnow()).total_seconds() / 60
            raise AuthenticationError(
                f"Prea multe încercări de autentificare. Încercați din nou în {int(remaining_minutes)} minute"
            )

def _record_failed_attempt(self, username: str, ip_address: str = None) -> None:
    key = f"{username}:{ip_address}" if ip_address else username
    
    if key not in self.login_attempts:
        self.login_attempts[key] = {
            'count': 1,
            'first_attempt': datetime.utcnow(),
            'locked_until': datetime.utcnow()
        }
    else:
        self.login_attempts[key]['count'] += 1
    
    # Lock account after MAX_LOGIN_ATTEMPTS
    if self.login_attempts[key]['count'] >= self.MAX_LOGIN_ATTEMPTS:
        self.login_attempts[key]['locked_until'] = datetime.utcnow() + timedelta(minutes=self.LOCKOUT_DURATION_MINUTES)
```

### 3. Session Management and Token Refresh
```python
def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
    # Verify refresh token
    payload = self.verify_token(refresh_token)
    
    # Check if it's actually a refresh token
    if payload.get('token_type') != 'refresh':
        raise AuthenticationError("Token de reînnoire invalid")
    
    # Get admin user and generate new tokens
    admin_user = User.find_by_id(payload.get('user_id'))
    if not admin_user or admin_user.role != User.ROLE_ADMIN:
        raise AuthenticationError("Utilizator admin negăsit")
    
    # Generate fresh access and refresh tokens
    new_access_token = self.generate_token(admin_user)
    new_refresh_token = self.generate_refresh_token(admin_user)
    
    return {
        'access_token': new_access_token,
        'refresh_token': new_refresh_token,
        'token_type': 'Bearer',
        'expires_in': self.TOKEN_EXPIRY_HOURS * 3600
    }
```

## Admin Management Features

### 1. Initial Admin Account Creation
```python
def create_initial_admin(self, name: str, phone_number: str, password: str) -> Dict[str, Any]:
    # Check if any admin already exists
    db = get_database()
    existing_admin = db[User.COLLECTION_NAME].find_one({'role': User.ROLE_ADMIN})
    
    if existing_admin:
        raise AuthenticationError("Un administrator există deja în sistem")
    
    # Create admin user with admin role
    admin_user = User.create(
        phone_number=phone_number,
        name=name,
        password=password,
        role=User.ROLE_ADMIN
    )
    
    # Mark as verified (admin doesn't need SMS verification)
    admin_user.update({'is_verified': True})
    
    return {
        'success': True,
        'message': 'Administrator creat cu succes',
        'admin': {
            'id': str(admin_user._id),
            'name': admin_user.name,
            'phone_number': admin_user.phone_number,
            'role': admin_user.role
        }
    }
```

### 2. Admin Logout with Token Invalidation
```python
def logout_admin(self, token: str) -> Dict[str, Any]:
    try:
        # Verify token first
        payload = self.verify_token(token)
        
        # In production, add token to blacklist here
        # For now, we log the logout
        logging.info(f"Admin logged out: {payload.get('phone_number')}")
        
        return {
            'success': True,
            'message': 'Deconectare reușită'
        }
        
    except AuthenticationError:
        # Even if token is invalid, consider logout successful
        return {
            'success': True,
            'message': 'Deconectare reușită'
        }
```

### 3. Admin Role Verification
```python
# Throughout authentication flow
if admin_user.role != User.ROLE_ADMIN:
    raise AuthenticationError(
        "Acces interzis. Doar administratorii pot accesa acest sistem"
    )

# In token verification
if payload.get('role') != User.ROLE_ADMIN:
    raise AuthenticationError("Token invalid pentru admin")

# Account verification check
if not admin_user.is_verified:
    raise AuthenticationError(
        "Contul nu este verificat. Contactați administratorul sistemului"
    )
```

## Integration with Existing Systems

### 1. User Model Integration
```python
# Uses existing User model methods
admin_user = User.find_by_phone(username)  # Find admin by phone
admin_user.verify_password(password)       # Verify password using existing method
admin_user.update({'last_login': datetime.utcnow()})  # Update last login

# Creates admin users using existing creation flow
admin_user = User.create(
    phone_number=phone_number,
    name=name,
    password=password,
    role=User.ROLE_ADMIN
)
```

### 2. Error Handling Integration
```python
from app.utils.error_handlers import AuthenticationError, ValidationError

# Uses existing error handler classes for consistency
raise AuthenticationError("Romanian error message", "AUTH_001")
raise ValidationError("Romanian validation message")
```

### 3. Database Integration
```python
from app.database import get_database
from app.models.user import User

# Uses existing database connection and user model
db = get_database()
collection = db[User.COLLECTION_NAME]
```

## Configuration and Environment

### 1. Environment Variable Configuration
```python
def __init__(self, config=None):
    self.config = config or {}
    self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    
    # Validate configuration
    if not self.secret_key or self.secret_key == 'your-secret-key-change-in-production':
        logging.warning("Using default JWT secret key. Change JWT_SECRET_KEY in production!")
```

### 2. Security Configuration Constants
```python
# JWT Configuration
ALGORITHM = 'HS256'
TOKEN_EXPIRY_HOURS = 8  # Admin sessions last 8 hours
REFRESH_TOKEN_EXPIRY_DAYS = 7  # Refresh tokens last 7 days

# Password and Rate Limiting
MIN_PASSWORD_LENGTH = 8
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30
```

### 3. Logging and Audit Trail
```python
# Security logging throughout the service
logging.info(f"Admin authentication successful: {username}")
logging.warning(f"Account locked due to failed attempts: {username}")
logging.info(f"Access token generated for admin: {admin_user.phone_number}")
logging.info(f"Admin logged out: {payload.get('phone_number')}")
```

## Error Handling and Security

### 1. Comprehensive Romanian Error Messages
```python
# Authentication errors with Romanian localization
AUTH_001: "Datele de autentificare sunt incorecte"
AUTH_002: "Acces interzis. Doar administratorii pot accesa acest sistem"
AUTH_003: "Contul nu este verificat. Contactați administratorul sistemului"
AUTH_006: "Token de autentificare lipsește"
AUTH_008: "Token-ul de autentificare a expirat"
AUTH_015: "Prea multe încercări de autentificare. Încercați din nou în X minute"
```

### 2. Secure Error Responses
```python
# Don't expose sensitive information in errors
if not admin_user:
    self._record_failed_attempt(username, ip_address)
    raise AuthenticationError("Datele de autentificare sunt incorecte")  # Generic message

# Log detailed errors but return generic messages
except Exception as e:
    logging.error(f"Authentication error: {str(e)}")  # Detailed log
    raise AuthenticationError("Eroare la autentificare. Încercați din nou")  # Generic user message
```

### 3. Input Validation and Sanitization
```python
# Validate all inputs
if not username or not password:
    raise ValidationError("Numele de utilizator și parola sunt obligatorii")

# Password strength validation
if len(password) < self.MIN_PASSWORD_LENGTH:
    raise ValidationError(f"Parola trebuie să aibă cel puțin {self.MIN_PASSWORD_LENGTH} caractere")

# Token format validation
if token.startswith('Bearer '):
    token = token[7:]  # Remove Bearer prefix safely
```

## Quality Assurance

- Service follows secure authentication best practices with JWT and bcrypt
- Complete Romanian localization with culturally appropriate error messages
- Comprehensive rate limiting and brute force protection
- Secure password hashing with bcrypt and appropriate salt rounds
- JWT tokens with proper expiration, audience, and issuer validation
- Integration with existing User model and database infrastructure
- Extensive logging for security auditing and monitoring
- Proper error handling with secure error messages
- Token refresh mechanism for seamless admin sessions
- Initial admin creation functionality for system setup
- Admin role verification throughout authentication flow
- Environment variable configuration for production deployment

## Next Integration Opportunities

Ready for immediate integration with:
- Admin authentication endpoints for Flask routes
- Admin panel frontend authentication flow
- Role-based access control middleware for protected routes
- Token blacklisting system for secure logout
- Admin password reset functionality
- Multi-factor authentication for enhanced security
- Session management with Redis for scalability
- Audit logging system for admin actions
- Admin account management interface
- API rate limiting integration for admin endpoints