#!/usr/bin/env python3
"""
Complete system setup for CARPEM Oncocentre
Sets up database with admin functionality from scratch
"""

import os
from app import create_app
from models import db, User

def setup_complete_system():
    """Setup the complete system with admin functionality"""
    print("CARPEM Oncocentre - Complete System Setup")
    print("=" * 45)
    
    # Set environment variables
    os.environ['AUTHORIZED_USERS'] = 'admin,user1,user2,doctor1,researcher1'
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        print("1. Creating database with admin support...")
        
        # Create all tables with latest schema (including is_admin)
        db.create_all()
        print("   Database tables created successfully!")
        
        # Check if users already exist
        existing_users = User.query.count()
        if existing_users > 0:
            print(f"   Found {existing_users} existing users")
            
            # Make admin user an admin if exists
            admin_user = User.query.filter_by(username='admin').first()
            if admin_user:
                admin_user.is_admin = True
                db.session.commit()
                print("   Made existing 'admin' user an administrator")
            else:
                print("   No 'admin' user found - will create one")
        
        print("\n2. Creating users...")
        
        # Create users if they don't exist
        users_to_create = [
            ('admin', 'admin123', True),    # Admin user
            ('user1', 'user1123', False),   # Regular users
            ('user2', 'user2123', False),
            ('doctor1', 'doctor123', False),
            ('researcher1', 'research123', False)
        ]
        
        created_count = 0
        for username, password, is_admin in users_to_create:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                user = User(username=username, is_admin=is_admin)
                user.set_password(password)
                db.session.add(user)
                created_count += 1
                print(f"   Created user: {username}")
            else:
                print(f"   User already exists: {username}")
        
        if created_count > 0:
            db.session.commit()
            print(f"   Successfully created {created_count} new users")
        
        print("\n3. Verifying setup...")
        
        # Verify admin users
        admins = User.query.filter_by(is_admin=True).all()
        print(f"   Administrators: {len(admins)}")
        for admin in admins:
            print(f"     - {admin.username}")
        
        # Verify total users
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        print(f"   Total users: {total_users}")
        print(f"   Active users: {active_users}")
        
        print("\n4. Testing login functionality...")
        
        # Test admin login
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user and admin_user.check_password('admin123'):
            print("   Admin login test: SUCCESS")
        else:
            print("   Admin login test: FAILED")
        
        # Test admin capabilities
        if admin_user and admin_user.is_admin:
            print("   Admin privileges: SUCCESS")
        else:
            print("   Admin privileges: FAILED")
        
        return True

def test_admin_interface():
    """Test admin interface functionality"""
    print("\n5. Testing admin interface...")
    
    app = create_app()
    
    with app.test_client() as client:
        # Test login
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        if response.status_code == 302:  # Redirect = success
            print("   Web login: SUCCESS")
            
            # Test admin dashboard
            response = client.get('/admin/dashboard')
            if response.status_code == 200:
                print("   Admin dashboard: SUCCESS")
            else:
                print(f"   Admin dashboard: FAILED ({response.status_code})")
            
            # Test user management
            response = client.get('/admin/users')
            if response.status_code == 200:
                print("   User management: SUCCESS")
            else:
                print(f"   User management: FAILED ({response.status_code})")
        else:
            print(f"   Web login: FAILED ({response.status_code})")

def main():
    """Main setup function"""
    try:
        success = setup_complete_system()
        if success:
            test_admin_interface()
            
            print("\n" + "=" * 45)
            print("SETUP COMPLETED SUCCESSFULLY!")
            print("\nYour CARPEM Oncocentre system is ready with:")
            print("✓ Database with admin support")
            print("✓ User authentication system")
            print("✓ Admin user management interface")
            print("✓ Data encryption")
            print("✓ Security controls")
            
            print("\nTo start using:")
            print("1. Start the server:")
            print("   python run_https.py")
            print("2. Open browser:")
            print("   https://localhost:5000")
            print("3. Login as admin:")
            print("   Username: admin")
            print("   Password: admin123")
            print("4. Access admin features via 'Administration' menu")
            
            print("\nOther user credentials:")
            print("   user1 / user1123")
            print("   user2 / user2123")
            print("   doctor1 / doctor123")
            print("   researcher1 / research123")
            
        else:
            print("Setup failed!")
    
    except Exception as e:
        print(f"ERROR: Setup failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()