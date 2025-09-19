#!/usr/bin/env python3
"""
HTTPS Configuration Script for CARPEM Oncocentre
This script sets up and runs the application with HTTPS/TLS encryption.
"""

import ssl
import os
from app import create_app

def generate_self_signed_cert():
    """Generate self-signed certificate for development/testing"""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import datetime
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Create certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "FR"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Ile-de-France"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Paris"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "CARPEM"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("127.0.0.1"),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Write certificate and key files
        with open("server.crt", "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        with open("server.key", "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
            
        print("✓ Self-signed certificate generated: server.crt, server.key")
        return True
        
    except ImportError:
        print("✗ Cannot generate certificate: cryptography package required")
        print("  Run: pip install cryptography")
        return False
    except Exception as e:
        print(f"✗ Error generating certificate: {e}")
        return False

def setup_https():
    """Setup HTTPS configuration"""
    cert_file = "server.crt"
    key_file = "server.key"
    
    # Check if certificate files exist
    if not (os.path.exists(cert_file) and os.path.exists(key_file)):
        print("📋 Certificate files not found. Generating self-signed certificate...")
        if not generate_self_signed_cert():
            return None
    
    # Create SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    try:
        context.load_cert_chain(cert_file, key_file)
        print(f"✓ SSL certificate loaded: {cert_file}")
        return context
    except Exception as e:
        print(f"✗ Error loading SSL certificate: {e}")
        return None

def main():
    """Main function to run the application with HTTPS"""
    print("🔐 CARPEM Oncocentre - HTTPS Setup")
    print("=" * 40)
    
    # Set environment variables for production security
    os.environ.setdefault('SECRET_KEY', os.urandom(32).hex())
    os.environ.setdefault('AUTHORIZED_USERS', 'admin,user1,user2,doctor1,researcher1')  # Configure as needed
    
    # Create Flask app
    app = create_app()
    
    # Additional security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net"
        return response
    
    # Setup HTTPS
    ssl_context = setup_https()
    if ssl_context is None:
        print("✗ Failed to setup HTTPS. Exiting.")
        return
    
    print("\n🚀 Starting CARPEM Oncocentre with HTTPS...")
    print("📍 Access the application at: https://localhost:5000")
    print("📍 Login with authorized credentials")
    print("\n⚠️  Security Notes:")
    print("   - Change default passwords in production")
    print("   - Use proper SSL certificates in production")
    print("   - Configure firewall and access controls")
    print("   - Regularly update encryption keys")
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,  # Disable debug in production
            ssl_context=ssl_context
        )
    except KeyboardInterrupt:
        print("\n👋 Application stopped.")
    except Exception as e:
        print(f"\n✗ Error running application: {e}")

if __name__ == '__main__':
    main()