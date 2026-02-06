#!/usr/bin/env python3
"""Create users table and optionally seed a demo user."""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import init_db, SessionLocal
from app.models.db_models import User
from app.auth import get_password_hash


def main():
    print("🔧 Creating users table...")
    
    # Create tables
    init_db()
    print("✅ Users table created")
    
    # Ask if user wants to create a demo account
    create_demo = input("\nCreate a demo user account? (y/n): ").strip().lower()
    
    if create_demo == 'y':
        db = SessionLocal()
        try:
            # Check if demo user exists
            existing = db.query(User).filter(User.email == "demo@example.com").first()
            if existing:
                print("❌ Demo user already exists")
                return
            
            # Create demo user
            demo_user = User(
                email="demo@example.com",
                username="demo",
                hashed_password=get_password_hash("demo123"),
                full_name="Demo User",
                is_active=True
            )
            db.add(demo_user)
            db.commit()
            
            print("\n✅ Demo user created successfully!")
            print("\n📋 Login credentials:")
            print("   Email: demo@example.com")
            print("   Password: demo123")
            print("\n⚠️  Change these credentials in production!")
            
        except Exception as e:
            print(f"\n❌ Error creating demo user: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            db.close()
    else:
        print("\nℹ️  No demo user created. Use the registration page to create your first account.")


if __name__ == "__main__":
    main()
