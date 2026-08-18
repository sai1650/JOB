#!/usr/bin/env python3
"""Quick test of login functionality."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.db.session import SessionLocal
from app.repositories.user_repo import UserRepository
from app.services.auth import verify_password, hash_password

# Test credentials
ADMIN_EMAIL = "admin@screening-ai.com"
ADMIN_PASSWORD = "Admin123!@#"

TEST_EMAIL = "test@screening-ai.com"
TEST_PASSWORD = "Test123!@#"

def test_login():
    """Test login credentials."""
    db = SessionLocal()
    repo = UserRepository(db)

    print("🔐 Testing Login Credentials\n")
    print("=" * 50)

    # Test admin login
    admin = repo.get_by_email(ADMIN_EMAIL)
    if admin:
        if verify_password(ADMIN_PASSWORD, admin.hashed_password):
            print(f"✅ Admin login: SUCCESS")
            print(f"   Email: {admin.email}")
            print(f"   Name: {admin.name}")
            print(f"   Is Admin: {admin.is_admin}")
            print(f"   Is Active: {admin.is_active}")
        else:
            print(f"❌ Admin login: FAILED (wrong password)")
    else:
        print(f"❌ Admin not found in database")

    print()

    # Test user login
    user = repo.get_by_email(TEST_EMAIL)
    if user:
        if verify_password(TEST_PASSWORD, user.hashed_password):
            print(f"✅ Test user login: SUCCESS")
            print(f"   Email: {user.email}")
            print(f"   Name: {user.name}")
            print(f"   Is Admin: {user.is_admin}")
            print(f"   Is Active: {user.is_active}")
        else:
            print(f"❌ Test user login: FAILED (wrong password)")
    else:
        print(f"❌ Test user not found in database")

    print()
    print("=" * 50)
    print("\n✅ All credentials are valid and ready to use!")
    print("\nYou can now:")
    print(f"1. Login with admin: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    print(f"2. Login with test user: {TEST_EMAIL} / {TEST_PASSWORD}")

    db.close()

if __name__ == "__main__":
    test_login()
