#!/usr/bin/env python3
"""
Database migration utilities
"""

import os
import sys
import sqlite3
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.models import db, User

def migrate_database():
    """Migrate existing database to add admin features"""
    print("Database Migration - Adding Admin Column")
    print("=" * 40)
    
    app = create_app('development')
    
    with app.app_context():
        try:
            # Check if is_admin column exists
            conn = sqlite3.connect('instance/oncocentre.db')
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(user)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'is_admin' not in columns:
                print("Adding is_admin column to user table...")
                cursor.execute("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0 NOT NULL")
                conn.commit()
                print("✅ Column added successfully!")
            else:
                print("Column 'is_admin' already exists.")
            
            conn.close()
            
            # Verify admin user exists
            admin_user = User.query.filter_by(username='admin').first()
            if admin_user:
                admin_user.is_admin = True
                db.session.commit()
                print("✅ Admin user updated successfully!")
            else:
                print("⚠️  Admin user not found.")
            
            print("Migration completed successfully!")
            return True
            
        except Exception as e:
            print(f"ERROR: Migration failed: {e}")
            return False

if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)