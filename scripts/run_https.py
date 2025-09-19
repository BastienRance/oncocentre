#!/usr/bin/env python3
"""
HTTPS server for the CARPEM Oncocentre application
"""

import os
import ssl
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app

def create_ssl_context():
    """Create SSL context with self-signed certificates"""
    import subprocess
    import tempfile
    
    cert_file = 'server.crt'
    key_file = 'server.key'
    
    # Generate self-signed certificate if it doesn't exist
    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        print("Generating self-signed SSL certificate...")
        subprocess.run([
            'openssl', 'req', '-x509', '-newkey', 'rsa:4096', '-nodes',
            '-out', cert_file, '-keyout', key_file, '-days', '365',
            '-subj', '/C=FR/ST=IDF/L=Paris/O=CARPEM/OU=Oncocentre/CN=localhost'
        ], check=True)
        print(f"SSL certificate created: {cert_file}, {key_file}")
    
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert_file, key_file)
    return context

if __name__ == '__main__':
    # Create application
    app = create_app('production')
    
    # Set up SSL context
    ssl_context = create_ssl_context()
    
    print("Starting CARPEM Oncocentre HTTPS server...")
    print("Access the application at: https://localhost:5000")
    print("Login with: admin / admin123 (change in production)")
    
    # Run HTTPS server
    app.run(
        host='0.0.0.0',
        port=5000,
        ssl_context=ssl_context,
        debug=False
    )