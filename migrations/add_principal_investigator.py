#!/usr/bin/env python3
"""
Database migration script to add principal investigator field to User table
"""

import sqlite3
import os
import sys
from datetime import datetime

def migrate_database():
    """Add principal investigator field to the User table"""
    
    db_path = 'instance/oncocentre.db'
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if principal investigator field already exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'is_principal_investigator' in columns:
            print("Principal investigator field already exists.")
            print("Migration may have already been run.")
            return True
            
        # Add the field
        cursor.execute('ALTER TABLE user ADD COLUMN is_principal_investigator BOOLEAN DEFAULT 0 NOT NULL')
        print("Added is_principal_investigator field")
        
        # Commit changes
        conn.commit()
        
        print("Migration completed successfully!")
        
        # Verify the migration
        cursor.execute("PRAGMA table_info(user)")
        columns_after = [row[1] for row in cursor.fetchall()]
        print(f"User table now has {len(columns_after)} columns:")
        for col in sorted(columns_after):
            print(f"  - {col}")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        return False

if __name__ == '__main__':
    print("CARPEM Oncocentre - Principal Investigator Field Migration")
    print("=" * 55)
    print(f"Starting migration at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = migrate_database()
    
    if success:
        print("\n✓ Migration completed successfully!")
        sys.exit(0)
    else:
        print("\n✗ Migration failed!")
        sys.exit(1)