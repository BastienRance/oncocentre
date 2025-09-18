#!/usr/bin/env python3
"""
Working database migration for CARPEM Oncocentre
This script will properly handle the migration to admin functionality
"""

import sqlite3
import os
import bcrypt

def create_fresh_database():
    """Create a completely fresh database with admin functionality"""
    print("Creating fresh database with admin support...")
    
    # Remove old database
    if os.path.exists('oncocentre.db'):
        os.remove('oncocentre.db')
        print("Removed old database")
    
    # Create connection
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
    
    # Create Patient table with encryption support
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
    
    print("Database tables created successfully")
    
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
    
    print("Database setup completed successfully!")
    return True

def verify_database():
    """Verify the database is working correctly"""
    print("\nVerifying database...")
    
    conn = sqlite3.connect('oncocentre.db')
    cursor = conn.cursor()
    
    # Check users
    cursor.execute("SELECT username, is_admin FROM user")
    users = cursor.fetchall()
    
    print(f"Found {len(users)} users:")
    for username, is_admin in users:
        role = "Admin" if is_admin else "User"
        print(f"  - {username} ({role})")
    
    # Check admin count
    cursor.execute("SELECT COUNT(*) FROM user WHERE is_admin = 1")
    admin_count = cursor.fetchone()[0]
    print(f"Administrators: {admin_count}")
    
    conn.close()
    return True

def test_application():
    """Test that the application works with the new database"""
    print("\nTesting application...")
    
    try:
        # Set environment
        os.environ['AUTHORIZED_USERS'] = 'admin,user1,user2,doctor1,researcher1'
        
        from app import create_app
        from models import User
        
        app = create_app()
        
        with app.app_context():
            # Test that we can query users
            admin_user = User.query.filter_by(username='admin').first()
            if admin_user:
                print(f"✓ Found admin user: {admin_user.username}")
                print(f"✓ Is admin: {admin_user.is_admin}")
                print(f"✓ Password check: {admin_user.check_password('admin123')}")
            else:
                print("✗ Admin user not found")
                return False
            
            # Test web interface
            with app.test_client() as client:
                response = client.post('/auth/login', data={
                    'username': 'admin',
                    'password': 'admin123'
                })
                
                if response.status_code == 302:
                    print("✓ Web login successful")
                    
                    response = client.get('/admin/dashboard')
                    if response.status_code == 200:
                        print("✓ Admin dashboard accessible")
                        return True
                    else:
                        print(f"✗ Admin dashboard failed: {response.status_code}")
                else:
                    print(f"✗ Web login failed: {response.status_code}")
        
        return False
        
    except Exception as e:
        print(f"✗ Application test failed: {e}")
        return False

def main():
    """Main migration function"""
    print("CARPEM Oncocentre - Working Database Migration")
    print("=" * 50)
    
    try:
        # Create fresh database
        if create_fresh_database():
            if verify_database():
                if test_application():
                    print("\n" + "=" * 50)
                    print("MIGRATION COMPLETED SUCCESSFULLY!")
                    print("\nYour CARPEM Oncocentre system is ready!")
                    
                    print("\nTo start the application:")
                    print("  python run_https.py")
                    
                    print("\nAccess at: https://localhost:5000")
                    
                    print("\nLogin credentials:")
                    print("  admin / admin123 (Administrator)")
                    print("  user1 / user1123")
                    print("  user2 / user2123")
                    print("  doctor1 / doctor123")
                    print("  researcher1 / research123")
                    
                    print("\nAdmin features:")
                    print("  - Login as 'admin' user")
                    print("  - Use 'Administration' menu")
                    print("  - Create and manage users")
                    print("  - View system statistics")
                    
                    return True
        
        print("Migration failed!")
        return False
        
    except Exception as e:
        print(f"ERROR: Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    main()