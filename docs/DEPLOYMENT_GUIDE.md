# CARPEM Oncocentre - Production Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the CARPEM Oncocentre application in a production environment. The application has been restructured and now features database-driven whitelist management for enhanced security and ease of administration.

## Prerequisites

### System Requirements
- Python 3.8 or higher
- SQLite 3 (included with Python)
- Web server (Apache/Nginx recommended)
- WSGI server (Gunicorn recommended)
- SSL certificate for HTTPS

### Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- Flask
- Flask-Login
- Flask-SQLAlchemy
- Flask-WTF
- WTForms
- bcrypt
- cryptography
- ldap3 (for LDAP authentication)

## 1. Initial Setup

### Clone and Setup Application
```bash
# Clone the repository
git clone <repository-url>
cd oncocentre

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Directory Structure Verification
Ensure the clean directory structure is in place:
```
oncocentre/
├── app/                 # Application package
├── templates/           # Jinja2 templates
├── static/             # Static assets
├── scripts/            # Utility scripts
├── tests/              # Test suite
├── docs/               # Documentation
├── instance/           # Instance data (SQLite DB)
├── run.py              # Entry point
└── encryption.key      # Encryption key (protect this!)
```

## 2. Database Initialization

### Create Database and Tables
```bash
# Initialize database with all tables
python -c "from app import create_app; app = create_app(); app.app_context().push(); from app.core.models import db; db.create_all()"
```

### Migrate Whitelist to Database
```bash
# Set environment variables
export AUTHORIZED_USERS="admin,doctor1,researcher1,nurse1"

# Run migration script
python scripts/migrate_whitelist.py
```

Expected output:
```
OK Database tables created/updated
OK Migrated 4 usernames from environment to database

Current whitelist status:
   Environment users: 4 (admin, doctor1, nurse1, researcher1)
   Database users: 4 (admin, doctor1, nurse1, researcher1)

OK Database whitelist is active and will be used for authentication
```

## 3. User Management

### Create Admin User
```bash
# Create initial admin user
python scripts/create_users.py
```

Follow the prompts to create:
- Admin user (can manage other users and whitelist)
- Regular users
- Principal investigators

### Verify User Setup
```bash
# Check all users in database
python scripts/check_users.py
```

## 4. Security Configuration

### Encryption Key Management
```bash
# Verify encryption key exists
ls -la encryption.key

# Secure the key file (Linux/Mac)
chmod 600 encryption.key
chown webapp:webapp encryption.key
```

### Environment Variables
Create `/etc/environment` or systemd environment file:
```bash
# Production environment variables
FLASK_ENV=production
AUTHORIZED_USERS="admin,doctor1,researcher1,nurse1"  # Fallback only

# Optional LDAP configuration
LDAP_SERVER="ldaps://ldap.institution.com"
LDAP_BASE_DN="dc=institution,dc=com"
LDAP_USER_DN="cn=users,dc=institution,dc=com"
LDAP_BIND_USER="service-account@institution.com"
LDAP_BIND_PASSWORD="secure-password"
```

### LDAP Configuration (Optional)
Create `config/.ldap_config.env`:
```bash
LDAP_SERVER=ldaps://ldap.institution.com
LDAP_BASE_DN=dc=institution,dc=com
LDAP_USER_DN=cn=users,dc=institution,dc=com
LDAP_BIND_USER=service-account@institution.com
LDAP_BIND_PASSWORD=secure-password
LDAP_USE_SSL=true
```

Secure the file:
```bash
chmod 600 config/.ldap_config.env
chown webapp:webapp config/.ldap_config.env
```

## 5. Web Server Configuration

### Gunicorn WSGI Server
Install and configure Gunicorn:
```bash
pip install gunicorn

# Create Gunicorn configuration
cat > gunicorn.conf.py << 'EOF'
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True
EOF
```

### Systemd Service
Create `/etc/systemd/system/oncocentre.service`:
```ini
[Unit]
Description=CARPEM Oncocentre Web Application
After=network.target

[Service]
Type=notify
User=webapp
Group=webapp
WorkingDirectory=/opt/oncocentre
Environment=PATH=/opt/oncocentre/venv/bin
Environment=FLASK_ENV=production
Environment=AUTHORIZED_USERS=admin,doctor1,researcher1,nurse1
ExecStart=/opt/oncocentre/venv/bin/gunicorn --config gunicorn.conf.py run:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable oncocentre
sudo systemctl start oncocentre
sudo systemctl status oncocentre
```

### Nginx Reverse Proxy
Configure Nginx (`/etc/nginx/sites-available/oncocentre`):
```nginx
server {
    listen 80;
    server_name oncocentre.institution.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name oncocentre.institution.com;

    ssl_certificate /path/to/ssl/certificate.pem;
    ssl_certificate_key /path/to/ssl/private_key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /opt/oncocentre/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/oncocentre /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 6. Testing Deployment

### Run Comprehensive Tests
```bash
# Set environment for testing
export AUTHORIZED_USERS="admin,doctor1,researcher1,nurse1"

# Test application functionality
python tests/test_roles_http.py

# Test whitelist management
python tests/test_whitelist_management.py
```

### Manual Testing Checklist
- [ ] Application accessible via HTTPS
- [ ] Login page loads correctly
- [ ] Admin can log in and access dashboard
- [ ] Whitelist management interface accessible at `/admin/whitelist`
- [ ] Can add/remove users from whitelist via web interface
- [ ] LDAP authentication working (if configured)
- [ ] Patient creation form accessible to regular users
- [ ] Admin restrictions working (cannot create patients)
- [ ] All static assets loading correctly

## 7. Whitelist Management

### Web Interface Management
Once deployed, administrators can manage the whitelist through the web interface:

1. **Login as Admin**: Use admin credentials to access the application
2. **Access Whitelist Management**: Navigate to `/admin/whitelist`
3. **Add Users**: Use the form to add new authorized users
4. **Remove Users**: Click remove button to deactivate users
5. **Migrate Environment**: Use migration button if needed

### Command Line Management (Emergency)
If web interface is unavailable:
```bash
# Add user to whitelist via script
python -c "
from app import create_app
from app.core.models import db, WhitelistEntry, User
app = create_app()
with app.app_context():
    admin = User.query.filter_by(is_admin=True).first()
    WhitelistEntry.add_username('new_user', admin.id, 'Emergency addition')
    print('User added to whitelist')
"

# Check whitelist status
python scripts/check_users.py
```

## 8. Monitoring and Maintenance

### Log Configuration
Configure application logging:
```python
# Add to app configuration
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/oncocentre.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

### Database Backup
```bash
# Create daily backup script
cat > /opt/oncocentre/backup_db.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/oncocentre/backups"
mkdir -p $BACKUP_DIR

# Backup SQLite database
cp /opt/oncocentre/instance/oncocentre.db $BACKUP_DIR/oncocentre_$DATE.db

# Keep only last 30 days of backups
find $BACKUP_DIR -name "oncocentre_*.db" -mtime +30 -delete
EOF

chmod +x /opt/oncocentre/backup_db.sh

# Add to crontab
echo "0 2 * * * /opt/oncocentre/backup_db.sh" | crontab -
```

### Health Check Script
```bash
cat > /opt/oncocentre/health_check.py << 'EOF'
#!/usr/bin/env python3
import requests
import sys

try:
    response = requests.get('https://oncocentre.institution.com/auth/login', timeout=10)
    if response.status_code == 200:
        print("OK: Application is responding")
        sys.exit(0)
    else:
        print(f"ERROR: Application returned status {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"ERROR: Cannot connect to application: {e}")
    sys.exit(1)
EOF

chmod +x /opt/oncocentre/health_check.py
```

## 9. Security Hardening

### File Permissions
```bash
# Set secure permissions
chmod 644 /opt/oncocentre/app/*.py
chmod 600 /opt/oncocentre/encryption.key
chmod 600 /opt/oncocentre/config/.ldap_config.env
chmod 755 /opt/oncocentre/static
chmod 755 /opt/oncocentre/templates
```

### Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw enable
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP (redirects to HTTPS)
sudo ufw allow 443/tcp   # HTTPS
```

### Regular Security Updates
```bash
# Create update script
cat > /opt/oncocentre/update_security.sh << 'EOF'
#!/bin/bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Python packages
cd /opt/oncocentre
source venv/bin/activate
pip list --outdated --format=json | python -c "
import json, sys
packages = json.load(sys.stdin)
for pkg in packages:
    print(f'pip install --upgrade {pkg[\"name\"]}')
" | bash

# Restart application
sudo systemctl restart oncocentre
EOF

chmod +x /opt/oncocentre/update_security.sh
```

## 10. Production Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Database initialized and migrated
- [ ] Admin users created
- [ ] Whitelist migrated to database
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] LDAP configuration tested (if applicable)

### Post-Deployment
- [ ] Application accessible via HTTPS
- [ ] Login functionality working
- [ ] Whitelist management accessible
- [ ] Admin interface functional
- [ ] Patient creation working for authorized users
- [ ] LDAP authentication working (if configured)
- [ ] Backup scripts configured
- [ ] Monitoring enabled
- [ ] Security hardening applied

### Ongoing Maintenance
- [ ] Regular database backups
- [ ] Log monitoring
- [ ] Security updates
- [ ] User access review
- [ ] SSL certificate renewal
- [ ] Performance monitoring

## Troubleshooting

### Common Issues

**Issue**: Application won't start
```bash
# Check service status
sudo systemctl status oncocentre

# Check logs
sudo journalctl -u oncocentre -n 50

# Check Gunicorn directly
cd /opt/oncocentre
source venv/bin/activate
gunicorn --config gunicorn.conf.py run:app
```

**Issue**: Database errors
```bash
# Check database file
ls -la instance/oncocentre.db

# Verify tables exist
python scripts/check_schema.py

# Re-migrate if needed
python scripts/migrate_whitelist.py
```

**Issue**: Encryption errors (InvalidToken)
```bash
# Fix encryption key mismatches - removes corrupted patient data
python scripts/fix_encryption_errors.py

# Note: This removes patient records that cannot be decrypted
# This typically happens when encryption keys change
```

**Issue**: Whitelist not working
```bash
# Check whitelist status
python scripts/check_users.py

# Test whitelist functionality
python tests/test_whitelist_management.py
```

**Issue**: LDAP authentication failing
```bash
# Test LDAP configuration
python scripts/setup_ldap.py

# Check LDAP connectivity
python -c "
from app.core.ldap_auth import ldap_auth
result = ldap_auth.test_connection()
print('LDAP test result:', result)
"
```

## Support and Documentation

- **Main Documentation**: `docs/CLAUDE.md`
- **Installation Guide**: `docs/INSTALLATION_GUIDE.md`
- **Security Guide**: `docs/SECURITY_DEPLOYMENT.md`
- **Admin Guide**: `docs/GUIDE_ADMINISTRATEUR.md`

The application is now production-ready with:
- Clean, maintainable codebase structure
- Database-driven whitelist management
- Comprehensive security features
- Full test coverage
- Complete documentation

For additional support or issues, refer to the comprehensive test suite and documentation provided.