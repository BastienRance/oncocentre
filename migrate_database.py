#!/usr/bin/env python3
"""
Database migration script for CARPEM Oncocentre
Adds the is_admin column to the User table
"""

import sqlite3
from app import create_app
from models import db, User

def migrate_database():
    """Add is_admin column to User table"""
    print("Database Migration - Adding Admin Column")
    print("=" * 40)
    
    try:
        # Direct SQLite connection to add column
        conn = sqlite3.connect('oncocentre.db')
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_admin' in columns:
            print("Column 'is_admin' already exists.")
        else:
            print("Adding 'is_admin' column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0 NOT NULL")
            conn.commit()
            print("SUCCESS: Column added successfully!")
        
        conn.close()
        
        # Now use SQLAlchemy to make admin user an admin
        app = create_app()
        with app.app_context():
            admin_user = User.query.filter_by(username='admin').first()
            if admin_user:
                admin_user.is_admin = True
                db.session.commit()
                print(f"SUCCESS: User 'admin' is now an administrator!")
            else:
                print("WARNING: User 'admin' not found.")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Migration failed: {e}")
        return False

def verify_migration():
    """Verify the migration was successful"""
    print("\nVerifying migration...")
    
    app = create_app()
    with app.app_context():
        # Check if we can query admin users
        try:
            admins = User.query.filter_by(is_admin=True).all()
            print(f"SUCCESS: Found {len(admins)} administrator(s):")
            for admin in admins:
                print(f"  - {admin.username}")
            return True
        except Exception as e:
            print(f"ERROR: Verification failed: {e}")
            return False

def main():
    """Main migration function"""
    success = migrate_database()
    if success:
        verify_migration()
        print("\n" + "=" * 40)
        print("Migration completed successfully!")
        print("You can now use admin features with user 'admin'")
    else:
        print("\nMigration failed!")

if __name__ == '__main__':
    main()