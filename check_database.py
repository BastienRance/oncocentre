#!/usr/bin/env python3
"""
Check database schema and tables
"""

import sqlite3
import os

def check_database():
    """Check database schema"""
    db_path = 'oncocentre.db'
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} does not exist!")
        return
    
    print(f"Checking database: {db_path}")
    print("=" * 30)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("Tables found:")
    for table in tables:
        table_name = table[0]
        print(f"\nTable: {table_name}")
        
        # Get column info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print("Columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'} {'DEFAULT ' + str(col[4]) if col[4] else ''}")
    
    conn.close()

if __name__ == '__main__':
    check_database()