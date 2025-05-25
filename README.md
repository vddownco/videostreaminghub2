# VideoStreamingHub

A modern, feature-rich video streaming platform built with FastAPI, SQLAlchemy, and Bootstrap 5. This platform allows users to upload, share, and interact with videos in a YouTube-like environment.

## Features

- **User Authentication**: Secure registration and login system with JWT tokens
- **Video Management**: Upload, view, update, and delete videos
- **Interactive Features**: Like videos, add comments, and track watch history
- **Responsive UI**: Mobile-friendly interface built with Bootstrap 5
- **Video Processing**: Automatic thumbnail generation and video duration calculation (with FFmpeg)
- **Profile Management**: User profiles with customizable profile pictures

## Technical Stack

### Backend
- **FastAPI**: High-performance web framework for building APIs
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) system
- **Pydantic**: Data validation and settings management
- **JWT**: JSON Web Tokens for secure authentication
- **FFmpeg** (optional): Video processing and thumbnail generation

### Frontend
- **Bootstrap 5**: Responsive UI components and styling
- **JavaScript**: Client-side interactivity and fetch API for AJAX requests
- **Jinja2**: Server-side templating

### Storage
- File-based storage for videos, thumbnails, and profile pictures
- SQLite database (can be configured for other databases)

## Setup and Installation

### Prerequisites
- Python 3.8+
- FFmpeg (optional, for video processing)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/leefarhadaman/videostreaminghub.git
   cd videostreaminghub
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install FFmpeg (optional but recommended)**

   - **macOS**:
     ```bash
     brew install ffmpeg
     ```
   - **Ubuntu/Debian**:
     ```bash
     sudo apt update
     sudo apt install ffmpeg
     ```
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

5. **Initialize the database**
   ```bash
   python init_db.py
   ```

6. **Start the server**
   ```bash
   ./start_server.sh  # or python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
   ```

7. **Access the application**
   Open your browser and navigate to [http://localhost:8001](http://localhost:8001)

## Usage

### User Registration and Authentication
1. Register for a new account via the registration page
2. Log in with your credentials
3. Token-based authentication is handled automatically via JavaScript

### Video Management
1. Upload videos through the upload page (accessible when logged in)
2. Videos can be set as public or private during upload
3. Edit video details or delete videos from your profile
4. Add custom thumbnails or let the system generate one automatically

### Social Features
1. Like videos and add comments
2. View user profiles and their public videos
3. Track watch history

## Recent Improvements

- **Python 3.13 Compatibility**: Updated Jinja2 to fix "unicode-escape" encoding issues
- **Enhanced FFmpeg Integration**: Improved error handling and fallbacks when FFmpeg is not available
- **Responsive Upload UI**: Drag-and-drop file uploads with progress tracking
- **Comprehensive Error Handling**: Better user feedback and error recovery
- **Authentication System**: JWT-based auth with client-side token management

## Project Structure

```
VideoStreamingHub/
├── app/                    # Backend application
│   ├── database/           # Database models and configuration
│   ├── models/             # Pydantic schemas
│   ├── routes/             # API endpoints
│   ├── utils/              # Utility functions
│   └── main.py             # Application entry point
├── frontend/               # Frontend assets
│   ├── static/             # Static files (CSS, JS, uploads)
│   │   ├── js/             # JavaScript files
│   │   ├── css/            # CSS files
│   │   ├── videos/         # Uploaded videos
│   │   ├── thumbnails/     # Video thumbnails
│   │   └── profile_pictures/ # User profile pictures
│   └── templates/          # Jinja2 templates
├── venv/                   # Virtual environment
├── requirements.txt        # Python dependencies
├── start_server.sh         # Server startup script
└── README.md               # This file
```

## Future Plans

1. **Enhanced Video Processing**:
   - Implement video transcoding for different quality levels
   - Support for adaptive streaming (HLS/DASH)
   - Background processing queue for large videos

2. **User Experience Improvements**:
   - Playlist and subscription features
   - Enhanced search with filters and recommendations
   - Video analytics and statistics

3. **Infrastructure Enhancements**:
   - Docker containerization
   - Cloud storage integration (S3, GCS)
   - CDN integration for better content delivery

4. **Monetization Features**:
   - Premium content access
   - Subscription tiers
   - Creator monetization options

5. **Mobile Applications**:
   - Develop companion mobile apps using the existing API

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- FFmpeg for video processing capabilities
- FastAPI for the excellent web framework
- Bootstrap team for the responsive UI components 
