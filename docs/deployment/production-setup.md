# Production Deployment Guide - Pe Foc de Lemne

> **Complete Production Environment Setup for Romanian Local Producer Marketplace**

This comprehensive guide covers the complete production deployment of the Pe Foc de Lemne marketplace, including server setup, security hardening, and Romanian compliance requirements.

## 📋 Prerequisites

### Infrastructure Requirements
- **Server**: Ubuntu 20.04+ LTS (minimum 4GB RAM, 2 CPU cores, 40GB SSD)
- **Domain**: Registered domain with SSL certificate capability
- **Database**: MongoDB Atlas (recommended) or self-hosted MongoDB
- **SMS Service**: Twilio account for Romanian SMS verification
- **Email**: SMTP service for notifications
- **CDN**: CloudFlare or similar (optional but recommended)

### Romanian Compliance Requirements
- **GDPR Compliance**: Data protection officer designation
- **Romanian Privacy Law**: Local data protection compliance
- **Tax Registration**: Romanian VAT registration if applicable
- **Business License**: Romanian marketplace operating license

## 🏗️ Server Setup and Configuration

### 1. Initial Server Setup
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y \
    nginx \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    git \
    curl \
    wget \
    unzip \
    fail2ban \
    ufw \
    certbot \
    python3-certbot-nginx

# Install MongoDB tools (if using external MongoDB)
wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list
sudo apt update
sudo apt install -y mongodb-mongosh mongodb-tools
```

### 2. Security Hardening
```bash
# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Configure fail2ban for SSH protection
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Disable root login and password authentication
sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart ssh

# Set up automatic security updates
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 3. Application User Setup
```bash
# Create application user
sudo useradd -m -s /bin/bash pefocdelemne
sudo usermod -aG sudo pefocdelemne

# Set up SSH key access for deployment
sudo mkdir -p /home/pefocdelemne/.ssh
sudo chmod 700 /home/pefocdelemne/.ssh
# Copy your public key to /home/pefocdelemne/.ssh/authorized_keys
sudo chown -R pefocdelemne:pefocdelemne /home/pefocdelemne/.ssh
sudo chmod 600 /home/pefocdelemne/.ssh/authorized_keys
```

## 🚀 Application Deployment

### 1. Code Deployment
```bash
# Switch to application user
sudo su - pefocdelemne

# Clone repository
git clone https://github.com/yourusername/pe-foc-de-lemne.git
cd pe-foc-de-lemne

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# Install Node.js dependencies and build frontend
cd frontend
npm install
npm run build
cd ..
```

### 2. Environment Configuration
```bash
# Backend environment variables
cat > /home/pefocdelemne/pe-foc-de-lemne/backend/.env << 'EOF'
# Application Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-super-secure-secret-key-here

# Database Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/pe_foc_de_lemne_prod?retryWrites=true&w=majority

# Twilio SMS Configuration
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-romanian-number

# JWT and Security
JWT_SECRET_KEY=your-jwt-secret-key
ENCRYPTION_MASTER_KEY=your-encryption-master-key-32-chars

# Security Configuration
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECURITY_PASSWORD_SALT=your-password-salt

# Email Configuration (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@yourdomain.com

# Analytics (optional)
GA4_MEASUREMENT_ID=G-XXXXXXXXXX

# Romanian Compliance
GDPR_CONTACT_EMAIL=privacy@yourdomain.com
BUSINESS_ADDRESS=Your Business Address, Romania
VAT_NUMBER=RO12345678
EOF

# Frontend environment variables
cat > /home/pefocdelemne/pe-foc-de-lemne/frontend/.env.production.local << 'EOF'
# API Configuration
REACT_APP_API_URL=https://yourdomain.com/api

# Analytics
REACT_APP_GA4_MEASUREMENT_ID=G-XXXXXXXXXX

# Application Configuration
REACT_APP_ENV=production
REACT_APP_VERSION=1.0.0

# Romanian Configuration
REACT_APP_LOCALE=ro-RO
REACT_APP_CURRENCY=RON
REACT_APP_COUNTRY=RO

# Business Information
REACT_APP_BUSINESS_NAME=Pe Foc de Lemne
REACT_APP_BUSINESS_EMAIL=contact@yourdomain.com
REACT_APP_BUSINESS_PHONE=+40XXX XXX XXX
EOF

# Secure environment files
chmod 600 /home/pefocdelemne/pe-foc-de-lemne/backend/.env
chmod 600 /home/pefocdelemne/pe-foc-de-lemne/frontend/.env.production.local
```

### 3. Database Setup
```bash
# If using MongoDB Atlas (recommended)
# 1. Create cluster at https://cloud.mongodb.com
# 2. Configure network access for your server IP
# 3. Create database user with readWrite permissions
# 4. Update MONGODB_URI in .env file

# If using local MongoDB (not recommended for production)
sudo apt install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod

# Create database and user
mongosh --eval "
use pe_foc_de_lemne_prod;
db.createUser({
  user: 'pe_foc_de_lemne_user',
  pwd: 'secure_database_password',
  roles: ['readWrite']
});
"

# Create indexes for performance
cd /home/pefocdelemne/pe-foc-de-lemne/backend
python3 -c "
from app.database import create_indexes
create_indexes()
"
```

## 🔧 Process Management with PM2

### 1. Install and Configure PM2
```bash
# Install PM2 globally
sudo npm install -g pm2

# Create PM2 ecosystem configuration
cat > /home/pefocdelemne/pe-foc-de-lemne/ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'pe-foc-de-lemne-backend',
    script: '/home/pefocdelemne/pe-foc-de-lemne/venv/bin/python',
    args: 'app.py',
    cwd: '/home/pefocdelemne/pe-foc-de-lemne/backend',
    instances: 'max',
    exec_mode: 'cluster',
    env: {
      FLASK_ENV: 'production',
      PORT: 8080,
      PYTHONPATH: '/home/pefocdelemne/pe-foc-de-lemne/backend'
    },
    env_production: {
      NODE_ENV: 'production'
    },
    error_file: '/var/log/pe-foc-de-lemne/backend-error.log',
    out_file: '/var/log/pe-foc-de-lemne/backend-out.log',
    log_file: '/var/log/pe-foc-de-lemne/backend.log',
    time: true,
    max_memory_restart: '1G',
    node_args: '--max-old-space-size=1024'
  }]
};
EOF
```

### 2. Setup Logging
```bash
# Create log directories
sudo mkdir -p /var/log/pe-foc-de-lemne
sudo chown pefocdelemne:pefocdelemne /var/log/pe-foc-de-lemne

# Configure log rotation
sudo cat > /etc/logrotate.d/pe-foc-de-lemne << 'EOF'
/var/log/pe-foc-de-lemne/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    sharedscripts
    postrotate
        /usr/bin/pm2 reloadLogs
    endscript
}
EOF
```

### 3. Start Application
```bash
# Start application with PM2
cd /home/pefocdelemne/pe-foc-de-lemne
pm2 start ecosystem.config.js --env production

# Configure PM2 to start on boot
pm2 startup
# Follow the instructions to run the generated command as root

# Save PM2 configuration
pm2 save
```

## 🌐 Nginx Configuration

### 1. SSL Certificate Setup
```bash
# Obtain SSL certificate from Let's Encrypt
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Verify certificate auto-renewal
sudo certbot renew --dry-run

# Set up automatic renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### 2. Nginx Site Configuration
```bash
# Create Nginx configuration
sudo cat > /etc/nginx/sites-available/pe-foc-de-lemne << 'EOF'
# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=general:10m rate=30r/s;

# Upstream backend
upstream backend {
    least_conn;
    server 127.0.0.1:8080 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirect all other HTTP requests to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# Main HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # HSTS (optional but recommended)
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    
    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
    
    # Content Security Policy for Romanian marketplace
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://www.google-analytics.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://www.google-analytics.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self';" always;
    
    # Document root for React build
    root /home/pefocdelemne/pe-foc-de-lemne/frontend/build;
    index index.html;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json
        application/xml
        image/svg+xml;
    
    # Brotli compression (if module available)
    # brotli on;
    # brotli_comp_level 6;
    # brotli_types text/xml image/svg+xml application/x-font-ttf image/vnd.microsoft.icon application/x-font-opentype application/json font/eot application/vnd.ms-fontobject application/javascript font/otf application/xml application/xhtml+xml text/javascript application/x-javascript text/plain application/x-font-truetype application/xml+rss image/x-icon font/opentype text/css image/x-win-bitmap;
    
    # API routes with rate limiting
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        # Buffer sizes
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }
    
    # Static assets with far-future expiry
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Vary "Accept-Encoding";
    }
    
    # Media files
    location /media/ {
        expires 1M;
        add_header Cache-Control "public";
        add_header Vary "Accept-Encoding";
    }
    
    # Favicon and robots
    location = /favicon.ico {
        expires 1M;
        add_header Cache-Control "public";
        log_not_found off;
    }
    
    location = /robots.txt {
        expires 1d;
        add_header Cache-Control "public";
        log_not_found off;
    }
    
    # React app - handle client-side routing
    location / {
        limit_req zone=general burst=50 nodelay;
        
        try_files $uri $uri/ /index.html;
        
        # Cache for HTML files
        location ~* \.html$ {
            expires 1h;
            add_header Cache-Control "public, must-revalidate";
        }
        
        # Cache for assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Block access to sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    location ~ ~$ {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    # Romanian marketplace specific redirects
    location = /politica-confidentialitate {
        return 301 https://$server_name/confidentialitate;
    }
    
    location = /termeni-conditii {
        return 301 https://$server_name/termeni;
    }
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/pe-foc-de-lemne /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## 📊 Monitoring and Health Checks

### 1. Application Monitoring
```bash
# Create health check script
cat > /home/pefocdelemne/health-check.sh << 'EOF'
#!/bin/bash

# Health check for Pe Foc de Lemne application
LOG_FILE="/var/log/pe-foc-de-lemne/health-check.log"
API_URL="https://yourdomain.com/api/health"
EMAIL_ALERT="admin@yourdomain.com"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Check API health
if curl -f -s --max-time 10 "$API_URL" > /dev/null; then
    log_message "API health check: OK"
else
    log_message "API health check: FAILED"
    echo "Pe Foc de Lemne API is down!" | mail -s "ALERT: API Down" "$EMAIL_ALERT"
    pm2 restart pe-foc-de-lemne-backend
    log_message "Attempted to restart backend service"
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    log_message "Disk usage warning: ${DISK_USAGE}%"
    echo "Disk usage is at ${DISK_USAGE}%" | mail -s "WARNING: High Disk Usage" "$EMAIL_ALERT"
fi

# Check memory usage
MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ "$MEM_USAGE" -gt 90 ]; then
    log_message "Memory usage warning: ${MEM_USAGE}%"
    echo "Memory usage is at ${MEM_USAGE}%" | mail -s "WARNING: High Memory Usage" "$EMAIL_ALERT"
fi

# Check PM2 processes
PM2_STATUS=$(pm2 jlist | jq -r '.[] | select(.name=="pe-foc-de-lemne-backend") | .pm2_env.status')
if [ "$PM2_STATUS" != "online" ]; then
    log_message "PM2 process status: $PM2_STATUS"
    echo "PM2 process is not online: $PM2_STATUS" | mail -s "ALERT: PM2 Process Down" "$EMAIL_ALERT"
    pm2 restart pe-foc-de-lemne-backend
fi
EOF

chmod +x /home/pefocdelemne/health-check.sh

# Schedule health checks every 5 minutes
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/pefocdelemne/health-check.sh") | crontab -
```

### 2. Log Management
```bash
# Configure rsyslog for application logs
sudo cat > /etc/rsyslog.d/50-pe-foc-de-lemne.conf << 'EOF'
# Pe Foc de Lemne application logs
if $programname startswith 'pe-foc-de-lemne' then /var/log/pe-foc-de-lemne/application.log
& stop
EOF

sudo systemctl restart rsyslog
```

### 3. Performance Monitoring
```bash
# Install htop for system monitoring
sudo apt install -y htop iotop nethogs

# Create system stats script
cat > /home/pefocdelemne/system-stats.sh << 'EOF'
#!/bin/bash

# System statistics for Pe Foc de Lemne
DATE=$(date '+%Y-%m-%d %H:%M:%S')
STATS_FILE="/var/log/pe-foc-de-lemne/system-stats.log"

# CPU usage
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')

# Memory usage
MEM_TOTAL=$(free -m | awk 'NR==2{print $2}')
MEM_USED=$(free -m | awk 'NR==2{print $3}')
MEM_PERCENTAGE=$(echo "scale=2; $MEM_USED*100/$MEM_TOTAL" | bc)

# Disk usage
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}')

# Network connections
CONNECTIONS=$(netstat -an | grep :443 | wc -l)

# Log stats
echo "$DATE,CPU:$CPU_USAGE%,MEM:$MEM_PERCENTAGE%,DISK:$DISK_USAGE,CONN:$CONNECTIONS" >> "$STATS_FILE"
EOF

chmod +x /home/pefocdelemne/system-stats.sh

# Schedule system stats collection every 10 minutes
(crontab -l 2>/dev/null; echo "*/10 * * * * /home/pefocdelemne/system-stats.sh") | crontab -
```

## 🔒 Security and Compliance

### 1. Romanian GDPR Compliance Setup
```bash
# Create GDPR compliance directory
mkdir -p /home/pefocdelemne/gdpr-compliance

# Data retention policy script
cat > /home/pefocdelemne/gdpr-compliance/data-retention.py << 'EOF'
#!/usr/bin/env python3
"""
GDPR Data Retention Policy Enforcement
Automatically removes old data according to Romanian privacy laws
"""

import os
import sys
from datetime import datetime, timedelta
from pymongo import MongoClient

# Add the backend directory to Python path
sys.path.append('/home/pefocdelemne/pe-foc-de-lemne/backend')

from app.config import Config

def cleanup_old_data():
    """Remove data older than retention period"""
    client = MongoClient(Config.MONGODB_URI)
    db = client.get_database()
    
    # 2 years retention for orders (Romanian requirement)
    two_years_ago = datetime.utcnow() - timedelta(days=730)
    
    # Remove old analytics events (1 year retention)
    one_year_ago = datetime.utcnow() - timedelta(days=365)
    result = db.analytics_events.delete_many({
        'timestamp': {'$lt': one_year_ago}
    })
    print(f"Removed {result.deleted_count} old analytics events")
    
    # Anonymize old orders (keep for tax purposes but remove PII)
    orders_to_anonymize = db.orders.find({
        'created_at': {'$lt': two_years_ago},
        'anonymized': {'$ne': True}
    })
    
    for order in orders_to_anonymize:
        db.orders.update_one(
            {'_id': order['_id']},
            {
                '$set': {
                    'customer_info.name': 'ANONYMIZED',
                    'customer_info.email': 'anonymized@example.com',
                    'customer_info.phone': '+40XXXXXXXXX',
                    'customer_info.address': 'ANONYMIZED',
                    'anonymized': True,
                    'anonymized_at': datetime.utcnow()
                }
            }
        )
    
    print(f"Anonymized {orders_to_anonymize.count()} old orders")
    
    # Remove old SMS verification sessions (24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    result = db.sms_sessions.delete_many({
        'created_at': {'$lt': yesterday}
    })
    print(f"Removed {result.deleted_count} old SMS sessions")

if __name__ == "__main__":
    cleanup_old_data()
EOF

chmod +x /home/pefocdelemne/gdpr-compliance/data-retention.py

# Schedule GDPR compliance cleanup daily at 2 AM
(crontab -l 2>/dev/null; echo "0 2 * * * /home/pefocdelemne/gdpr-compliance/data-retention.py >> /var/log/pe-foc-de-lemne/gdpr-compliance.log 2>&1") | crontab -
```

### 2. Backup Strategy
```bash
# Create backup script for Romanian compliance
cat > /home/pefocdelemne/backup-script.sh << 'EOF'
#!/bin/bash

# Backup script for Pe Foc de Lemne
# Compliant with Romanian data protection requirements

BACKUP_DIR="/home/pefocdelemne/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p "$BACKUP_DIR/database" "$BACKUP_DIR/application" "$BACKUP_DIR/logs"

# Database backup (encrypted)
echo "Starting database backup..."
mongodump --uri="$MONGODB_URI" --out="$BACKUP_DIR/database/mongo_$DATE" --gzip

# Encrypt database backup
tar -czf "$BACKUP_DIR/database/mongo_$DATE.tar.gz" -C "$BACKUP_DIR/database" "mongo_$DATE"
gpg --cipher-algo AES256 --compress-algo 1 --s2k-cipher-algo AES256 --s2k-digest-algo SHA512 --s2k-mode 3 --s2k-count 65011712 --symmetric --output "$BACKUP_DIR/database/mongo_$DATE.tar.gz.gpg" "$BACKUP_DIR/database/mongo_$DATE.tar.gz"

# Remove unencrypted backup
rm -rf "$BACKUP_DIR/database/mongo_$DATE" "$BACKUP_DIR/database/mongo_$DATE.tar.gz"

# Application code backup
echo "Starting application backup..."
tar -czf "$BACKUP_DIR/application/app_$DATE.tar.gz" -C /home/pefocdelemne pe-foc-de-lemne --exclude=node_modules --exclude=venv --exclude=.git

# Logs backup
echo "Starting logs backup..."
tar -czf "$BACKUP_DIR/logs/logs_$DATE.tar.gz" -C /var/log pe-foc-de-lemne

# Remove old backups (GDPR compliance - only keep what's necessary)
find "$BACKUP_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.gpg" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $DATE"
EOF

chmod +x /home/pefocdelemne/backup-script.sh

# Schedule daily backups at 3 AM
(crontab -l 2>/dev/null; echo "0 3 * * * /home/pefocdelemne/backup-script.sh >> /var/log/pe-foc-de-lemne/backup.log 2>&1") | crontab -
```

## 🚀 Deployment Scripts

### 1. Deployment Automation
```bash
# Create deployment script
cat > /home/pefocdelemne/deploy.sh << 'EOF'
#!/bin/bash

# Pe Foc de Lemne deployment script
set -e

APP_DIR="/home/pefocdelemne/pe-foc-de-lemne"
BACKUP_DIR="/home/pefocdelemne/deployment-backups"
DATE=$(date +%Y%m%d_%H%M%S)

echo "Starting deployment: $DATE"

# Create backup of current version
mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_DIR/pre-deploy-$DATE.tar.gz" -C /home/pefocdelemne pe-foc-de-lemne --exclude=node_modules --exclude=venv

# Navigate to application directory
cd "$APP_DIR"

# Pull latest changes
echo "Pulling latest changes..."
git fetch origin
git reset --hard origin/main

# Backend updates
echo "Updating backend..."
source venv/bin/activate
pip install -r backend/requirements.txt

# Frontend updates
echo "Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Database migrations (if any)
echo "Running database migrations..."
cd backend
python3 -c "from app.database import run_migrations; run_migrations()" || echo "No migrations to run"
cd ..

# Restart services
echo "Restarting services..."
pm2 restart pe-foc-de-lemne-backend

# Health check
echo "Performing health check..."
sleep 10
if curl -f -s --max-time 10 "https://yourdomain.com/api/health" > /dev/null; then
    echo "✅ Deployment successful!"
    
    # Remove old deployment backups (keep last 5)
    ls -t "$BACKUP_DIR"/pre-deploy-*.tar.gz | tail -n +6 | xargs -r rm
else
    echo "❌ Health check failed! Rolling back..."
    # Rollback logic here
    tar -xzf "$BACKUP_DIR/pre-deploy-$DATE.tar.gz" -C /home/pefocdelemne
    pm2 restart pe-foc-de-lemne-backend
    echo "Rollback completed"
    exit 1
fi

echo "Deployment completed: $DATE"
EOF

chmod +x /home/pefocdelemne/deploy.sh
```

### 2. Environment Update Script
```bash
# Create environment update script
cat > /home/pefocdelemne/update-env.sh << 'EOF'
#!/bin/bash

# Update environment variables for Pe Foc de Lemne
# Usage: ./update-env.sh KEY VALUE

if [ $# -ne 2 ]; then
    echo "Usage: $0 KEY VALUE"
    exit 1
fi

KEY=$1
VALUE=$2
ENV_FILE="/home/pefocdelemne/pe-foc-de-lemne/backend/.env"

# Backup current .env
cp "$ENV_FILE" "$ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"

# Update or add the key-value pair
if grep -q "^$KEY=" "$ENV_FILE"; then
    # Key exists, update it
    sed -i "s/^$KEY=.*/$KEY=$VALUE/" "$ENV_FILE"
    echo "Updated $KEY in $ENV_FILE"
else
    # Key doesn't exist, add it
    echo "$KEY=$VALUE" >> "$ENV_FILE"
    echo "Added $KEY to $ENV_FILE"
fi

# Restart application to apply changes
pm2 restart pe-foc-de-lemne-backend
echo "Application restarted"
EOF

chmod +x /home/pefocdelemne/update-env.sh
```

## 📈 Performance Optimization

### 1. Database Optimization
```bash
# MongoDB optimization script
cat > /home/pefocdelemne/optimize-db.py << 'EOF'
#!/usr/bin/env python3
"""
Database optimization for Pe Foc de Lemne
Romanian marketplace performance tuning
"""

import sys
sys.path.append('/home/pefocdelemne/pe-foc-de-lemne/backend')

from pymongo import MongoClient
from app.config import Config

def optimize_database():
    """Optimize MongoDB for Romanian marketplace"""
    client = MongoClient(Config.MONGODB_URI)
    db = client.get_database()
    
    # Create indexes for performance
    print("Creating performance indexes...")
    
    # Products indexes
    db.products.create_index([("category", 1), ("status", 1)])
    db.products.create_index([("producer", 1), ("status", 1)])
    db.products.create_index([("name", "text"), ("description", "text")])
    db.products.create_index([("price", 1)])
    db.products.create_index([("created_at", -1)])
    
    # Orders indexes
    db.orders.create_index([("order_number", 1)], unique=True)
    db.orders.create_index([("customer_info.phone", 1)])
    db.orders.create_index([("status", 1)])
    db.orders.create_index([("created_at", -1)])
    
    # Cart indexes
    db.cart_sessions.create_index([("session_id", 1)], unique=True)
    db.cart_sessions.create_index([("created_at", 1)], expireAfterSeconds=7200)  # 2 hours
    
    # SMS sessions indexes
    db.sms_sessions.create_index([("session_id", 1)], unique=True)
    db.sms_sessions.create_index([("phone_number", 1)])
    db.sms_sessions.create_index([("created_at", 1)], expireAfterSeconds=3600)  # 1 hour
    
    # Analytics indexes
    db.analytics_events.create_index([("timestamp", -1)])
    db.analytics_events.create_index([("event_type", 1), ("timestamp", -1)])
    db.analytics_events.create_index([("user_session", 1)])
    
    # Categories indexes
    db.categories.create_index([("name", 1), ("status", 1)])
    
    print("Database optimization completed!")

if __name__ == "__main__":
    optimize_database()
EOF

chmod +x /home/pefocdelemne/optimize-db.py
python3 /home/pefocdelemne/optimize-db.py
```

### 2. Nginx Performance Tuning
```bash
# Update Nginx configuration for better performance
sudo cat > /etc/nginx/nginx.conf << 'EOF'
user www-data;
worker_processes auto;
worker_rlimit_nofile 65535;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 30;
    keepalive_requests 100;
    types_hash_max_size 2048;
    server_tokens off;
    client_max_body_size 20M;
    
    # Buffer sizes
    client_body_buffer_size 128k;
    client_header_buffer_size 3m;
    large_client_header_buffers 4 256k;
    
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_min_length 1000;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json
        application/xml
        image/svg+xml;
    
    # Open file cache
    open_file_cache max=1000 inactive=20s;
    open_file_cache_valid 30s;
    open_file_cache_min_uses 2;
    open_file_cache_errors on;
    
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
EOF

sudo nginx -t && sudo systemctl reload nginx
```

## 🔍 Troubleshooting Guide

### Common Issues and Solutions

#### 1. Application Won't Start
```bash
# Check PM2 status
pm2 status

# Check application logs
pm2 logs pe-foc-de-lemne-backend

# Check environment variables
cat /home/pefocdelemne/pe-foc-de-lemne/backend/.env

# Restart application
pm2 restart pe-foc-de-lemne-backend
```

#### 2. Database Connection Issues
```bash
# Test MongoDB connection
mongosh "$MONGODB_URI" --eval "db.stats()"

# Check network connectivity
telnet your-mongodb-host 27017

# Verify credentials
echo $MONGODB_URI | sed 's/mongodb:\/\///' | cut -d@ -f1
```

#### 3. SSL Certificate Problems
```bash
# Check certificate status
sudo certbot certificates

# Test SSL configuration
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Renew certificate manually
sudo certbot renew --force-renewal -d yourdomain.com
```

#### 4. Performance Issues
```bash
# Check system resources
htop

# Monitor network connections
netstat -tulpn | grep :443

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Monitor PM2 processes
pm2 monit
```

---

**This completes the production deployment setup for Pe Foc de Lemne Romanian marketplace.**

**For support:** tech@yourdomain.com | **Documentation:** See [docs/](../) directory