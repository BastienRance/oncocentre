#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('instance/oncocentre.db')
cursor = conn.cursor()

cursor.execute("SELECT id, username, password_hash, is_active, is_admin, is_principal_investigator, auth_source FROM user")
users = cursor.fetchall()

print("Users in database:")
print("ID | Username | Has Password | Active | Admin | PI | Auth Source")
print("-" * 70)

for user in users:
    user_id, username, password_hash, is_active, is_admin, is_pi, auth_source = user
    has_password = "Yes" if password_hash else "No"
    print(f"{user_id:2} | {username:12} | {has_password:12} | {bool(is_active):6} | {bool(is_admin):5} | {bool(is_pi):2} | {auth_source or 'local'}")

conn.close()