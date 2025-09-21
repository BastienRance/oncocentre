# CARPEM Oncocentre

A secure Flask web application for managing patient identifier creation and access for the CARPEM biological data collection.

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd oncocentre
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment and run
export AUTHORIZED_USERS="admin,user1,user2"
python run.py
```

Visit `http://localhost:5000` to access the application.

## ✨ Key Features

### 🔐 Advanced Security
- **Dual Authentication**: Local database + LDAP/Active Directory integration
- **Database-Driven Whitelist**: Web-based user access management
- **Role-Based Access Control**: Admin, Principal Investigator, and Regular User roles
- **Data Encryption**: All PII encrypted at rest using Fernet encryption
- **CSRF Protection**: All forms protected against cross-site request forgery

### 👥 User Management
- **Web-Based Whitelist Management**: Add/remove authorized users through admin interface
- **Migration Tools**: Seamlessly migrate from environment variables to database
- **Audit Trail**: Track who added users and when
- **Flexible Administration**: Temporary deactivation, descriptions, and reactivation

### 🏥 Patient Data
- **Unique ID Generation**: `ONCOCENTRE_YYYY_NNNNN` format
- **Secure Registry**: Encrypted patient information storage
- **Access Control**: Role-based patient data visibility
- **Data Integrity**: Comprehensive validation and foreign key relationships

## 📁 Project Structure

```
oncocentre/
├── app/                    # Main application package
│   ├── admin/             # Admin interface (user & whitelist management)
│   ├── auth/              # Authentication (local + LDAP)
│   ├── main/              # Patient management
│   └── core/              # Database models and utilities
├── templates/             # Jinja2 templates
├── static/               # CSS, JavaScript, images
├── scripts/              # Utility scripts
├── tests/                # Comprehensive test suite
├── docs/                 # Documentation
└── run.py                # Application entry point
```

## 🛠️ Development

### Running Tests
```bash
# Comprehensive role testing
python tests/test_roles_http.py

# Whitelist management testing
python tests/test_whitelist_management.py

# All functionality tests
python tests/test_specifications.py
```

### User Management
```bash
# Check current users
python scripts/check_users.py

# Create test users
python scripts/create_users.py

# Migrate whitelist to database
python scripts/migrate_whitelist.py
```

## 🔧 Configuration

### Environment Variables
```bash
# Required (fallback for whitelist)
AUTHORIZED_USERS="admin,user1,user2,doctor1,researcher1"

# Optional LDAP configuration
LDAP_SERVER="ldaps://ldap.institution.com"
LDAP_BASE_DN="dc=institution,dc=com"
LDAP_USER_DN="cn=users,dc=institution,dc=com"
LDAP_BIND_USER="service-account@institution.com"
LDAP_BIND_PASSWORD="service-password"
```

### LDAP Configuration (Optional)
Create `config/.ldap_config.env` for LDAP settings.

## 👨‍💼 Admin Interface

### Whitelist Management
- **Access**: `/admin/whitelist` (admin users only)
- **Features**:
  - Add new authorized users with descriptions
  - Remove/deactivate users (preserves audit trail)
  - Reactivate previously deactivated users
  - One-click migration from environment variables
  - View current environment vs database status

### User Management
- **Access**: `/admin/dashboard`
- **Features**:
  - Create new users with role assignment
  - Edit existing user permissions
  - View user statistics and recent activity
  - Manage user activation status

## 🔒 Security Features

### Access Control
- **Whitelist Enforcement**: Only whitelisted users can access the application
- **Role-Based Permissions**: Different access levels for different user types
- **Admin Restrictions**: Admins cannot create patient identifiers (separation of duties)
- **PI Enhanced Access**: Principal Investigators can view all patients

### Data Protection
- **Encryption at Rest**: All PII encrypted using Fernet symmetric encryption
- **Secure Sessions**: Flask-Login with secure session management
- **Input Validation**: Comprehensive form validation using WTForms
- **CSRF Protection**: All forms protected against attacks

### LDAP Security
- **Secure Binding**: Service account for LDAP authentication
- **SSL/TLS Support**: Encrypted LDAP connections
- **User Validation**: LDAP users validated against local whitelist
- **Auto-sync**: LDAP user information synchronized on login

## 🚀 Production Deployment

### Quick Deploy
```bash
# Initialize database and migrate whitelist
python scripts/migrate_whitelist.py

# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn --bind 0.0.0.0:8000 run:app
```

### Full Production Setup
See `docs/DEPLOYMENT_GUIDE.md` for comprehensive production deployment instructions including:
- Systemd service configuration
- Nginx reverse proxy setup
- SSL/TLS configuration
- Database backup strategies
- Security hardening
- Monitoring and maintenance

## 📚 Documentation

- **Developer Guide**: [`docs/CLAUDE.md`](docs/CLAUDE.md) - Comprehensive developer documentation
- **Deployment Guide**: [`docs/DEPLOYMENT_GUIDE.md`](docs/DEPLOYMENT_GUIDE.md) - Production deployment instructions
- **Installation Guide**: [`docs/INSTALLATION_GUIDE.md`](docs/INSTALLATION_GUIDE.md) - Detailed installation steps
- **Security Guide**: [`docs/SECURITY_DEPLOYMENT.md`](docs/SECURITY_DEPLOYMENT.md) - Security considerations
- **Admin Guide**: [`docs/GUIDE_ADMINISTRATEUR.md`](docs/GUIDE_ADMINISTRATEUR.md) - Administrator manual

## 🧪 Testing

The application includes comprehensive test coverage:

- **Role-Based Testing**: Verify all user roles work correctly
- **Authentication Testing**: Test both local and LDAP authentication
- **Whitelist Management Testing**: Verify database-driven whitelist functionality
- **Security Testing**: Validate access controls and permissions
- **Integration Testing**: End-to-end functionality verification

## 📈 Recent Updates (Version 2.0)

### 🆕 Database-Driven Whitelist Management
- Complete whitelist management through web interface
- Migration tools for seamless transition from environment variables
- Audit trail with timestamps and user tracking
- Admin-friendly interface integrated into dashboard

### 🏗️ Code Restructuring
- Cleaned architecture with removed obsolete files
- Organized directory structure with proper separation
- Updated documentation reflecting current state
- Comprehensive test suite reorganization

## 🤝 Contributing

1. Follow the existing code style and architecture
2. Run the full test suite before submitting changes
3. Update documentation for any new features
4. Ensure security best practices are maintained

## 📄 License

This project is developed for the CARPEM consortium for biological data management.

## 🆘 Support

For issues or questions:
1. Check the comprehensive documentation in `docs/`
2. Run the test suite to verify functionality
3. Review the troubleshooting section in `docs/DEPLOYMENT_GUIDE.md`

---

**CARPEM Oncocentre** - Secure, scalable patient identifier management for biological research.