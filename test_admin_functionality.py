#!/usr/bin/env python3
"""
Test admin functionality for CARPEM Oncocentre
"""

import os
from app import create_app
from models import db, User

def test_admin_functionality():
    """Test admin functionality from scratch"""
    print("Testing Admin Functionality")
    print("=" * 30)
    
    # Ensure clean start
    for file in ['oncocentre.db', 'encryption.key']:
        if os.path.exists(file):
            os.remove(file)
    
    # Set environment
    os.environ['AUTHORIZED_USERS'] = 'admin,user1,user2'
    
    app = create_app()
    
    with app.app_context():
        print("1. Creating database...")
        db.create_all()
        
        # Create admin user
        print("2. Creating admin user...")
        admin_user = User(username='admin', is_admin=True)
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        
        # Create regular user
        print("3. Creating regular user...")
        regular_user = User(username='user1', is_admin=False)
        regular_user.set_password('user1123')
        db.session.add(regular_user)
        
        db.session.commit()
        
        print("4. Testing admin functions...")
        
        # Test admin permissions
        print(f"   admin.is_admin: {admin_user.is_admin}")
        print(f"   user1.is_admin: {regular_user.is_admin}")
        
        # Test admin routes with test client
        with app.test_client() as client:
            # Login as admin
            response = client.post('/auth/login', data={
                'username': 'admin',
                'password': 'admin123'
            })
            
            if response.status_code == 302:  # Redirect = success
                print("   Admin login: SUCCESS")
                
                # Test admin dashboard access
                response = client.get('/admin/dashboard')
                if response.status_code == 200:
                    print("   Admin dashboard access: SUCCESS")
                else:
                    print(f"   Admin dashboard access: FAILED ({response.status_code})")
                
                # Test user creation
                response = client.get('/admin/users/create')
                if response.status_code == 200:
                    print("   Admin user creation page: SUCCESS")
                else:
                    print(f"   Admin user creation page: FAILED ({response.status_code})")
                
            else:
                print("   Admin login: FAILED")
        
        # Test regular user permissions
        with app.test_client() as client:
            # Login as regular user
            response = client.post('/auth/login', data={
                'username': 'user1',
                'password': 'user1123'
            })
            
            if response.status_code == 302:  # Redirect = success
                print("   User login: SUCCESS")
                
                # Test admin dashboard access (should fail)
                response = client.get('/admin/dashboard')
                if response.status_code == 403:  # Forbidden
                    print("   Admin access blocked for regular user: SUCCESS")
                else:
                    print(f"   Admin access blocked for regular user: FAILED ({response.status_code})")
            else:
                print("   User login: FAILED")
        
        print("\n5. Testing user creation functionality...")
        
        # Test creating a new user through admin interface
        with app.test_client() as client:
            # Login as admin
            client.post('/auth/login', data={
                'username': 'admin',
                'password': 'admin123'
            })
            
            # Create new user
            response = client.post('/admin/users/create', data={
                'username': 'newuser',
                'password': 'newpass123',
                'confirm_password': 'newpass123',
                'is_admin': False
            })
            
            if response.status_code == 302:  # Redirect = success
                print("   User creation through admin: SUCCESS")
                
                # Verify user was created
                new_user = User.query.filter_by(username='newuser').first()
                if new_user:
                    print(f"   New user verification: SUCCESS ({new_user.username})")
                else:
                    print("   New user verification: FAILED")
            else:
                print(f"   User creation through admin: FAILED ({response.status_code})")
        
        return True

def main():
    """Main test function"""
    try:
        success = test_admin_functionality()
        if success:
            print("\n" + "=" * 30)
            print("ADMIN FUNCTIONALITY TEST COMPLETED!")
            print("\nTo use the admin interface:")
            print("1. Start server: python run_https.py")
            print("2. Login: admin / admin123")
            print("3. Use admin menu in navigation")
            print("\nAdmin features:")
            print("- Dashboard with system statistics")
            print("- User management (create/edit/delete)")
            print("- System information")
            print("- Automated authorized user management")
    except Exception as e:
        print(f"TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()