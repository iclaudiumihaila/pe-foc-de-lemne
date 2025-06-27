# Production Setup Guide for Pe Foc de Lemne

## Database Setup

The production MongoDB URI has been configured. To set up the production database:

### 1. Install Python dependencies (if not already installed):
```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the setup script to create admin user and indexes:
```bash
cd backend
python setup_production_db.py \
  --admin-phone "+40712345678" \
  --admin-password "your-secure-password" \
  --admin-name "Administrator"
```

Replace the phone number and password with your desired admin credentials.

## Environment Variables for Railway

Set these environment variables in your Railway project:

### Backend Service:
```
MONGO_URI=mongodb://mongo:wHkJtfTKOIDKtkzSxcOIjhCZpbeUPmkF@shuttle.proxy.rlwy.net:58855
JWT_SECRET_KEY=<generate-a-secure-random-string>
SECRET_KEY=<generate-another-secure-random-string>
FLASK_ENV=production
CORS_ORIGINS=https://your-frontend-app.up.railway.app
PORT=8000
```

### Frontend Service:
```
REACT_APP_API_URL=https://your-backend-app.up.railway.app/api
NODE_ENV=production
```

## Generate Secure Keys

To generate secure random keys for JWT_SECRET_KEY and SECRET_KEY:

```python
import secrets
print(secrets.token_urlsafe(32))
```

## Important Notes

1. **Change the default secrets**: The JWT_SECRET_KEY and SECRET_KEY must be changed from the defaults in production.

2. **Update CORS origins**: Replace `your-frontend-app.up.railway.app` with your actual Railway frontend URL.

3. **Database is already configured**: The MongoDB connection string is already set up and ready to use.

4. **Admin credentials**: Store the admin phone and password securely. You'll need these to log into the admin panel.

5. **SMS Configuration**: If you plan to use SMS verification, you'll need to set up Twilio credentials:
   - TWILIO_ACCOUNT_SID
   - TWILIO_AUTH_TOKEN
   - TWILIO_PHONE_NUMBER

## Verification

After setup, verify everything works:

1. Admin login: Try logging in with the admin credentials at `/admin/login`
2. Check categories: Verify categories are created at `/api/categories`
3. Test product creation: Create a test product through the admin panel

## Security Checklist

- [ ] Changed JWT_SECRET_KEY from default
- [ ] Changed SECRET_KEY from default
- [ ] Set strong admin password
- [ ] Updated CORS_ORIGINS to match your frontend URL
- [ ] Enabled HTTPS on Railway (automatic)
- [ ] Reviewed environment variables for sensitive data