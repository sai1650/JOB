#!/usr/bin/env python3
"""Seed default users into the database."""

import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db.session import SessionLocal
from app.repositories.user_repo import UserRepository
from app.core.config import settings

def seed_users():
    """Create default users if they don't exist."""
    db = SessionLocal()
    repo = UserRepository(db)
    
    try:
        # Create admin user
        admin = repo.get_by_email(settings.ADMIN_EMAIL)
        if not admin:
            admin = repo.create(
                name=settings.ADMIN_NAME,
                email=settings.ADMIN_EMAIL,
                password=settings.ADMIN_PASSWORD,
                is_admin=True,
            )
            print(f"✓ Created admin user: {admin.email}")
        else:
            print(f"✓ Admin user already exists: {admin.email}")
        
        # Create test user
        test_user = repo.get_by_email(settings.TEST_USER_EMAIL)
        if not test_user:
            test_user = repo.create(
                name=settings.TEST_USER_NAME,
                email=settings.TEST_USER_EMAIL,
                password=settings.TEST_USER_PASSWORD,
                is_admin=False,
            )
            print(f"✓ Created test user: {test_user.email}")
        else:
            print(f"✓ Test user already exists: {test_user.email}")
        
        print("\n✓ Database seeding completed successfully!")
        print("\nLogin credentials:")
        print(f"  Admin: {settings.ADMIN_EMAIL} / {settings.ADMIN_PASSWORD}")
        print(f"  Test:  {settings.TEST_USER_EMAIL} / {settings.TEST_USER_PASSWORD}")
        
    except Exception as e:
        print(f"✗ Error seeding database: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
