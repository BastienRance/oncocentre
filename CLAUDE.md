# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CARPEM Oncocentre is a Flask web application for managing patient identifier creation and access for the CARPEM biological data collection. The application generates unique identifiers following the format `ONCOCENTRE_YYYY_NNNNN` and provides a patient registry.

## Development Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

## Architecture Overview

The application follows a modular Flask structure:

- `app.py`: Application factory and main entry point
- `models.py`: SQLAlchemy database models (Patient table)
- `routes.py`: Flask routes and request handlers
- `utils.py`: Utility functions for ID generation and validation
- `templates/`: Jinja2 HTML templates with CARPEM branding
- `static/`: CSS and JavaScript assets

### Key Features

- **Patient Registration**: Form to create new patient records with IPP, name, birth date, and sex
- **Live ID Preview**: Real-time preview of the next oncocentre identifier 
- **Patient Listing**: Table view of all registered patients
- **CARPEM Branding**: Styled with official CARPEM colors (#009ee0 blue, #ec2849 pink)

### Database Schema

SQLite database with a single `Patient` table:
- `id`: Primary key
- `ipp`: Patient identifier (required)
- `first_name`, `last_name`: Patient names
- `birth_date`: Date of birth
- `sex`: M or F
- `oncocentre_id`: Generated unique identifier (ONCOCENTRE_YYYY_NNNNN)
- `created_at`: Timestamp

## Common Commands

- Start development server: `python app.py`
- The application automatically creates the SQLite database on first run
- Access forms at `/` and patient list at `/patients`