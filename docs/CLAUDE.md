# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CARPEM Oncocentre is a Flask web application for managing patient identifier creation and access for the CARPEM biological data collection. The application generates unique identifiers following the format `ONCOCENTRE_YYYY_NNNNN` and provides a patient registry with comprehensive security features including dual authentication (Local + LDAP/Active Directory) and database-driven whitelist management.

## Project Structure

The application follows a modular Flask architecture:

```
oncocentre/
├── app/                          # Main application package
│   ├── __init__.py              # Application factory
│   ├── config.py                # Configuration settings
│   ├── admin/                   # Admin blueprint
│   │   ├── __init__.py
│   │   ├── views.py             # User management & whitelist routes
│   │   └── forms.py             # Admin forms (user creation/editing)
│   ├── auth/                    # Authentication blueprint
│   │   ├── __init__.py
│   │   ├── views.py             # Dual authentication (Local + LDAP)
│   │   └── forms.py             # Login forms
│   ├── main/                    # Main application blueprint
│   │   ├── __init__.py
│   │   ├── views.py             # Patient management routes
│   │   └── forms.py             # Patient creation forms
│   └── core/                    # Core modules
│       ├── __init__.py
│       ├── models.py            # All database models (User, Patient, WhitelistEntry)
│       ├── crypto.py            # Encryption utilities
│       ├── patient_id.py        # ID generation
│       ├── patient.py           # Patient model re-export
│       ├── utils.py             # Utility functions
│       └── ldap_auth.py         # LDAP authentication module
├── templates/                   # Jinja2 templates
│   ├── base.html                # Base template
│   ├── main/                    # Patient management templates
│   ├── auth/                    # Authentication templates
│   └── admin/                   # Admin interface templates
│       ├── dashboard.html       # Admin dashboard
│       ├── users.html           # User management
│       ├── edit_user.html       # User editing
│       └── whitelist.html       # Whitelist management (NEW)
├── static/                      # Static assets
│   ├── css/                     # Stylesheets
│   ├── js/                      # JavaScript
│   └── images/                  # Images
├── scripts/                     # Utility scripts
│   ├── migrate_whitelist.py     # Whitelist migration (NEW)
│   ├── check_users.py           # User verification
│   ├── create_users.py          # User creation
│   └── load_ldap_config.py      # LDAP configuration loader
├── tests/                       # Test suite
│   ├── test_roles_http.py       # Comprehensive role testing
│   ├── test_whitelist_management.py  # Whitelist testing (NEW)
│   └── [other test files]
├── docs/                        # Documentation
├── instance/                    # Instance-specific data
│   └── oncocentre.db           # SQLite database
├── run.py                       # Application entry point
└── encryption.key               # Data encryption key (sensitive)
```

## Key Features

### 1. Dual Authentication System
- **Local Authentication**: Username/password stored in SQLite database
- **LDAP/Active Directory**: Integration with institutional directory services
- **Automatic User Creation**: LDAP users auto-created on first login
- **User Management**: Admin interface for user creation and management

### 2. Database-Driven Whitelist Management (NEW)
- **Web Interface**: Admins can manage authorized users through the web UI
- **Migration Tool**: Seamlessly migrate from environment variables to database
- **Audit Trail**: Track who added users and when
- **Flexible Management**: Add descriptions, temporarily deactivate users
- **Backward Compatible**: Falls back to `AUTHORIZED_USERS` environment variable

### 3. Patient Data Management
- **Unique ID Generation**: `ONCOCENTRE_YYYY_NNNNN` format
- **Encrypted Storage**: PII encrypted using Fernet encryption
- **Role-Based Access**: Different access levels for users, PIs, and admins
- **Data Integrity**: Foreign key relationships and validation

### 4. Security Features
- **Role-Based Access Control**: Admin, Principal Investigator, Regular User roles
- **CSRF Protection**: Forms protected against cross-site request forgery
- **Password Hashing**: bcrypt for secure password storage
- **Session Management**: Flask-Login for secure session handling
- **Environment-Based Whitelisting**: Production-ready access control

## Database Models

### User Model (`app/core/models.py`)
```python
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=True)  # Nullable for LDAP users
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_principal_investigator = db.Column(db.Boolean, default=False, nullable=False)
    auth_source = db.Column(db.String(20), default='local', nullable=False)  # 'local' or 'ldap'
    # LDAP fields for directory integration
    email, first_name, last_name, display_name, ldap_dn, last_ldap_sync
```

### Patient Model (`app/core/models.py`)
```python
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    oncocentre_id = db.Column(db.String(50), unique=True, nullable=False)
    ipp_encrypted = db.Column(db.LargeBinary, nullable=False)  # Encrypted IPP
    # All PII fields are encrypted at rest
    first_name_encrypted, last_name_encrypted, birth_date_encrypted, sex
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
```

### WhitelistEntry Model (`app/core/models.py`) - NEW
```python
class WhitelistEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

## Authentication Flow

1. **User Access**: Application checks if username is in whitelist (database first, then environment variable)
2. **Method Selection**: User selects authentication method (Local or LDAP)
3. **Local Auth**: Credentials verified against SQLite database
4. **LDAP Auth**: Credentials verified against LDAP/AD server
5. **User Creation**: LDAP users auto-created in local database on first login
6. **Session Creation**: Flask-Login manages user session

## Whitelist Management (NEW FEATURE)

### Database-First Approach
The application now prioritizes database whitelist over environment variables:

```python
def get_authorized_users():
    """Get authorized users from database first, then environment variable as fallback"""
    try:
        from ..core.models import WhitelistEntry
        db_users = WhitelistEntry.get_authorized_usernames()
        if db_users:
            return db_users
    except Exception:
        # Fall back to environment variable
        pass
    users_str = os.environ.get('AUTHORIZED_USERS', 'admin,user1,user2,doctor1,researcher1')
    return set(user.strip() for user in users_str.split(',') if user.strip())
```

### Admin Interface
- **Access**: `/admin/whitelist` (admin only)
- **Add Users**: Simple form with username and optional description
- **Remove Users**: Deactivate users (preserves audit trail)
- **Reactivate**: Restore previously deactivated users
- **Migration**: One-click migration from environment variables

### Migration Process
```bash
# Migrate existing environment whitelist to database
python scripts/migrate_whitelist.py
```

## Development Workflow

### Running the Application
```bash
# Set environment variables
export AUTHORIZED_USERS="admin,user1,user2,doctor1,researcher1"

# Run development server
python run.py

# Access application
# http://localhost:5000
```

### Testing
```bash
# Run comprehensive role tests
python tests/test_roles_http.py

# Test whitelist management
python tests/test_whitelist_management.py

# Test all functionality
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

## Configuration

### Environment Variables
```bash
# Required
AUTHORIZED_USERS="admin,user1,user2,doctor1,researcher1"  # Whitelist (fallback)

# Optional LDAP configuration
LDAP_SERVER="ldap://your-ldap-server.com"
LDAP_BASE_DN="dc=your-domain,dc=com"
LDAP_USER_DN="cn=users,dc=your-domain,dc=com"
LDAP_BIND_USER="service-account@your-domain.com"
LDAP_BIND_PASSWORD="service-password"
```

### LDAP Configuration File (Optional)
Create `config/.ldap_config.env`:
```
LDAP_SERVER=ldap://your-ldap-server.com
LDAP_BASE_DN=dc=your-domain,dc=com
LDAP_USER_DN=cn=users,dc=your-domain,dc=com
LDAP_BIND_USER=service-account@your-domain.com
LDAP_BIND_PASSWORD=service-password
```

## Key Routes

### Authentication
- `GET /auth/login` - Login page with method selection
- `POST /auth/login` - Process login (local or LDAP)
- `GET /auth/logout` - Logout and session cleanup

### Main Application
- `GET /` - Patient creation form (authenticated users only)
- `POST /` - Create new patient identifier
- `GET /patients` - Patient list (role-based access)

### Admin Interface
- `GET /admin/dashboard` - Admin dashboard with statistics
- `GET /admin/users` - User management interface
- `GET /admin/users/create` - Create new user
- `GET /admin/users/<id>/edit` - Edit existing user
- `POST /admin/users/<id>/delete` - Delete/deactivate user
- `GET /admin/whitelist` - **NEW** Whitelist management interface
- `POST /admin/whitelist/add` - **NEW** Add user to whitelist
- `GET /admin/whitelist/remove/<username>` - **NEW** Remove user from whitelist
- `GET /admin/whitelist/migrate` - **NEW** Migrate environment to database

## Security Considerations

### Access Control
1. **Whitelist Enforcement**: Only whitelisted users can access the application
2. **Role-Based Permissions**: Different access levels for different user types
3. **Admin Restrictions**: Admins cannot create patient identifiers
4. **PI Enhanced Access**: Principal Investigators can view all patients

### Data Protection
1. **Encryption at Rest**: All PII encrypted using Fernet symmetric encryption
2. **Secure Sessions**: Flask-Login with secure session management
3. **CSRF Protection**: All forms protected against CSRF attacks
4. **Input Validation**: Comprehensive form validation using WTForms

### LDAP Security
1. **Secure Binding**: Service account for LDAP authentication
2. **SSL/TLS Support**: Encrypted LDAP connections (ldaps://)
3. **User Validation**: LDAP users validated against local whitelist
4. **Auto-sync**: LDAP user information synchronized on login

## Recent Updates

### Version 2.0 - Whitelist Management System
- **Database-Driven Whitelist**: Complete whitelist management through web interface
- **Migration Tools**: Seamless migration from environment variables
- **Audit Trail**: Track whitelist changes with timestamps and creators
- **Admin Interface**: User-friendly whitelist management in admin dashboard
- **Backward Compatibility**: Maintains compatibility with environment variable approach

### Code Restructuring
- **Cleaned Architecture**: Removed obsolete files and directories
- **Organized Structure**: Moved test files and scripts to proper directories
- **Updated Imports**: Fixed all import statements after reorganization
- **Documentation Update**: Comprehensive documentation reflecting current state

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all modules are in correct directories after restructuring
2. **LDAP Connection**: Check LDAP server connectivity and credentials
3. **Whitelist Issues**: Verify users are in database whitelist or environment variable
4. **Database Issues**: Run `python scripts/migrate_whitelist.py` to initialize whitelist table

### Logs and Debugging
- Application logs authentication attempts and errors
- Use `python scripts/check_users.py` to verify user database state
- Test whitelist functionality with `python tests/test_whitelist_management.py`

## Production Deployment

### Database Migration
```bash
# Initialize whitelist table and migrate environment users
python scripts/migrate_whitelist.py
```

### Security Checklist
- [ ] Database whitelist configured
- [ ] Environment variables set for production
- [ ] LDAP configuration secured
- [ ] SSL certificates installed
- [ ] Encryption keys protected
- [ ] Admin accounts configured
- [ ] Access logs enabled

The application is now production-ready with comprehensive whitelist management and a clean, maintainable codebase structure.