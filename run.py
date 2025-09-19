#!/usr/bin/env python3
"""
Main entry point for the CARPEM Oncocentre application
"""

import os
from app import create_app

# Get configuration from environment
config_name = os.getenv('FLASK_CONFIG', 'development')

# Create application instance
app = create_app(config_name)

if __name__ == '__main__':
    # Development server
    app.run(debug=True, host='127.0.0.1', port=5000)