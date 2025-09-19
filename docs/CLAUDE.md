# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CARPEM Oncocentre is a Flask web application for managing patient identifier creation and access for the CARPEM biological data collection. The application generates unique identifiers following the format `ONCOCENTRE_YYYY_NNNNN` and provides a patient registry with comprehensive security features.

## Project Structure

The application follows a modular Flask architecture:

```
oncocentre/
├── app/                          # Main application package
│   ├── __init__.py              # Application factory
│   ├── config.py                # Configuration settings
│   ├── models/                  # Database models
│   │   ├── __init__.py
│   │   ├── user.py              # User authentication model
│   │   └── patient.py           # Patient data model with encryption
│   ├── views/                   # Route handlers (blueprints)
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication routes
│   │   ├── main.py              # Patient management routes
│   │   └── admin.py             # Administrative routes
│   ├── forms/                   # WTForms for validation
│   │   ├── __init__.py
│   │   ├── auth.py              # Login forms
│   │   ├── patient.py           # Patient creation forms
│   │   └── admin.py             # User management forms
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       ├── crypto.py            # Encryption utilities
│       └── patient_id.py        # ID generation
├── migrations/                  # Database management
│   ├── __init__.py
│   ├── migrate.py               # Database migration script
│   └── reset.py                 # Database reset script
├── scripts/                     # Management scripts
│   ├── create_users.py          # User creation script
│   ├── make_admin.py            # Admin privilege management
│   └── run_https.py             # HTTPS server
├── tests/                       # Test files
│   ├── __init__.py
│   ├── test_auth.py             # Authentication tests
│   └── test_patients.py         # Patient management tests
├── docs/                        # Documentation
│   ├── INSTALLATION_GUIDE.md
│   ├── SECURITY_DEPLOYMENT.md
│   └── ADMIN_IMPLEMENTATION_SUMMARY.md
├── templates/                   # Jinja2 templates
├── static/                      # CSS/JS assets
├── run.py                       # Application entry point
└── requirements.txt
```

## Development Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create initial users and admin:
   ```bash
   python scripts/create_users.py
   python scripts/make_admin.py admin
   ```

3. Run the application:
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
- Encryption key automatically generated and stored in `encryption.key`

**Authentication Flow**:
1. User credentials validated against bcrypt-hashed passwords
2. Username checked against `AUTHORIZED_USERS` environment variable whitelist
3. User account status (`is_active`) verified
4. Flask-Login session management with fallback direct database access

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
- Bcrypt password hashing

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

### Database Management
```bash
# Reset database completely
python migrations/reset.py

# Migrate existing database (adds admin features)
python migrations/migrate.py
```

### Testing Commands
```bash
# Run authentication tests
python tests/test_auth.py

# Run patient management tests
python tests/test_patients.py
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

## Security Features

- **Data at rest**: Fernet encryption for sensitive patient data
- **Data in transit**: HTTPS with security headers (HSTS, CSP, X-Frame-Options)
- **Authentication**: Bcrypt password hashing with whitelist authorization
- **Session management**: Flask-Login with secure session handling
- **Access control**: User isolation and role-based permissions
- **CSRF protection**: WTForms CSRF tokens on all forms
- **Admin interface**: Web-based user management with comprehensive controls

## Testing Strategy

The codebase includes focused test files:
- `tests/test_auth.py`: Authentication flow testing
- `tests/test_patients.py`: Patient management and encryption testing

## File Generation Notes

Key files generated at runtime:
- `instance/oncocentre.db`: SQLite database (Flask instance folder)
- `encryption.key`: Fernet encryption key (critical for data access)
- `server.crt`/`server.key`: SSL certificates for HTTPS

## Application Routes

- `/`: Patient creation form (requires login)
- `/patients`: User's patient list (user-specific)
- `/preview_id`: AJAX endpoint for ID preview
- `/auth/login`: Authentication endpoint
- `/auth/logout`: Logout endpoint
- `/admin/dashboard`: Admin interface (admin only)
- `/admin/users`: User management (admin only)
- `/admin/users/create`: User creation (admin only)
- `/admin/users/<id>/edit`: User editing (admin only)

## Migration Notes

This codebase has been refactored from a flat file structure to a modular Flask application. Key improvements:

1. **Separation of Concerns**: Models, views, forms, and utilities are now in separate modules
2. **Application Factory**: Supports multiple configurations and testing
3. **Blueprints**: Routes are organized by functionality
4. **Centralized Configuration**: All settings in `app/config.py`
5. **Organized Scripts**: Management and migration scripts in dedicated directories
6. **Proper Testing**: Test files organized by functionality