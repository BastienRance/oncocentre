# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CARPEM Oncocentre is a Flask web application for managing patient identifier creation and access for the CARPEM biological data collection. The application generates unique identifiers following the format `ONCOCENTRE_YYYY_NNNNN` and provides a patient registry with comprehensive security features including dual authentication (Local + LDAP/Active Directory).

## Project Structure

The application follows a modular Flask architecture:

```
oncocentre/
├── app/                          # Main application package
│   ├── __init__.py              # Application factory
│   ├── config.py                # Configuration settings (Local + LDAP)
│   ├── models/                  # Database models
│   │   ├── __init__.py
│   │   ├── user.py              # User authentication model (dual auth support)
│   │   └── patient.py           # Patient data model with encryption
│   ├── views/                   # Route handlers (blueprints)
│   │   ├── __init__.py
│   │   ├── auth.py              # Dual authentication routes (Local + LDAP)
│   │   ├── main.py              # Patient management routes
│   │   └── admin.py             # Administrative routes
│   ├── forms/                   # WTForms for validation
│   │   ├── __init__.py
│   │   ├── auth.py              # Login forms with auth method selection
│   │   ├── patient.py           # Patient creation forms
│   │   └── admin.py             # User management forms
│   └── utils/                   # Application utility functions
│       ├── __init__.py
│       ├── crypto.py            # Encryption utilities
│       ├── patient_id.py        # ID generation
│       └── ldap_auth.py         # LDAP authentication module
├── config/                      # Configuration files (git-ignored)
│   ├── .ldap_config.env         # LDAP server configuration (sensitive)
│   └── encryption.key           # Data encryption key (sensitive)
├── utils/                       # Global utility modules
│   └── load_ldap_config.py      # LDAP configuration loader
├── ssl/                         # SSL certificates (git-ignored)
│   ├── server.crt               # SSL certificate
│   └── server.key               # SSL private key
├── migrations/                  # Database management
│   ├── migrate.py               # Database migration script
│   ├── reset.py                 # Database reset script
│   └── add_ldap_fields.py       # LDAP fields migration
├── scripts/                     # Management scripts
│   ├── create_users.py          # User creation script
│   ├── make_admin.py            # Admin privilege management
│   ├── run_https.py             # HTTPS server
│   ├── setup_ldap.py            # Interactive LDAP configuration
│   └── cleanup_old_files.py     # File cleanup utility
├── tests/                       # Test files
│   ├── __init__.py
│   ├── test_auth.py             # Authentication tests
│   ├── test_patients.py         # Patient management tests
│   ├── test_dual_auth.py        # HTTP dual authentication tests
│   ├── test_simple_dual_auth.py # Direct dual authentication tests
│   └── test_refactored_app.py   # Comprehensive application tests
├── docs/                        # Documentation
│   ├── CLAUDE.md                # Developer documentation (this file)
│   ├── INSTALLATION_GUIDE.md
│   ├── SECURITY_DEPLOYMENT.md
│   ├── ADMIN_IMPLEMENTATION_SUMMARY.md
│   ├── GUIDE_UTILISATEUR.md     # French user documentation
│   └── GUIDE_ADMINISTRATEUR.md  # French admin documentation
├── templates/                   # Jinja2 templates
│   └── login.html              # Login form with auth method selection
├── static/                      # CSS/JS assets
├── instance/                    # Flask instance folder
│   └── oncocentre.db           # SQLite database
├── run.py                       # Application entry point
└── requirements.txt             # Dependencies (includes LDAP libraries)
```

## Development Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure LDAP (optional):
   ```bash
   # Interactive LDAP setup
   python scripts/setup_ldap.py
   
   # Or manually create config/.ldap_config.env with your LDAP settings
   ```

3. Create initial users and admin:
   ```bash
   python scripts/create_users.py
   python scripts/make_admin.py admin
   ```

4. Run database migrations (if upgrading):
   ```bash
   python migrations/add_ldap_fields.py
   ```

5. Run the application:
   ```bash
   # Development (HTTP)
   python run.py
   
   # Production (HTTPS)
   python scripts/run_https.py
   ```

Application URLs:
- HTTP: `http://localhost:5000`
- HTTPS: `https://localhost:5000`
- Login: `/auth/login`

## Architecture Overview

### Application Factory Pattern
The application uses Flask's application factory pattern in `app/__init__.py`, allowing for different configurations (development, testing, production).

### Modular Design
- **Models**: Database models split by entity (`user.py`, `patient.py`)
- **Views**: Route handlers organized by functionality (`auth.py`, `main.py`, `admin.py`)
- **Forms**: Form classes grouped by purpose (`auth.py`, `patient.py`, `admin.py`)
- **Utils**: Utility functions separated by domain (`crypto.py`, `patient_id.py`)

### Security Architecture

**Data Encryption**: Field-level encryption using Fernet symmetric encryption:
- Patient IPP (identifiant permanent du patient)
- First/last names
- Birth dates
- Encryption key automatically generated and stored in `config/encryption.key`

**Dual Authentication System**: Supports both local and LDAP/Active Directory authentication:
- **Auto-detect Mode**: Tries local authentication first, falls back to LDAP
- **Local Authentication**: Bcrypt-hashed passwords stored in local database
- **LDAP Authentication**: Integration with Active Directory/OpenLDAP servers
- **User Auto-creation**: LDAP users automatically created in local database on first login
- **User Synchronization**: User information updated from LDAP on each login

**Authentication Flow**:
1. User selects authentication method (Auto-detect, Local, or LDAP) on login form
2. Credentials validated according to selected method
3. Username checked against `AUTHORIZED_USERS` environment variable whitelist
4. User account status (`is_active`) verified
5. Flask-Login session management with fallback direct database access

**Authorization Levels**:
- Regular users: Access only their own patient records
- Admin users: Full user management through web interface
- User isolation enforced at database query level

### Database Schema

SQLite with two main tables:

**User Table** (`app/models/user.py`):
- Authentication and authorization fields
- `is_admin` boolean for role-based access
- `is_active` for account management
- `auth_source` field ('local' or 'ldap')
- LDAP-specific fields: `email`, `first_name`, `last_name`, `display_name`, `ldap_dn`, `last_ldap_sync`
- Bcrypt password hashing for local users (nullable for LDAP users)

**Patient Table** (`app/models/patient.py`):
- Encrypted sensitive fields with property-based access
- `created_by` foreign key for user isolation
- `oncocentre_id` unique identifier generation

## Common Commands

### Development Commands
```bash
# Start development server
python run.py

# Start secure HTTPS server  
python scripts/run_https.py

# Create test users (admin/admin123, user1/user1123, etc.)
python scripts/create_users.py

# Grant admin privileges
python scripts/make_admin.py <username>

# List admin users
python scripts/make_admin.py list
```

### LDAP Configuration Commands
```bash
# Interactive LDAP setup
python scripts/setup_ldap.py

# Load LDAP configuration (for testing)
python utils/load_ldap_config.py

# Test LDAP connection (via admin interface at /auth/ldap-test)
```

### Database Management
```bash
# Reset database completely
python migrations/reset.py

# Migrate existing database (adds admin features)
python migrations/migrate.py

# Add LDAP fields to existing User table
python migrations/add_ldap_fields.py
```

### Testing Commands
```bash
# Run authentication tests
python tests/test_auth.py

# Run patient management tests
python tests/test_patients.py

# Run dual authentication tests
python tests/test_simple_dual_auth.py
python tests/test_dual_auth.py

# Run comprehensive application tests
python tests/test_refactored_app.py
```

## Development Patterns

### Import Patterns
- Use relative imports within the app package: `from ..models import User`
- Use absolute imports for external packages: `from flask import Blueprint`
- Avoid circular imports by importing inside functions when necessary

### Database Access Pattern
The application implements a fallback pattern for database access to handle SQLAlchemy metadata caching issues:
1. Attempt SQLAlchemy ORM query
2. Fall back to direct sqlite3 connection
3. Return compatible user objects

This pattern is implemented in `app/views/auth.py` and `app/__init__.py`.

### Encryption Pattern
Sensitive data uses property-based encryption in `app/models/patient.py`:
```python
@property
def field_name(self):
    return decrypt_data(self.field_name_encrypted)

@field_name.setter
def field_name(self, value):
    self.field_name_encrypted = encrypt_data(value)
```

### Admin Interface Pattern
Admin functionality uses dedicated Blueprint with role-based decorators and comprehensive user management features accessible via `/admin/dashboard`.

## Environment Configuration

Required environment variables:
```bash
export SECRET_KEY="production-secret-key"
export AUTHORIZED_USERS="admin,user1,user2,doctor1,researcher1"
export FLASK_CONFIG="development"  # or "production"
```

LDAP configuration (optional, stored in `config/.ldap_config.env`):
```bash
LDAP_ENABLED=true
LDAP_SERVER=ldap://dc.company.com
LDAP_PORT=389
LDAP_USE_SSL=false
LDAP_DOMAIN=COMPANY
LDAP_BASE_DN=DC=company,DC=com
LDAP_USER_SEARCH_BASE=OU=Users,DC=company,DC=com
LDAP_USER_SEARCH_FILTER=(sAMAccountName={username})
LDAP_BIND_USER=CN=ServiceAccount,OU=ServiceAccounts,DC=company,DC=com
LDAP_BIND_PASSWORD=YourServiceAccountPassword
LDAP_TIMEOUT=10
ALLOW_LOCAL_AUTH=true
ALLOW_LDAP_AUTH=true
AUTO_CREATE_LDAP_USERS=true
```

## Security Features

- **Data at rest**: Fernet encryption for sensitive patient data
- **Data in transit**: HTTPS with security headers (HSTS, CSP, X-Frame-Options)
- **Dual authentication**: Local password authentication + LDAP/Active Directory integration
- **Authentication methods**: Auto-detect, Local-only, or LDAP-only modes
- **User synchronization**: Automatic LDAP user creation and information updates
- **Session management**: Flask-Login with secure session handling
- **Access control**: User isolation and role-based permissions
- **CSRF protection**: WTForms CSRF tokens on all forms
- **Admin interface**: Web-based user management with comprehensive controls
- **Configuration security**: Sensitive LDAP credentials stored in git-ignored config files

## Testing Strategy

The codebase includes comprehensive test files:
- `tests/test_auth.py`: Authentication flow testing
- `tests/test_patients.py`: Patient management and encryption testing
- `tests/test_simple_dual_auth.py`: Direct dual authentication function testing
- `tests/test_dual_auth.py`: HTTP-based dual authentication testing
- `tests/test_refactored_app.py`: Full application integration testing

## File Generation Notes

Key files generated at runtime:
- `instance/oncocentre.db`: SQLite database (Flask instance folder)
- `config/encryption.key`: Fernet encryption key (critical for data access)
- `ssl/server.crt`/`ssl/server.key`: SSL certificates for HTTPS
- `config/.ldap_config.env`: LDAP configuration (created by setup script)

## Application Routes

- `/`: Patient creation form (requires login)
- `/patients`: User's patient list (user-specific)
- `/preview_id`: AJAX endpoint for ID preview
- `/auth/login`: Authentication endpoint with dual auth method selection
- `/auth/logout`: Logout endpoint
- `/auth/ldap-test`: LDAP connection testing (admin only)
- `/auth/create_initial_user`: Initial admin user creation (dev only)
- `/admin/dashboard`: Admin interface (admin only)
- `/admin/users`: User management (admin only)
- `/admin/users/create`: User creation (admin only)
- `/admin/users/<id>/edit`: User editing (admin only)
- `/admin/system_info`: System information display (admin only)

## Migration Notes

This codebase has been refactored from a flat file structure to a modular Flask application with dual authentication support. Key improvements:

1. **Separation of Concerns**: Models, views, forms, and utilities are now in separate modules
2. **Application Factory**: Supports multiple configurations and testing
3. **Blueprints**: Routes are organized by functionality
4. **Centralized Configuration**: All settings in `app/config.py` with LDAP support
5. **Dual Authentication**: Local and LDAP/Active Directory authentication with auto-detect mode
6. **Organized File Structure**: 
   - Configuration files in `config/` (git-ignored for security)
   - Utility modules in `utils/`
   - SSL certificates in `ssl/`
   - All test files in `tests/`
   - Management scripts in `scripts/`
7. **Enhanced Security**: LDAP credentials and encryption keys properly secured
8. **User Documentation**: Comprehensive French documentation for end users and administrators
9. **Migration Scripts**: Database migration support for LDAP fields

## Documentation

### Available Documentation Files

- **`GUIDE_UTILISATEUR.md`**: Complete French user manual covering login, patient creation, and all user features
- **`GUIDE_ADMINISTRATEUR.md`**: French administrator guide covering installation, user management, security, and maintenance
- **`INSTALLATION_GUIDE.md`**: Technical installation and setup instructions
- **`SECURITY_DEPLOYMENT.md`**: Security features and deployment guidelines
- **`ADMIN_IMPLEMENTATION_SUMMARY.md`**: Technical overview of admin features