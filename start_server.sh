#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Create data directory if it doesn't exist
mkdir -p data

# Create necessary directories
mkdir -p frontend/static/videos
mkdir -p frontend/static/thumbnails
mkdir -p frontend/static/profile_pictures
mkdir -p frontend/static/banners

# Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001