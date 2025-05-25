from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os

from ..database.database import get_db
from ..database.models import User, Video
from ..models.schemas import User as UserSchema, UserUpdate, Video as VideoSchema
from ..utils.auth import get_current_active_user, get_password_hash
from ..utils.video import save_profile_picture, save_banner_image

# Create router
router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{username}", response_model=UserSchema)
async def get_user(username: str, db: Session = Depends(get_db)):
    """
    Get a user by username.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.get("/{username}/videos", response_model=List[VideoSchema])
async def get_user_videos(
    username: str, 
    skip: int = 0, 
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get videos uploaded by a user.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # If current user is the same as requested user, show all videos
    # Otherwise, only show public videos
    if current_user.id == user.id:
        videos = db.query(Video).filter(Video.uploader_id == user.id)
    else:
        videos = db.query(Video).filter(
            Video.uploader_id == user.id,
            Video.is_private == False
        )
    
    return videos.offset(skip).limit(limit).all()


@router.put("/me", response_model=UserSchema)
async def update_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update the current user's information.
    """
    # Check if username is being changed and if it's already taken
    if user_update.username and user_update.username != current_user.username:
        db_user = db.query(User).filter(User.username == user_update.username).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = user_update.username
    
    # Check if email is being changed and if it's already taken
    if user_update.email and user_update.email != current_user.email:
        db_user = db.query(User).filter(User.email == user_update.email).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = user_update.email
    
    # Update other fields
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    if user_update.bio is not None:
        current_user.bio = user_update.bio
    
    if user_update.password:
        current_user.hashed_password = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/me/profile-picture", response_model=UserSchema)
async def upload_profile_picture(
    profile_picture: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload a profile picture for the current user.
    """
    # Save the uploaded profile picture
    profile_picture_path = await save_profile_picture(profile_picture)
    
    # Update the user's profile picture
    current_user.profile_picture = os.path.basename(profile_picture_path)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/me/banner", response_model=UserSchema)
async def upload_banner(
    banner: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload a banner image for the current user.
    """
    # Save the uploaded banner image
    banner_path = await save_banner_image(banner)
    
    # Update the user's banner image
    current_user.banner_image = os.path.basename(banner_path)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/{username}/subscribe", response_model=UserSchema)
async def subscribe_to_user(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Subscribe to a user.
    """
    # Get the user to subscribe to
    channel = db.query(User).filter(User.username == username).first()
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if the user is trying to subscribe to themselves
    if current_user.id == channel.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot subscribe to yourself"
        )
    
    # Check if the user is already subscribed
    if channel in current_user.subscriptions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already subscribed to this user"
        )
    
    # Add the subscription
    current_user.subscriptions.append(channel)
    
    db.commit()
    db.refresh(channel)
    
    return channel


@router.post("/{username}/unsubscribe", response_model=UserSchema)
async def unsubscribe_from_user(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Unsubscribe from a user.
    """
    # Get the user to unsubscribe from
    channel = db.query(User).filter(User.username == username).first()
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if the user is subscribed
    if channel not in current_user.subscriptions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not subscribed to this user"
        )
    
    # Remove the subscription
    current_user.subscriptions.remove(channel)
    
    db.commit()
    db.refresh(channel)
    
    return channel 