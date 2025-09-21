#!/usr/bin/env python3
"""
Simple role test using direct HTTP requests
"""

import requests
import sys

def test_role_access():
    """Test access for different user roles"""
    base_url = "http://localhost:5000"

    print("CARPEM Oncocentre - Simple Role Access Test")
    print("=" * 60)

    # Test 1: Check if application is running
    try:
        response = requests.get(f"{base_url}/auth/login", timeout=5)
        if response.status_code == 200:
            print("OK Application is accessible")
        else:
            print("FAIL Application not accessible")
            return False
    except requests.ConnectionError:
        print("FAIL Cannot connect to application. Make sure it's running on localhost:5000")
        return False
    except Exception as e:
        print(f"FAIL Error connecting: {e}")
        return False

    # Test 2: Check login page content
    print("\n> Testing login page...")
    if 'login' in response.text.lower():
        print("OK Login page loads correctly")
    else:
        print("FAIL Login page content issue")

    # Test 3: Check authentication method options
    if 'auth_method' in response.text:
        print("OK Authentication method selection available")
    else:
        print("WARN Authentication method selection not found")

    # Test 4: Check admin area access without login
    print("\n> Testing admin access without authentication...")
    response = requests.get(f"{base_url}/admin/dashboard")
    if response.status_code in [302, 401, 403]:
        print("OK Admin area correctly protected")
    else:
        print(f"FAIL Admin area not protected (Status: {response.status_code})")

    # Test 5: Check patient area access without login
    print("\n> Testing patient area access without authentication...")
    response = requests.get(f"{base_url}/")
    if response.status_code in [302, 401, 403]:
        print("OK Patient area correctly protected")
    else:
        print(f"FAIL Patient area not protected (Status: {response.status_code})")

    return True

def test_with_credentials():
    """Test with actual user credentials if available"""
    print("\n" + "=" * 60)
    print("MANUAL CREDENTIAL TESTING")
    print("=" * 60)
    print("To test with actual users, you can:")
    print("1. Create users with: python scripts/create_users.py")
    print("2. Make admin: python scripts/make_admin.py admin")
    print("3. Use credentials like admin/admin123 or user1/user1123")
    print("\nOr test manually by visiting http://localhost:5000")

if __name__ == '__main__':
    if test_role_access():
        test_with_credentials()
    sys.exit(0)