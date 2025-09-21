#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('instance/oncocentre.db')
cursor = conn.cursor()

# Get table schema
cursor.execute("PRAGMA table_info(user)")
columns = cursor.fetchall()

print("User table schema:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close()