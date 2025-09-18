# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CARPEM Oncocentre is a Flask web application for managing patient identifier creation and access for the CARPEM biological data collection. The application generates unique identifiers following the format `ONCOCENTRE_YYYY_NNNNN` and provides a patient registry.

## Development Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create initial users and admin:
   ```bash
   python create_test_users.py
   python make_admin.py admin
   ```

3. Run the application (HTTP):
   ```bash
   python app.py
   ```

4. Run the secure application (HTTPS):
   ```bash
   python run_https.py
   ```

The application will be available at `http://localhost:5000` or `https://localhost:5000` (secure)

## Architecture Overview

The application follows a modular Flask structure:

- `app.py`: Application factory and main entry point
- `models.py`: SQLAlchemy database models (User and Patient tables)
- `routes.py`: Main Flask routes for patient management
- `auth.py`: Authentication routes and user login system
- `admin.py`: Administrator routes for user management
- `forms.py`: WTForms for validation and CSRF protection
- `utils.py`: Utility functions for ID generation and validation
- `templates/`: Jinja2 HTML templates with CARPEM branding
  - `templates/admin/`: Admin interface templates
- `static/`: CSS and JavaScript assets

### Key Features

- **User Authentication**: Secure login system with password hashing
- **Patient Registration**: Form to create new patient records with IPP, name, birth date, and sex
- **Live ID Preview**: Real-time preview of the next oncocentre identifier 
- **Patient Listing**: Table view of all registered patients (user-specific)
- **Admin User Management**: Create, edit, delete users with role-based access
- **Data Encryption**: Sensitive patient data encrypted at rest
- **HTTPS Support**: Secure communication with SSL/TLS
- **CARPEM Branding**: Styled with official CARPEM colors (#009ee0 blue, #ec2849 pink)

### Database Schema

SQLite database with `User` and `Patient` tables:

**User Table:**
- `id`: Primary key
- `username`: Unique username (required)
- `password_hash`: Bcrypt hashed password
- `is_active`: Boolean for account status
- `is_admin`: Boolean for admin privileges
- `created_at`: Timestamp

**Patient Table:**
- `id`: Primary key
- `ipp_encrypted`: Encrypted patient identifier
- `first_name_encrypted`, `last_name_encrypted`: Encrypted patient names
- `birth_date_encrypted`: Encrypted date of birth
- `sex`: M or F (not encrypted)
- `oncocentre_id`: Generated unique identifier (ONCOCENTRE_YYYY_NNNNN)
- `created_by`: Foreign key to User table
- `created_at`: Timestamp

## Common Commands

### Development Commands
- Start development server: `python app.py`
- Start secure HTTPS server: `python run_https.py`
- Create test users: `python create_test_users.py`
- Make user admin: `python make_admin.py <username>`

### Database Management
- Reset database: `python reset_database.py`
- Migrate database: `python migrate_database.py`
- Check database schema: `python check_database.py`

### Testing
- Run security tests: `python test_security_fixed.py`
- Test login functionality: `python test_simple_login.py`
- Test admin functionality: `python ADMIN_SETUP_COMPLETE.py`

### Application Access
- Main application: `/` (requires login)
- Patient list: `/patients` (user-specific)
- Admin dashboard: `/admin/dashboard` (admin only)
- Login page: `/auth/login`