# Pe Foc de Lemne - Production Deployment Guide

> **Quick Reference for Production Deployment**

This guide provides essential steps for deploying the Pe Foc de Lemne marketplace to production.

## 🎯 Quick Start Checklist

- [ ] Server with Ubuntu 20.04+ (minimum 2GB RAM, 2 CPU cores)
- [ ] Domain name configured with DNS
- [ ] SSL certificate (Let's Encrypt recommended)
- [ ] MongoDB instance (Atlas or self-hosted)
- [ ] Twilio account for SMS verification
- [ ] Google Analytics 4 property (optional)

## 🚀 Production Deployment Steps

### 1. Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y nginx python3 python3-pip nodejs npm mongodb-tools git

# Install PM2 for process management
sudo npm install -g pm2

# Create application user
sudo useradd -m -s /bin/bash pefocdelemne
sudo usermod -aG sudo pefocdelemne
```

### 2. Application Setup
```bash
# Switch to application user
sudo su - pefocdelemne

# Clone repository
git clone [your-repository-url] /home/pefocdelemne/pe-foc-de-lemne
cd /home/pefocdelemne/pe-foc-de-lemne

# Set up backend
cd backend
pip3 install -r requirements.txt

# Set up frontend
cd ../frontend
npm install
npm run build
```

### 3. Environment Configuration
```bash
# Backend environment
cat > /home/pefocdelemne/pe-foc-de-lemne/backend/.env << EOF
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-production-secret-key

# MongoDB (use MongoDB Atlas for production)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/pe_foc_de_lemne

# Twilio SMS
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-phone

# JWT and encryption
JWT_SECRET_KEY=your-jwt-secret
ENCRYPTION_MASTER_KEY=your-encryption-key

# Security
CORS_ORIGINS=https://yourdomain.com
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
EOF

# Frontend environment
cat > /home/pefocdelemne/pe-foc-de-lemne/frontend/.env.production << EOF
REACT_APP_API_URL=https://yourdomain.com/api
REACT_APP_GA4_MEASUREMENT_ID=your-ga4-id
REACT_APP_ENV=production
EOF
```

### 4. Process Management with PM2
```bash
# Backend PM2 configuration
cat > /home/pefocdelemne/pe-foc-de-lemne/ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'pe-foc-de-lemne-backend',
    script: 'python3',
    args: 'app.py',
    cwd: '/home/pefocdelemne/pe-foc-de-lemne/backend',
    instances: 2,
    exec_mode: 'cluster',
    env: {
      FLASK_ENV: 'production',
      PORT: 8080
    },
    error_file: '/var/log/pe-foc-de-lemne/backend-error.log',
    out_file: '/var/log/pe-foc-de-lemne/backend-out.log',
    log_file: '/var/log/pe-foc-de-lemne/backend.log'
  }]
};
EOF

# Create log directory
sudo mkdir -p /var/log/pe-foc-de-lemne
sudo chown pefocdelemne:pefocdelemne /var/log/pe-foc-de-lemne

# Start application
pm2 start ecosystem.config.js
pm2 startup
pm2 save
```

### 5. Nginx Configuration
```bash
# Create Nginx configuration
sudo cat > /etc/nginx/sites-available/pe-foc-de-lemne << EOF
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Serve React frontend
    root /home/pefocdelemne/pe-foc-de-lemne/frontend/build;
    index index.html;
    
    # API proxy
    location /api {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
    
    # Static files with caching
    location /static {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # React routing
    location / {
        try_files \$uri \$uri/ /index.html;
    }
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/pe-foc-de-lemne /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. SSL Certificate with Let's Encrypt
```bash
# Install Certbot
sudo apt install snapd
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot

# Create certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Verify auto-renewal
sudo certbot renew --dry-run
```

### 7. MongoDB Setup (if self-hosting)
```bash
# Install MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list
sudo apt update
sudo apt install -y mongodb-org

# Configure MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Create database user
mongo pe_foc_de_lemne --eval "
db.createUser({
  user: 'pe_foc_de_lemne_user',
  pwd: 'secure_password',
  roles: ['readWrite']
})
"
```

## 🔒 Security Checklist

### Server Security
- [ ] SSH key authentication enabled
- [ ] Password authentication disabled
- [ ] Firewall configured (UFW)
- [ ] Fail2ban installed and configured
- [ ] Regular security updates enabled

### Application Security
- [ ] Environment variables secured
- [ ] Database credentials encrypted
- [ ] HTTPS enforced everywhere
- [ ] Security headers configured
- [ ] Rate limiting enabled

### Monitoring Setup
- [ ] Log rotation configured
- [ ] System monitoring (CPU, memory, disk)
- [ ] Application monitoring (uptime, errors)
- [ ] SSL certificate expiry monitoring

## 📊 Monitoring and Maintenance

### System Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Set up log rotation
sudo cat > /etc/logrotate.d/pe-foc-de-lemne << EOF
/var/log/pe-foc-de-lemne/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    sharedscripts
    postrotate
        pm2 reloadLogs
    endscript
}
EOF
```

### Application Monitoring
```bash
# PM2 monitoring commands
pm2 status                    # Check application status
pm2 logs                      # View application logs
pm2 monit                     # Real-time monitoring
pm2 restart pe-foc-de-lemne-backend  # Restart application
```

### Database Backup
```bash
# Create backup script
cat > /home/pefocdelemne/backup_db.sh << EOF
#!/bin/bash
DATE=\$(date +%Y%m%d_%H%M%S)
mongodump --uri="mongodb+srv://username:password@cluster.mongodb.net/pe_foc_de_lemne" --out="/home/pefocdelemne/backups/db_\$DATE"
find /home/pefocdelemne/backups -name "db_*" -mtime +7 -exec rm -rf {} \;
EOF

chmod +x /home/pefocdelemne/backup_db.sh

# Schedule daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /home/pefocdelemne/backup_db.sh") | crontab -
```

## 🔧 Common Issues and Solutions

### Application Won't Start
```bash
# Check PM2 logs
pm2 logs pe-foc-de-lemne-backend

# Check environment variables
cat /home/pefocdelemne/pe-foc-de-lemne/backend/.env

# Restart application
pm2 restart pe-foc-de-lemne-backend
```

### Database Connection Issues
```bash
# Test MongoDB connection
mongo "mongodb+srv://username:password@cluster.mongodb.net/pe_foc_de_lemne" --eval "db.stats()"

# Check network connectivity
telnet cluster.mongodb.net 27017
```

### SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate manually
sudo certbot renew

# Test SSL configuration
openssl s_client -connect yourdomain.com:443
```

## 📞 Support and Troubleshooting

### Log Locations
- **Application logs**: `/var/log/pe-foc-de-lemne/`
- **Nginx logs**: `/var/log/nginx/`
- **System logs**: `/var/log/syslog`
- **PM2 logs**: `~/.pm2/logs/`

### Performance Optimization
- Monitor server resources with `htop`
- Check database performance with MongoDB profiler
- Optimize Nginx caching and compression
- Scale horizontally by adding more PM2 instances

### Updates and Maintenance
```bash
# Update application code
cd /home/pefocdelemne/pe-foc-de-lemne
git pull origin main
cd frontend && npm run build
pm2 restart pe-foc-de-lemne-backend
```

---

**For detailed documentation, see [docs/deployment/](docs/deployment/) directory.**

**Support**: tech@pefocdelemne.ro | **Documentation**: [docs.pefocdelemne.ro](docs.pefocdelemne.ro)