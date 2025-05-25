import os
import uuid
import shutil
import subprocess
from pathlib import Path
from fastapi import UploadFile, HTTPException
from PIL import Image
import io
import aiofiles
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get storage paths from environment variables or use defaults
VIDEO_STORAGE_PATH = os.getenv("VIDEO_STORAGE_PATH", "./frontend/static/videos")
THUMBNAIL_STORAGE_PATH = os.getenv("THUMBNAIL_STORAGE_PATH", "./frontend/static/thumbnails")
PROFILE_PICTURE_PATH = os.getenv("PROFILE_PICTURE_PATH", "./frontend/static/profile_pictures")
BANNER_PATH = os.getenv("BANNER_PATH", "./frontend/static/banners")

# Default thumbnail path for videos when FFmpeg is not available
DEFAULT_THUMBNAIL_PATH = os.getenv("DEFAULT_THUMBNAIL_PATH", "./frontend/static/thumbnails/default_video.jpg")

# Ensure directories exist
for directory in [VIDEO_STORAGE_PATH, THUMBNAIL_STORAGE_PATH, PROFILE_PICTURE_PATH, BANNER_PATH]:
    os.makedirs(directory, exist_ok=True)

# Create default thumbnail if it doesn't exist
if not os.path.exists(DEFAULT_THUMBNAIL_PATH):
    try:
        # Create a simple black thumbnail
        img = Image.new('RGB', (1280, 720), color=(0, 0, 0))
        # Draw play icon or other elements if desired
        img.save(DEFAULT_THUMBNAIL_PATH)
        logger.info(f"Created default thumbnail at {DEFAULT_THUMBNAIL_PATH}")
    except Exception as e:
        logger.error(f"Could not create default thumbnail: {str(e)}")


def check_ffmpeg():
    """Check if FFmpeg is installed on the system."""
    try:
        result = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            logger.info("FFmpeg is installed and available")
            return True
        else:
            logger.warning(f"FFmpeg check failed with return code {result.returncode}")
            return False
    except FileNotFoundError:
        logger.warning("FFmpeg is not installed on the system, some features will be limited")
        return False
    except Exception as e:
        logger.error(f"Error checking FFmpeg: {str(e)}")
        return False


async def save_upload_file(upload_file: UploadFile, directory: str) -> str:
    """
    Save an uploaded file to the specified directory.
    Returns the path to the saved file.
    """
    # Generate a unique filename
    file_extension = os.path.splitext(upload_file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(directory, unique_filename)
    
    # Save the file
    async with aiofiles.open(file_path, 'wb') as out_file:
        # Read the file in chunks
        while content := await upload_file.read(1024 * 1024):  # 1MB chunks
            await out_file.write(content)
    
    return file_path


async def save_video(video_file: UploadFile) -> str:
    """Save an uploaded video file."""
    # Check if the file is a video
    if not video_file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="File is not a video")
    
    return await save_upload_file(video_file, VIDEO_STORAGE_PATH)


async def save_thumbnail(thumbnail_file: UploadFile) -> str:
    """Save an uploaded thumbnail file."""
    # Check if the file is an image
    if not thumbnail_file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File is not an image")
    
    return await save_upload_file(thumbnail_file, THUMBNAIL_STORAGE_PATH)


async def save_profile_picture(image_file: UploadFile) -> str:
    """Save an uploaded profile picture."""
    # Check if the file is an image
    if not image_file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File is not an image")
    
    return await save_upload_file(image_file, PROFILE_PICTURE_PATH)


async def save_banner_image(image_file: UploadFile) -> str:
    """Save an uploaded banner image."""
    # Check if the file is an image
    if not image_file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File is not an image")
    
    return await save_upload_file(image_file, BANNER_PATH)


def generate_thumbnail_from_video(video_path: str) -> str:
    """
    Generate a thumbnail from a video file using FFmpeg.
    Returns the path to the generated thumbnail.
    If FFmpeg is not available, returns the default thumbnail.
    """
    if not check_ffmpeg():
        logger.warning("Using default thumbnail because FFmpeg is not installed")
        return DEFAULT_THUMBNAIL_PATH
    
    # Generate a unique filename for the thumbnail
    thumbnail_filename = f"{uuid.uuid4()}.jpg"
    thumbnail_path = os.path.join(THUMBNAIL_STORAGE_PATH, thumbnail_filename)
    
    # Extract a frame from the middle of the video
    try:
        logger.info(f"Generating thumbnail for video: {video_path}")
        result = subprocess.run([
            "ffmpeg",
            "-i", video_path,
            "-ss", "00:00:05",  # 5 seconds into the video
            "-frames:v", "1",
            thumbnail_path
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if os.path.exists(thumbnail_path) and os.path.getsize(thumbnail_path) > 0:
            logger.info(f"Successfully generated thumbnail: {thumbnail_path}")
            return thumbnail_path
        else:
            logger.error("Thumbnail was not created or is empty")
            return DEFAULT_THUMBNAIL_PATH
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to generate thumbnail: {e.stderr}")
        return DEFAULT_THUMBNAIL_PATH
    except Exception as e:
        logger.error(f"Unexpected error generating thumbnail: {str(e)}")
        return DEFAULT_THUMBNAIL_PATH


def get_video_duration(video_path: str) -> int:
    """
    Get the duration of a video file in seconds using FFmpeg.
    If FFmpeg is not available, returns a default duration of 0.
    """
    if not check_ffmpeg():
        logger.warning("Unable to get video duration because FFmpeg is not installed")
        return 0
    
    try:
        result = subprocess.run([
            "ffmpeg",
            "-i", video_path,
            "-hide_banner"
        ], capture_output=True, text=True, check=False)
        
        # Parse the output to find the duration
        error_output = result.stderr
        for line in error_output.split('\n'):
            if "Duration" in line:
                time_str = line.split("Duration: ")[1].split(",")[0].strip()
                h, m, s = time_str.split(":")
                seconds = int(float(h)) * 3600 + int(float(m)) * 60 + float(s)
                return int(seconds)
        
        return 0
    except Exception as e:
        logger.error(f"Error getting video duration: {str(e)}")
        return 0


def delete_file(file_path: str) -> bool:
    """
    Delete a file from the filesystem.
    Returns True if successful, False otherwise.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {str(e)}")
        return False 