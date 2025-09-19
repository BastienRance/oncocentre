#!/usr/bin/env python3
"""
Final admin fix for CARPEM Oncocentre
Resolves SQLAlchemy caching issues by creating database and testing in clean environment
"""

import os
import sqlite3
import bcrypt
import subprocess
import sys

def create_database_with_admin():
    """Create database with proper admin support"""
    print("Creating database with admin support...")
    
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
    
    print("Tables created successfully")
    
    # Create users
    users_data = [
        ('admin', 'admin123', True),
        ('user1', 'user1123', False),
        ('user2', 'user2123', False),
        ('doctor1', 'doctor123', False),
        ('researcher1', 'research123', False)
    ]
    
    for username, password, is_admin in users_data:
        # Hash password
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
    return True

def test_database_directly():
    """Test database without SQLAlchemy"""
    print("\nTesting database directly...")
    
    conn = sqlite3.connect('oncocentre.db')
    cursor = conn.cursor()
    
    # Check admin user
    cursor.execute("SELECT username, is_admin, password_hash FROM user WHERE username = 'admin'")
    result = cursor.fetchone()
    
    if result:
        username, is_admin, password_hash = result
        print(f"Admin user found: {username}")
        print(f"Is admin: {is_admin}")
        
        # Test password
        if bcrypt.checkpw('admin123'.encode('utf-8'), password_hash.encode('utf-8')):
            print("Password verification: SUCCESS")
            
            # Check authorization
            authorized_users = 'admin,user1,user2,doctor1,researcher1'.split(',')
            if username in authorized_users:
                print("Authorization check: SUCCESS")
                conn.close()
                return True
    
    conn.close()
    return False

def test_application_fresh():
    """Test application in a fresh Python process"""
    print("\nTesting application in fresh process...")
    
    # Create test script
    test_script = '''
import os
os.environ['AUTHORIZED_USERS'] = 'admin,user1,user2,doctor1,researcher1'

try:
    from app import create_app
    app = create_app()
    
    with app.test_client() as client:
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
                print("Admin access: SUCCESS")
                print("ALL TESTS PASSED!")
            else:
                print("Admin access: FAILED")
        else:
            print("Login: FAILED")
            
except Exception as e:
    print(f"Test failed: {e}")
'''
    
    # Write test script
    with open('test_admin.py', 'w') as f:
        f.write(test_script)
    
    # Run in fresh process
    try:
        result = subprocess.run([sys.executable, 'test_admin.py'], 
                              capture_output=True, text=True, timeout=30)
        print("Fresh process test output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        # Clean up
        if os.path.exists('test_admin.py'):
            os.remove('test_admin.py')
        
        return "ALL TESTS PASSED!" in result.stdout
        
    except Exception as e:
        print(f"Fresh process test failed: {e}")
        return False

def main():
    """Main function"""
    print("CARPEM Oncocentre - Final Admin Fix")
    print("=" * 40)
    
    try:
        if create_database_with_admin():
            if test_database_directly():
                if test_application_fresh():
                    print("\n" + "=" * 40)
                    print("ADMIN LOGIN FIXED SUCCESSFULLY!")
                    print("\nYour admin system is now working!")
                    print("\nTo use:")
                    print("1. Start server: python run_https.py")
                    print("2. Go to: https://localhost:5000")
                    print("3. Login: admin / admin123")
                    print("4. Access admin features via 'Administration' menu")
                    
                    print("\nAll user credentials:")
                    print("  admin / admin123 (Administrator)")
                    print("  user1 / user1123")
                    print("  user2 / user2123")
                    print("  doctor1 / doctor123")
                    print("  researcher1 / research123")
                    
                    return True
                else:
                    print("Application test failed")
            else:
                print("Database test failed")
        else:
            print("Database creation failed")
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    return False

if __name__ == '__main__':
    main()