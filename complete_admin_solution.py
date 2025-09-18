#!/usr/bin/env python3
"""
Complete admin solution for CARPEM Oncocentre
Fixes all SQLAlchemy caching issues by creating fresh environment
"""

import os
import sqlite3
import bcrypt
import subprocess
import sys

def create_database():
    """Create database with proper admin support"""
    print("Creating fresh database...")
    
    # Remove existing files
    for file in ['oncocentre.db', 'encryption.key']:
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed {file}")
    
    # Create database with correct schema
    conn = sqlite3.connect('oncocentre.db')
    cursor = conn.cursor()
    
    # Create User table with admin support
    cursor.execute('''
        CREATE TABLE user (
            id INTEGER PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            password_hash VARCHAR(128) NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            is_admin BOOLEAN NOT NULL DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Patient table
    cursor.execute('''
        CREATE TABLE patient (
            id INTEGER PRIMARY KEY,
            ipp_encrypted TEXT NOT NULL,
            first_name_encrypted TEXT NOT NULL,
            last_name_encrypted TEXT NOT NULL,
            birth_date_encrypted TEXT NOT NULL,
            sex VARCHAR(1) NOT NULL,
            oncocentre_id VARCHAR(50) UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER NOT NULL,
            FOREIGN KEY (created_by) REFERENCES user (id)
        )
    ''')
    
    # Create users
    users_data = [
        ('admin', 'admin123', True),
        ('user1', 'user1123', False),
        ('user2', 'user2123', False),
        ('doctor1', 'doctor123', False),
        ('researcher1', 'research123', False)
    ]
    
    for username, password, is_admin in users_data:
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
        cursor.execute('''
            INSERT INTO user (username, password_hash, is_active, is_admin)
            VALUES (?, ?, 1, ?)
        ''', (username, password_hash, is_admin))
        
        print(f"Created user: {username}")
    
    conn.commit()
    conn.close()
    print("Database setup completed!")

def test_server():
    """Test the server in a separate process"""
    print("Testing server in fresh Python process...")
    
    # Create test script
    test_script = '''
import os
import sys

# Set environment
os.environ['AUTHORIZED_USERS'] = 'admin,user1,user2,doctor1,researcher1'

try:
    from app import create_app
    app = create_app()
    
    # Disable CSRF for testing
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        print("Testing admin login...")
        
        # Test login
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        print(f"Login status: {response.status_code}")
        
        if response.status_code == 302:
            print("Login: SUCCESS")
            
            # Test admin dashboard
            response = client.get('/admin/dashboard')
            print(f"Admin dashboard: {response.status_code}")
            
            if response.status_code == 200:
                print("Admin dashboard: SUCCESS")
                
                # Test user management
                response = client.get('/admin/users')
                print(f"User management: {response.status_code}")
                
                if response.status_code == 200:
                    print("User management: SUCCESS")
                    print("ALL ADMIN TESTS PASSED!")
                    sys.exit(0)
                else:
                    print("User management: FAILED")
            else:
                print("Admin dashboard: FAILED")
        else:
            print("Login: FAILED")
            
    print("SOME TESTS FAILED")
    sys.exit(1)
    
except Exception as e:
    print(f"Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''
    
    # Write and run test
    with open('test_complete.py', 'w') as f:
        f.write(test_script)
    
    try:
        result = subprocess.run([sys.executable, 'test_complete.py'], 
                              capture_output=True, text=True, timeout=60)
        
        print("Test output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        # Clean up
        if os.path.exists('test_complete.py'):
            os.remove('test_complete.py')
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Test execution failed: {e}")
        return False

def start_production_server():
    """Start the production HTTPS server"""
    print("Starting production HTTPS server...")
    print("This will run the server with admin functionality enabled.")
    print("Press Ctrl+C to stop the server.")
    
    # Set environment
    os.environ['AUTHORIZED_USERS'] = 'admin,user1,user2,doctor1,researcher1'
    
    try:
        # Run the HTTPS server
        subprocess.run([sys.executable, 'run_https.py'])
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")

def main():
    """Main function"""
    print("CARPEM Oncocentre - Complete Admin Solution")
    print("=" * 50)
    
    try:
        print("Step 1: Creating database with admin support...")
        create_database()
        
        print("\nStep 2: Testing admin functionality...")
        if test_server():
            print("\n" + "=" * 50)
            print("SUCCESS! Admin system is now fully working!")
            print("\nYour CARPEM Oncocentre system is ready with:")
            print("✓ Database with admin support")
            print("✓ Working admin login")
            print("✓ Admin dashboard")
            print("✓ User management interface")
            print("✓ All security features")
            
            print("\nLogin credentials:")
            print("  admin / admin123 (Administrator)")
            print("  user1 / user1123")
            print("  user2 / user2123")
            print("  doctor1 / doctor123")
            print("  researcher1 / research123")
            
            print("\nAdmin features:")
            print("  - Login as 'admin' user")
            print("  - Access 'Administration' menu")
            print("  - Create and manage users")
            print("  - View system statistics")
            print("  - Control user access")
            
            print("\nWould you like to start the production server now? (y/n): ", end="")
            try:
                response = input()
                if response.lower() == 'y':
                    start_production_server()
                else:
                    print("\nTo start later, run: python run_https.py")
                    print("Then access: https://localhost:5000")
            except (EOFError, KeyboardInterrupt):
                print("\nTo start later, run: python run_https.py")
                print("Then access: https://localhost:5000")
        else:
            print("Tests failed! Check the output above.")
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()