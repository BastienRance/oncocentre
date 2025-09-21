#!/usr/bin/env python3
"""
Fix encryption errors by clearing corrupted patient data
This script removes patient records that cannot be decrypted due to key mismatches
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.core.models import db, Patient
import sqlite3

def fix_encryption_errors():
    """Remove patient records that cannot be decrypted"""
    app = create_app()

    with app.app_context():
        print("Checking for encryption errors in patient data...")

        # Get all patients
        patients = Patient.query.all()
        corrupted_patients = []

        for patient in patients:
            try:
                # Try to access encrypted fields
                _ = patient.ipp
                _ = patient.first_name
                _ = patient.last_name
                _ = patient.birth_date
                print(f"OK Patient {patient.oncocentre_id} - data accessible")
            except Exception as e:
                print(f"ERROR Patient {patient.oncocentre_id} - encryption error: {e}")
                corrupted_patients.append(patient)

        if corrupted_patients:
            print(f"\nFound {len(corrupted_patients)} corrupted patient records")
            print("These records have encryption errors and cannot be accessed")
            print("This typically happens when the encryption key changes")

            response = input("\nRemove corrupted patient records? (y/N): ")
            if response.lower() == 'y':
                for patient in corrupted_patients:
                    print(f"Removing patient {patient.oncocentre_id}")
                    db.session.delete(patient)

                db.session.commit()
                print(f"Removed {len(corrupted_patients)} corrupted patient records")
                print("The application should now work correctly")
            else:
                print("Keeping corrupted records - patient list will continue to show errors")
        else:
            print("No encryption errors found - all patient data is accessible")

if __name__ == '__main__':
    fix_encryption_errors()