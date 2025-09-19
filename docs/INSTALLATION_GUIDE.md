# CARPEM Oncocentre - Complete Installation Guide

## 📋 Overview

CARPEM Oncocentre is a secure Flask web application for managing patient identifier creation and access. This guide covers installation, configuration, and administration of the complete system with security features and user management.

## 🎯 Features

- **Secure User Authentication**: Login system with password hashing
- **Patient Identifier Management**: Generate unique ONCOCENTRE_YYYY_NNNNN identifiers
- **Data Encryption**: All sensitive patient data encrypted at rest
- **HTTPS Support**: Secure communication with SSL/TLS
- **Admin User Management**: Web interface for user administration
- **Access Control**: Role-based permissions and user isolation
- **Audit Trail**: User activity tracking and logging

## 🚀 Quick Start Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- Git (optional, for cloning)

### 1. Download and Setup

```bash
# Clone or download the project
cd /path/to/your/projects
# Extract or clone the CARPEM Oncocentre files

# Navigate to project directory
cd oncocentre

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Initialize Database and Users

```bash
# Create initial test users
python create_test_users.py

# Make admin user an administrator
python make_admin.py admin
```

This creates the following users:
- `admin / admin123` (Administrator)
- `user1 / user1123` (Regular user)
- `user2 / user2123` (Regular user)
- `doctor1 / doctor123` (Regular user)
- `researcher1 / research123` (Regular user)

### 3. Run the Application

#### Development (HTTP):
```bash
python app.py
```
Access at: `http://localhost:5000`

#### Production (HTTPS):
```bash
python run_https.py
```
Access at: `https://localhost:5000`

### 4. Login and Test

1. Open your browser to the application URL
2. Login with: `admin / admin123`
3. Access admin features via the "Administration" menu
4. Create patients and manage users

## 🔧 Detailed Installation

### Database Setup

The application uses SQLite by default. For existing installations that need the admin column:

```bash
# Check current database schema
python check_database.py

# Migrate existing database (adds admin features)
python migrate_database.py

# Reset database completely (if needed)
python reset_database.py
```

### Environment Configuration

Create or update environment variables:

```bash
# Windows
set SECRET_KEY=your-super-secret-key-here
set AUTHORIZED_USERS=admin,user1,user2,doctor1,researcher1

# Linux/Mac
export SECRET_KEY="your-super-secret-key-here"
export AUTHORIZED_USERS="admin,user1,user2,doctor1,researcher1"
```

### SSL Certificate Setup

#### Development (Self-signed certificates):
The application automatically generates self-signed certificates when running `python run_https.py`.

#### Production (CA-signed certificates):
1. Obtain SSL certificates from a Certificate Authority
2. Replace `server.crt` and `server.key` with your certificates
3. Ensure proper file permissions (readable by application only)

## 👑 Admin User Management

### Web Interface (Recommended)

1. **Login as Admin**: Use `admin / admin123`
2. **Access Admin Menu**: Click "Administration" in navigation
3. **Dashboard**: View system statistics and recent activity
4. **User Management**: Create, edit, or deactivate users
5. **System Info**: Monitor security settings and configuration

### Admin Features

- **Create Users**: Add new users with username/password
- **Edit Users**: Modify user status, admin privileges, reset passwords
- **Delete Users**: Safely remove users (deactivates if they have patients)
- **System Monitoring**: View user counts, patient statistics, security status

### Command Line Administration

```bash
# List all users
python manage_users.py list

# Create new user
python manage_users.py create newuser

# Make user an administrator
python make_admin.py username

# Deactivate user
python manage_users.py deactivate username

# Reset user password
python manage_users.py reset username
```

## 🔒 Security Configuration

### Encryption

- **Patient Data**: All sensitive patient information is encrypted using Fernet symmetric encryption
- **Passwords**: User passwords are hashed using bcrypt with salt
- **Encryption Key**: Automatically generated and stored in `encryption.key`

### Access Control

- **Authentication**: All pages require login except login page itself
- **Authorization**: Users can only access their own patient records
- **Admin Access**: Admin functions restricted to users with `is_admin=True`
- **Whitelist**: Only users in `AUTHORIZED_USERS` can log in

### HTTPS Configuration

- **Development**: Self-signed certificates automatically generated
- **Production**: Use CA-signed certificates for `server.crt` and `server.key`
- **Security Headers**: HSTS, CSP, X-Frame-Options automatically added
- **Redirection**: HTTP automatically redirects to HTTPS in production

## 🧪 Testing and Validation

### Security Tests

```bash
# Run comprehensive security test suite
python test_security_fixed.py

# Test login functionality specifically
python test_simple_login.py

# Test admin functionality
python ADMIN_SETUP_COMPLETE.py

# Run functionality tests
python test_functionality.py
```

### Manual Testing Checklist

- [ ] Can login with admin credentials
- [ ] Can access admin dashboard
- [ ] Can create new users through web interface
- [ ] Can edit existing users
- [ ] Regular users cannot access admin functions
- [ ] Patient data is properly encrypted
- [ ] User access is restricted to own patients
- [ ] HTTPS is working (production)
- [ ] Forms have CSRF protection

## 📁 File Structure

```
oncocentre/
├── app.py                          # Main application
├── models.py                       # Database models (User, Patient)
├── routes.py                       # Patient management routes
├── auth.py                         # Authentication routes
├── admin.py                        # Admin management routes
├── forms.py                        # WTForms for validation
├── utils.py                        # Utility functions
├── requirements.txt                # Python dependencies
├── run_https.py                   # HTTPS server
├── create_test_users.py           # User creation script
├── make_admin.py                  # Admin management utility
├── manage_users.py                # Legacy user management
├── templates/                     # HTML templates
│   ├── base.html                  # Base template
│   ├── index.html                 # Patient creation form
│   ├── patients.html              # Patient list
│   ├── login.html                 # Login form
│   └── admin/                     # Admin templates
│       ├── dashboard.html         # Admin dashboard
│       ├── users.html            # User management
│       ├── create_user.html      # User creation
│       ├── edit_user.html        # User editing
│       └── system_info.html      # System information
├── static/                        # CSS/JS assets
├── oncocentre.db                  # SQLite database (created)
├── encryption.key                 # Encryption key (created)
├── server.crt                     # SSL certificate (created)
└── server.key                     # SSL private key (created)
```

## 🚨 Troubleshooting

### Common Issues

**1. Login not working:**
- Check if user exists: `python manage_users.py list`
- Verify user is in AUTHORIZED_USERS environment variable
- Check password: users created with `create_test_users.py` have known passwords

**2. Admin features not accessible:**
- Make user admin: `python make_admin.py username`
- Verify admin status: `python make_admin.py list`
- Check browser developer tools for 403 errors

**3. Database errors:**
- For existing installations: `python migrate_database.py`
- For fresh start: `python reset_database.py`
- Check schema: `python check_database.py`

**4. HTTPS certificate issues:**
- Delete `server.crt` and `server.key`, restart `run_https.py`
- For production, ensure certificate files have correct permissions
- Check certificate validity dates

**5. Permission errors:**
- Ensure application has write permissions for database files
- Check file ownership and permissions on Linux/Mac systems
- Verify encryption key file is readable

### Debug Commands

```bash
# Check database status
python check_database.py

# Debug login issues
python debug_login.py

# Verify admin functionality
python ADMIN_SETUP_COMPLETE.py

# Test complete security setup
python FINAL_LOGIN_TEST.py
```

## 🔄 Updates and Maintenance

### Regular Tasks

- **Weekly**: Review user access logs, check for failed login attempts
- **Monthly**: Update Python dependencies, review user accounts
- **Quarterly**: Rotate encryption keys, audit user permissions
- **Annually**: Security assessment, certificate renewal

### Updating Dependencies

```bash
# Update Python packages
pip install --upgrade -r requirements.txt

# Check for security vulnerabilities
pip audit
```

### Backup Strategy

Essential files to backup:
- `oncocentre.db` (database)
- `encryption.key` (encryption key)
- `server.crt` and `server.key` (SSL certificates)
- Configuration files and environment variables

## 📞 Support

### Documentation Files

- `CLAUDE.md` - Development setup and architecture
- `SECURITY_DEPLOYMENT.md` - Security features and deployment
- `ADMIN_IMPLEMENTATION_SUMMARY.md` - Admin features overview

### Logs and Monitoring

- Application logs available in console output
- Failed login attempts logged automatically
- Admin actions logged for audit trail
- Monitor `oncocentre.db` file size and growth

## 🎉 Production Deployment

### Pre-deployment Checklist

- [ ] Update `SECRET_KEY` to strong random value
- [ ] Configure `AUTHORIZED_USERS` with production usernames
- [ ] Install proper SSL certificates
- [ ] Set up firewall rules (allow HTTPS, block HTTP in production)
- [ ] Configure backup strategy
- [ ] Set up monitoring and alerting
- [ ] Change default admin password
- [ ] Test all functionality in staging environment

### Production Environment Variables

```bash
export SECRET_KEY="$(openssl rand -hex 32)"
export AUTHORIZED_USERS="admin,doctor1,researcher1,nurse1"
export FLASK_ENV="production"
```

### Deployment Command

```bash
# Production deployment with HTTPS
python run_https.py
```

## ✅ Installation Complete

Your CARPEM Oncocentre installation is now complete with:

- ✅ Secure user authentication and authorization
- ✅ Encrypted patient data storage
- ✅ Admin user management interface
- ✅ HTTPS security
- ✅ Role-based access control
- ✅ Comprehensive testing suite

The application is ready for secure patient identifier management with full administrative capabilities.