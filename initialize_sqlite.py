#!/usr/bin/env python3
"""
Database initialization script using SQLite explicitly.
Creates all tables and adds a default admin user.
"""

import os
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
import traceback

# Add the project root to the Python path
sys.path.append('.')

# Import our app modules
from app.database.database import Base
from app.database.models import User
from app.utils.auth import get_password_hash

# Explicitly use SQLite
DATABASE_PATH = "./data/videohub.db"
if os.path.exists(DATABASE_PATH):
    print(f"Removing existing database: {DATABASE_PATH}")
    os.remove(DATABASE_PATH)

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database with all tables and a default admin user."""
    print(f"Initializing SQLite database at: {DATABASE_PATH}")
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully.")
        
        # List all tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Tables in database: {tables}")
        
        # Create a session
        db = SessionLocal()
        
        # Create admin user
        print("Creating admin user...")
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin"),
            full_name="Admin User",
            bio="System administrator",
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        print("Admin user created successfully.")
        
        # Create test user
        print("Creating test user...")
        test_user = User(
            username="test",
            email="test@example.com",
            hashed_password=get_password_hash("test"),
            full_name="Test User",
            bio="Test account",
            is_active=True
        )
        db.add(test_user)
        db.commit()
        print("Test user created successfully.")
        
        # Create directories for static files if they don't exist
        directories = [
            "frontend/static/videos",
            "frontend/static/thumbnails", 
            "frontend/static/profile_pictures",
            "frontend/static/banners"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"Created directory: {directory}")
        
        print("\nDatabase initialization completed successfully.")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nDetailed traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    init_db() 