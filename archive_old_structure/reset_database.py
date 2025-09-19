#!/usr/bin/env python3
"""
Reset database with admin functionality
"""

import os
from app import create_app
from models import db, User

def reset_database():
    """Reset the database and create initial admin user"""
    print("Resetting Database with Admin Support")
    print("=" * 40)
    
    # Remove existing database
    if os.path.exists('oncocentre.db'):
        os.remove('oncocentre.db')
        print("Removed existing database")
    
    # Create new database with updated schema
    app = create_app()
    with app.app_context():
        print("Creating new database...")
        db.create_all()
        
        # Create admin user
        admin_user = User(username='admin', is_admin=True)
        admin_user.set_password('admin123')
        
        # Create other test users
        test_users = [
            ('user1', 'user1123', False),
            ('user2', 'user2123', False),
            ('doctor1', 'doctor123', False),
            ('researcher1', 'research123', False)
        ]
        
        db.session.add(admin_user)
        
        for username, password, is_admin in test_users:
            user = User(username=username, is_admin=is_admin)
            user.set_password(password)
            db.session.add(user)
        
        try:
            db.session.commit()
            print("SUCCESS: Database created with admin support!")
            print("\nCreated users:")
            print("- admin / admin123 (Administrator)")
            for username, password, _ in test_users:
                print(f"- {username} / {password}")
            
            # Update authorized users environment
            import admin
            admin.update_authorized_users_env()
            
        except Exception as e:
            db.session.rollback()
            print(f"ERROR: Failed to create users: {e}")

def main():
    """Main function"""
    print("This will reset the entire database!")
    response = input("Are you sure? (yes/no): ")
    
    if response.lower() == 'yes':
        reset_database()
        print("\nDatabase reset complete!")
        print("You can now test admin functionality:")
        print("1. Start the server: python run_https.py")
        print("2. Login as: admin / admin123")
        print("3. Access admin features from the navigation menu")
    else:
        print("Operation cancelled.")

if __name__ == '__main__':
    main()