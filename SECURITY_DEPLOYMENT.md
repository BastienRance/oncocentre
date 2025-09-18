# CARPEM Oncocentre - Security Deployment Guide

## 🔐 Security Features Implemented

### ✅ Database Encryption
- **Sensitive patient data encrypted**: IPP, first name, last name, birth date
- **Encryption key management**: Automatic key generation and secure storage
- **Field-level encryption**: Uses Fernet symmetric encryption from cryptography library

### ✅ User Authentication
- **Login/password authentication**: Secure password hashing with bcrypt
- **Session management**: Flask-Login for secure session handling
- **Password requirements**: Minimum 8 characters (configurable)

### ✅ Authorization & Access Control
- **Whitelist-based authorization**: Only pre-authorized users can access the system
- **User isolation**: Users can only access patients they created
- **Role-based access**: Admin and user roles with different privileges
- **Admin user management**: Web interface for creating and managing users

### ✅ HTTPS/TLS Support
- **SSL/TLS encryption**: All traffic encrypted in transit
- **Certificate management**: Self-signed certificates for development, production-ready configuration
- **Security headers**: HSTS, CSP, X-Frame-Options, and more

### ✅ Security Testing
- **Comprehensive test suite**: Authentication, encryption, authorization tests
- **Input validation tests**: Form validation and sanitization
- **Integration tests**: End-to-end security workflows

## 🚀 Deployment Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Initial Users

```bash
# Create initial users with the new system
python create_test_users.py

# Make admin user an administrator
python make_admin.py admin

# Or create users individually (legacy method)
python manage_users.py create admin
python manage_users.py create user1
python manage_users.py create user2
```

### 3. Configure Environment Variables

```bash
# Set secret key (use a strong random key in production)
export SECRET_KEY="your-super-secret-key-here"

# Configure authorized users (comma-separated)
export AUTHORIZED_USERS="admin,user1,user2,doctor1,researcher1"
```

### 4. Run Security Tests

```bash
# Run comprehensive security test suite
python test_security.py
```

### 5. Deploy with HTTPS

#### Development/Testing:
```bash
# Run with self-signed certificates
python run_https.py
```

#### Production:
1. Obtain proper SSL certificates from a Certificate Authority
2. Replace `server.crt` and `server.key` with your certificates
3. Configure firewall and reverse proxy if needed
4. Run the HTTPS server:

```bash
python run_https.py
```

### 6. Access the Application

- **URL**: `https://localhost:5000` (development) or your domain (production)
- **Login**: Use credentials created in step 2
  - Admin: `admin / admin123`
  - Users: `user1 / user1123`, `user2 / user2123`, etc.
- **Admin Features**: Login as admin to access user management
- **Security**: All functionality requires authentication and follows security policies

## 🔒 Security Configuration Details

### Database Encryption Configuration

The application automatically:
- Generates encryption keys on first run (`encryption.key` file)
- Encrypts sensitive patient data before database storage
- Decrypts data automatically when accessed through the application

**Important**: Backup the `encryption.key` file securely. Loss of this key means permanent data loss.

### User Whitelist Configuration

Authorized users are configured via the `AUTHORIZED_USERS` environment variable:

```bash
# Example: Allow specific users
export AUTHORIZED_USERS="admin,researcher1,doctor2,nurse3"
```

Only users in this whitelist can log in, even if they have valid credentials.

### HTTPS Configuration

The application includes:
- **Development**: Self-signed certificate generation
- **Production**: Support for proper CA-signed certificates
- **Security headers**: Automatic security header injection
- **HSTS**: HTTP Strict Transport Security enabled

## 🛡️ Security Best Practices

### Production Deployment Checklist

- [ ] **Change default passwords**: Ensure all default/demo passwords are changed
- [ ] **Use strong SECRET_KEY**: Generate a cryptographically secure secret key
- [ ] **Proper SSL certificates**: Use CA-signed certificates in production
- [ ] **Firewall configuration**: Restrict access to necessary ports only
- [ ] **Regular key rotation**: Plan for periodic encryption key rotation
- [ ] **Backup strategy**: Secure backup of encryption keys and database
- [ ] **Monitoring**: Implement login attempt monitoring and alerting
- [ ] **Updates**: Keep dependencies updated for security patches

### User Management

#### Web Interface (Recommended)
1. Login as admin user
2. Use "Administration" menu in navigation
3. Access user management dashboard
4. Create, edit, or deactivate users through web interface

#### Command Line (Legacy)
```bash
# List all users
python manage_users.py list

# Make user an admin
python make_admin.py username

# Deactivate a user
python manage_users.py deactivate username

# Reset user password
python manage_users.py reset username

# Reactivate a user
python manage_users.py activate username
```

### Monitoring and Logs

The application logs authentication attempts and security events. Monitor:
- Failed login attempts
- Unauthorized access attempts
- User creation/modification events
- Patient data access patterns

## 🚨 Incident Response

### If Security Breach Suspected:

1. **Immediate Actions**:
   - Deactivate affected user accounts
   - Change encryption keys if compromise suspected
   - Review access logs for unauthorized activity

2. **Investigation**:
   - Run security test suite to verify system integrity
   - Check database for unauthorized modifications
   - Review application logs for suspicious patterns

3. **Recovery**:
   - Restore from clean backups if necessary
   - Reset all user passwords
   - Update security configurations as needed

## 📞 Support and Maintenance

### Regular Maintenance Tasks:

- **Weekly**: Review user access logs
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Rotate encryption keys and review user access rights
- **Annually**: Full security audit and penetration testing

### Troubleshooting:

- **Login Issues**: Check user is in AUTHORIZED_USERS whitelist
- **Encryption Errors**: Verify `encryption.key` file exists and is readable
- **HTTPS Issues**: Check certificate files and SSL configuration
- **Database Issues**: Verify SQLite database permissions and integrity

## 📋 Compliance Notes

This implementation addresses:
- **Data encryption at rest**: Sensitive patient data encrypted in database
- **Data encryption in transit**: HTTPS/TLS for all communications
- **Access control**: User authentication and authorization
- **Audit trail**: User actions logged for compliance tracking
- **Data isolation**: Users can only access their own patient records

For additional compliance requirements (HIPAA, GDPR, etc.), consider:
- Enhanced audit logging
- Data retention policies
- Additional access controls
- Regular security assessments