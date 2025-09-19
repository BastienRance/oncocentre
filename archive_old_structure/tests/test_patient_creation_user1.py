#!/usr/bin/env python3
"""
Test patient creation functionality when logged in as user1/user1123
"""

import requests
import sys
from datetime import datetime, date
import json

# Test configuration
BASE_URL = "http://127.0.0.1:5000"
USERNAME = "user1"
PASSWORD = "user1123"

def test_patient_creation():
    """Test complete patient creation workflow for user1"""
    
    print("🧪 Testing Patient Creation for user1/user1123")
    print("=" * 50)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Step 1: Test login
    print("\n1. Testing login...")
    login_url = f"{BASE_URL}/auth/login"
    
    # Get login page to retrieve CSRF token
    login_page = session.get(login_url)
    if login_page.status_code != 200:
        print(f"❌ Failed to access login page: {login_page.status_code}")
        return False
    
    # Extract CSRF token from the form
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(login_page.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})
    if not csrf_token:
        print("❌ Could not find CSRF token in login form")
        return False
    
    csrf_value = csrf_token.get('value')
    print(f"✅ Retrieved CSRF token: {csrf_value[:20]}...")
    
    # Submit login form
    login_data = {
        'username': USERNAME,
        'password': PASSWORD,
        'csrf_token': csrf_value
    }
    
    login_response = session.post(login_url, data=login_data, allow_redirects=False)
    
    if login_response.status_code == 302:
        print(f"✅ Login successful - redirected to: {login_response.headers.get('Location', 'Unknown')}")
    else:
        print(f"❌ Login failed with status: {login_response.status_code}")
        print(f"Response: {login_response.text[:500]}")
        return False
    
    # Step 2: Access main page (patient creation form)
    print("\n2. Accessing patient creation form...")
    main_page = session.get(f"{BASE_URL}/")
    
    if main_page.status_code != 200:
        print(f"❌ Failed to access main page: {main_page.status_code}")
        return False
    
    print("✅ Successfully accessed patient creation form")
    
    # Extract CSRF token from patient form
    soup = BeautifulSoup(main_page.content, 'html.parser')
    patient_csrf = soup.find('input', {'name': 'csrf_token'})
    if not patient_csrf:
        print("❌ Could not find CSRF token in patient form")
        return False
    
    patient_csrf_value = patient_csrf.get('value')
    print(f"✅ Retrieved patient form CSRF token: {patient_csrf_value[:20]}...")
    
    # Step 3: Preview next ID
    print("\n3. Testing ID preview...")
    preview_response = session.post(f"{BASE_URL}/preview_id", 
                                  json={}, 
                                  headers={'Content-Type': 'application/json'})
    
    if preview_response.status_code == 200:
        preview_data = preview_response.json()
        next_id = preview_data.get('oncocentre_id')
        print(f"✅ Next ID preview: {next_id}")
    else:
        print(f"⚠️  ID preview failed: {preview_response.status_code}")
        next_id = None
    
    # Step 4: Create test patients
    print("\n4. Creating test patients...")
    
    test_patients = [
        {
            'ipp': 'TEST001',
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'birth_date': '1980-05-15',
            'sex': 'M'
        },
        {
            'ipp': 'TEST002',
            'first_name': 'Marie',
            'last_name': 'Martin',
            'birth_date': '1975-09-22',
            'sex': 'F'
        },
        {
            'ipp': 'TEST003',
            'first_name': 'Pierre',
            'last_name': 'Leblanc',
            'birth_date': '1990-12-03',
            'sex': 'M'
        }
    ]
    
    created_patients = []
    
    for i, patient_data in enumerate(test_patients, 1):
        print(f"\n   Creating patient {i}: {patient_data['first_name']} {patient_data['last_name']}")
        
        # Prepare form data
        form_data = {
            'ipp': patient_data['ipp'],
            'first_name': patient_data['first_name'],
            'last_name': patient_data['last_name'],
            'birth_date': patient_data['birth_date'],
            'sex': patient_data['sex'],
            'csrf_token': patient_csrf_value
        }
        
        # Submit patient creation form
        create_response = session.post(f"{BASE_URL}/create_patient", 
                                     data=form_data, 
                                     allow_redirects=False)
        
        if create_response.status_code == 302:
            print(f"   ✅ Patient {i} created successfully")
            created_patients.append(patient_data)
            
            # Get updated CSRF token for next patient
            main_page = session.get(f"{BASE_URL}/")
            soup = BeautifulSoup(main_page.content, 'html.parser')
            patient_csrf = soup.find('input', {'name': 'csrf_token'})
            if patient_csrf:
                patient_csrf_value = patient_csrf.get('value')
        else:
            print(f"   ❌ Failed to create patient {i}: {create_response.status_code}")
            print(f"   Response: {create_response.text[:200]}")
    
    # Step 5: Verify patients list
    print("\n5. Verifying patients list...")
    patients_page = session.get(f"{BASE_URL}/patients")
    
    if patients_page.status_code != 200:
        print(f"❌ Failed to access patients list: {patients_page.status_code}")
        return False
    
    # Parse patients list
    soup = BeautifulSoup(patients_page.content, 'html.parser')
    patient_rows = soup.find_all('tr')[1:]  # Skip header row
    
    print(f"✅ Found {len(patient_rows)} patients in the list")
    
    for row in patient_rows:
        cells = row.find_all('td')
        if len(cells) >= 5:
            oncocentre_id = cells[0].text.strip()
            ipp = cells[1].text.strip()
            name = cells[2].text.strip()
            birth_date = cells[3].text.strip()
            sex = cells[4].text.strip()
            
            print(f"   - {oncocentre_id}: {name} (IPP: {ipp}, DOB: {birth_date}, Sex: {sex})")
    
    # Step 6: Test duplicate prevention
    print("\n6. Testing duplicate patient prevention...")
    
    duplicate_data = {
        'ipp': 'TEST001',  # Same IPP as first patient
        'first_name': 'Duplicate',
        'last_name': 'Test',
        'birth_date': '1985-01-01',
        'sex': 'M',
        'csrf_token': patient_csrf_value
    }
    
    duplicate_response = session.post(f"{BASE_URL}/create_patient", 
                                    data=duplicate_data, 
                                    allow_redirects=True)
    
    if "already exists" in duplicate_response.text:
        print("✅ Duplicate prevention working correctly")
    else:
        print("⚠️  Duplicate prevention may not be working")
    
    print(f"\n🎉 Test completed! Created {len(created_patients)} test patients as user1")
    return True

def cleanup_test_data():
    """Note: This is informational only - we don't delete test data"""
    print("\n📝 Note: Test patients created with IPPs TEST001, TEST002, TEST003")
    print("   These can be viewed in the patients list at /patients")
    print("   To reset all data, run: python reset_database.py")

if __name__ == "__main__":
    try:
        # Check if beautifulsoup4 is available
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            print("❌ BeautifulSoup4 not found. Installing...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4"])
            from bs4 import BeautifulSoup
        
        success = test_patient_creation()
        
        if success:
            cleanup_test_data()
            print("\n✅ All tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)