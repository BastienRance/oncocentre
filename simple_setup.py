#!/usr/bin/env python3
"""
Simple setup for CARPEM Oncocentre with admin features
Creates database and users from scratch
"""

import os
import sys

def setup_system():
    """Setup system from scratch"""
    print("CARPEM Oncocentre - Simple Setup")
    print("=" * 35)
    
    # Remove old database files
    for file in ['oncocentre.db', 'encryption.key']:
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed {file}")
    
    # Set environment
    os.environ['AUTHORIZED_USERS'] = 'admin,user1,user2,doctor1,researcher1'
    print("Environment configured")
    
    # Import after cleaning database
    from app import create_app
    from models import db, User
    
    app = create_app()
    
    with app.app_context():
        print("\n1. Creating fresh database...")
        db.create_all()
        
        print("2. Creating users...")
        
        # Create admin user
        admin = User(username='admin', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        print("   Created admin user")
        
        # Create regular users
        users = [
            ('user1', 'user1123'),
            ('user2', 'user2123'), 
            ('doctor1', 'doctor123'),
            ('researcher1', 'research123')
        ]
        
        for username, password in users:
            user = User(username=username, is_admin=False)
            user.set_password(password)
            db.session.add(user)
            print(f"   Created user: {username}")
        
        db.session.commit()
        print("   All users committed to database")
        
        print("\n3. Verifying setup...")
        
        # Check admin
        admin_check = User.query.filter_by(username='admin').first()
        if admin_check and admin_check.is_admin:
            print("   Admin user: OK")
        else:
            print("   Admin user: FAILED")
            return False
        
        # Check total users
        total = User.query.count()
        print(f"   Total users: {total}")
        
        # Test login
        if admin_check.check_password('admin123'):
            print("   Admin password: OK")
        else:
            print("   Admin password: FAILED")
            return False
        
        return True

def test_web_interface():
    """Test web interface"""
    print("\n4. Testing web interface...")
    
    from app import create_app
    app = create_app()
    
    with app.test_client() as client:
        # Test login
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        if response.status_code == 302:
            print("   Login: SUCCESS")
            
            # Test admin dashboard
            response = client.get('/admin/dashboard')
            if response.status_code == 200:
                print("   Admin dashboard: SUCCESS")
                return True
            else:
                print(f"   Admin dashboard: FAILED ({response.status_code})")
        else:
            print(f"   Login: FAILED ({response.status_code})")
    
    return False

def main():
    """Main function"""
    try:
        if setup_system():
            if test_web_interface():
                print("\n" + "=" * 35)
                print("SUCCESS: Setup completed!")
                print("\nYour system is ready!")
                print("\nTo start:")
                print("  python run_https.py")
                print("\nLogin at https://localhost:5000")
                print("  Username: admin")
                print("  Password: admin123")
                print("\nAdmin features available via 'Administration' menu")
                
                print("\nAll user credentials:")
                print("  admin / admin123 (Administrator)")
                print("  user1 / user1123")
                print("  user2 / user2123")
                print("  doctor1 / doctor123") 
                print("  researcher1 / research123")
            else:
                print("Web interface test failed")
        else:
            print("Setup failed")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()