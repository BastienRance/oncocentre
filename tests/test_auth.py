#!/usr/bin/env python3
"""
Authentication tests for the CARPEM Oncocentre application
"""

import os
import sys
import requests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_user_login(base_url="http://127.0.0.1:5000", username="user1", password="user1123"):
    """Test user login functionality"""
    print(f"🧪 Testing login for {username}")
    print("=" * 40)
    
    session = requests.Session()
    
    try:
        # Test login
        login_url = f"{base_url}/auth/login"
        login_page = session.get(login_url)
        
        if login_page.status_code != 200:
            print(f"❌ Failed to access login page: {login_page.status_code}")
            return False
        
        # Extract CSRF token
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(login_page.content, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        
        if not csrf_token:
            print("❌ Could not find CSRF token")
            return False
        
        # Submit login
        login_data = {
            'username': username,
            'password': password,
            'csrf_token': csrf_token.get('value')
        }
        
        login_response = session.post(login_url, data=login_data, allow_redirects=False)
        
        if login_response.status_code == 302:
            print(f"✅ Login successful for {username}")
            return True
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return False

def test_unauthorized_access(base_url="http://127.0.0.1:5000"):
    """Test that unauthorized users cannot access protected pages"""
    print("🧪 Testing unauthorized access protection")
    print("=" * 40)
    
    session = requests.Session()
    
    # Test accessing main page without login
    main_response = session.get(f"{base_url}/")
    
    if main_response.status_code == 302:
        print("✅ Unauthorized access properly redirected")
        return True
    else:
        print(f"❌ Unauthorized access not blocked: {main_response.status_code}")
        return False

if __name__ == "__main__":
    # Install beautifulsoup4 if needed
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4"])
        from bs4 import BeautifulSoup
    
    print("🧪 CARPEM Oncocentre Authentication Tests")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Test unauthorized access
    total_tests += 1
    if test_unauthorized_access():
        tests_passed += 1
    
    # Test user login
    total_tests += 1
    if test_user_login():
        tests_passed += 1
    
    print(f"\n📊 Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ All authentication tests passed!")
        sys.exit(0)
    else:
        print("❌ Some authentication tests failed!")
        sys.exit(1)