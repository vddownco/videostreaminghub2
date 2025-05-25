#!/usr/bin/env python3
"""
Debug script to test user login directly.
"""

import sys
import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
import traceback

# Add the project root to the Python path
sys.path.append('.')

# Import our app modules
from app.database.database import Base
from app.database.models import User
from app.utils.auth import verify_password, get_user, authenticate_user

# Database setup
DATABASE_PATH = "./data/videohub.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def print_all_users():
    """Print all users in the database."""
    db = SessionLocal()
    users = db.query(User).all()
    
    print(f"\nAll users in database ({len(users)}):")
    for user in users:
        print(f"  - ID: {user.id}, Username: {user.username}, Email: {user.email}")
        # Print first 10 chars of hashed_password to check format
        if hasattr(user, 'hashed_password') and user.hashed_password:
            hash_preview = user.hashed_password[:20] + "..." if len(user.hashed_password) > 20 else user.hashed_password
            print(f"    Password hash: {hash_preview}")
        else:
            print("    No password hash found!")
    
    db.close()

def test_login(username, password):
    """Test logging in with the given credentials."""
    print(f"\nTesting login for user: {username}")
    
    try:
        db = SessionLocal()
        
        # Get the user
        user = get_user(db, username)
        
        if not user:
            print(f"Error: User '{username}' not found in database.")
            return
        
        print(f"Found user: {user.username}, Email: {user.email}")
        
        # Test password verification
        if hasattr(user, 'hashed_password') and user.hashed_password:
            print(f"Stored password hash: {user.hashed_password[:20]}...")
            
            # Manual verification
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            manual_verify = pwd_context.verify(password, user.hashed_password)
            print(f"Manual password verification: {manual_verify}")
            
            # Using authenticate_user function
            auth_result = authenticate_user(db, username, password)
            print(f"authenticate_user result: {bool(auth_result)}")
            
            if not auth_result:
                print("Authentication failed. The password doesn't match the stored hash.")
            else:
                print("Authentication successful!")
        else:
            print("Error: No password hash found for this user!")
        
        db.close()
        
    except Exception as e:
        print(f"Error during login test: {str(e)}")
        traceback.print_exc()

def main():
    """Main function to run tests."""
    try:
        # Print all users
        print_all_users()
        
        # Test with admin user
        test_login("admin", "admin")
        
        # Test with test user
        test_login("test", "test")
        
        # Test with newly registered user if specified
        if len(sys.argv) > 2:
            username = sys.argv[1]
            password = sys.argv[2]
            test_login(username, password)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 