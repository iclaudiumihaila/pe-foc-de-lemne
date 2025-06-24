from flask import Blueprint

# Create admin blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Import and register admin routes
from .products import *
from .categories import *
from .orders import *
from .images import *