#!/usr/bin/env python3
"""
Test script for dual authentication system (Local + LDAP)
"""

import requests
import sys
from bs4 import BeautifulSoup

BASE_URL = 'http://127.0.0.1:5000'

def test_login_page():
    """Test that login page loads and shows authentication options"""
    print("Testing login page...")
    
    try:
        response = requests.get(f'{BASE_URL}/auth/login')
        if response.status_code != 200:
            print(f"✗ Login page failed to load: {response.status_code}")
            return False
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for authentication method radio buttons
        auth_radios = soup.find_all('input', {'name': 'auth_method', 'type': 'radio'})
        if not auth_radios:
            print("✗ No authentication method options found")
            return False
            
        auth_methods = [radio.get('value') for radio in auth_radios]
        print(f"✓ Authentication methods available: {auth_methods}")
        
        # Check for expected form fields
        username_field = soup.find('input', {'name': 'username'})
        password_field = soup.find('input', {'name': 'password'})
        
        if not username_field or not password_field:
            print("✗ Username or password field missing")
            return False
            
        print("✓ Login form loaded successfully with all fields")
        return True
        
    except Exception as e:
        print(f"✗ Error testing login page: {e}")
        return False

def test_local_authentication():
    """Test local authentication with existing user"""
    print("\nTesting local authentication...")
    
    try:
        # Get login page to extract CSRF token
        session = requests.Session()
        response = session.get(f'{BASE_URL}/auth/login')
        soup = BeautifulSoup(response.content, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        
        # Attempt login with local credentials
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'auth_method': 'local',
            'csrf_token': csrf_token,
            'submit': 'Sign In'
        }
        
        response = session.post(f'{BASE_URL}/auth/login', data=login_data, allow_redirects=False)
        
        if response.status_code == 302:
            print("✓ Local authentication successful (redirected)")
            
            # Follow redirect to check if we're logged in
            location = response.headers.get('Location', '')
            if '/auth/login' not in location:
                print("✓ Successfully logged in via local authentication")
                return True
            else:
                print("✗ Redirected back to login page")
                return False
        else:
            print(f"✗ Local authentication failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing local authentication: {e}")
        return False

def test_ldap_authentication():
    """Test LDAP authentication (will fail but should handle gracefully)"""
    print("\nTesting LDAP authentication...")
    
    try:
        # Get login page to extract CSRF token
        session = requests.Session()
        response = session.get(f'{BASE_URL}/auth/login')
        soup = BeautifulSoup(response.content, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        
        # Attempt login with LDAP method (will fail since no LDAP server configured)
        login_data = {
            'username': 'testuser',
            'password': 'testpass',
            'auth_method': 'ldap',
            'csrf_token': csrf_token,
            'submit': 'Sign In'
        }
        
        response = session.post(f'{BASE_URL}/auth/login', data=login_data)
        
        if 'LDAP authentication failed' in response.text or 'Authentication failed' in response.text:
            print("✓ LDAP authentication handled gracefully (expected failure)")
            return True
        else:
            print("✗ LDAP authentication response unexpected")
            return False
            
    except Exception as e:
        print(f"✗ Error testing LDAP authentication: {e}")
        return False

def test_auto_authentication():
    """Test auto authentication (tries local first)"""
    print("\nTesting auto authentication...")
    
    try:
        # Get login page to extract CSRF token
        session = requests.Session()
        response = session.get(f'{BASE_URL}/auth/login')
        soup = BeautifulSoup(response.content, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        
        # Attempt login with auto method (should try local first)
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'auth_method': 'auto',
            'csrf_token': csrf_token,
            'submit': 'Sign In'
        }
        
        response = session.post(f'{BASE_URL}/auth/login', data=login_data, allow_redirects=False)
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            if '/auth/login' not in location:
                print("✓ Auto authentication successful (local fallback worked)")
                return True
            else:
                print("✗ Auto authentication failed")
                return False
        else:
            print(f"✗ Auto authentication failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing auto authentication: {e}")
        return False

def main():
    """Run all authentication tests"""
    print("CARPEM Oncocentre - Dual Authentication Testing")
    print("=" * 48)
    
    tests = [
        test_login_page,
        test_local_authentication,
        test_ldap_authentication,
        test_auto_authentication
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        
    print(f"\n{'='*48}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All dual authentication tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())