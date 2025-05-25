#!/usr/bin/env python3
"""
Debug script to test user registration directly without going through the API.
This will help identify issues in the user creation process.
"""

import os
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
import traceback

# Add the project root to the Python path
sys.path.append('.')

# Import our app modules
from app.database.database import Base, get_db
from app.database.models import User
from app.utils.auth import get_password_hash

# Database setup - create a fresh database for testing
TEST_DB_PATH = "./data/test_db.db"
if os.path.exists(TEST_DB_PATH):
    os.remove(TEST_DB_PATH)

DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def main():
    print("Creating database tables...")
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully.")
        
        # List all tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Tables in database: {tables}")
        
        # Test user creation
        print("\nTesting user creation...")
        db = SessionLocal()
        
        # Create test user data
        test_user = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
            "full_name": "Test User",
            "bio": "This is a test user"
        }
        
        # Create user object
        hashed_password = get_password_hash(test_user["password"])
        db_user = User(
            username=test_user["username"],
            email=test_user["email"],
            hashed_password=hashed_password,
            full_name=test_user["full_name"],
            bio=test_user["bio"]
        )
        
        # Add to database
        print("Adding user to database...")
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Verify user was created
        created_user = db.query(User).filter(User.username == test_user["username"]).first()
        if created_user:
            print(f"User created successfully: {created_user.username}, {created_user.email}")
        else:
            print("Failed to create user.")
        
        db.close()
        print("\nTest completed successfully.")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nDetailed traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    main() 