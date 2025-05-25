from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from .database.database import engine, Base, get_db
from .database.models import Video
from .routes import auth, user, video, search

# Load environment variables
load_dotenv()

# Create the database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="VideoStreamingHub",
    description="A modern video streaming platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(video.router)
app.include_router(search.router)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="frontend/templates")


@app.get("/")
async def read_root(request: Request):
    """
    Render the home page.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/video/{video_id}")
async def video_page(request: Request, video_id: int, db: Session = Depends(get_db)):
    """
    Render the video player page.
    """
    # Get the video
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return templates.TemplateResponse("video.html", {
        "request": request,
        "video": video
    })


@app.get("/upload")
async def upload_page(request: Request):
    """
    Render the upload page.
    """
    return templates.TemplateResponse("upload.html", {"request": request})


@app.get("/login")
async def login_page(request: Request):
    """
    Render the login page.
    """
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register")
async def register_page(request: Request):
    """
    Render the registration page.
    """
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"} 