from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
import logging

# Set up logging
logger = logging.getLogger(__name__)

from ..database.database import get_db
from ..database.models import User, Video, Comment, WatchHistory
from ..models.schemas import (
    VideoCreate, Video as VideoSchema, VideoUpdate,
    CommentCreate, Comment as CommentSchema, CommentUpdate,
    WatchHistoryCreate, WatchHistory as WatchHistorySchema
)
from ..utils.auth import get_current_active_user
from ..utils.video import (
    save_video, save_thumbnail, generate_thumbnail_from_video,
    get_video_duration, delete_file, VIDEO_STORAGE_PATH, THUMBNAIL_STORAGE_PATH, DEFAULT_THUMBNAIL_PATH
)

# Create router
router = APIRouter(prefix="/videos", tags=["videos"])


@router.post("/", response_model=VideoSchema, status_code=status.HTTP_201_CREATED)
async def create_video(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    is_private: bool = Form(False),
    video_file: UploadFile = File(...),
    thumbnail_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload a new video.
    """
    # Variables to track created files for cleanup in case of error
    video_path = None
    thumbnail_path = None
    
    try:
        # Save the video file
        logger.info(f"Saving video file: {video_file.filename}")
        video_path = await save_video(video_file)
        logger.info(f"Video saved to {video_path}")
        
        # Save the thumbnail or generate one from the video
        try:
            if thumbnail_file:
                logger.info(f"Saving provided thumbnail: {thumbnail_file.filename}")
                thumbnail_path = await save_thumbnail(thumbnail_file)
            else:
                logger.info("Generating thumbnail from video")
                thumbnail_path = generate_thumbnail_from_video(video_path)
            logger.info(f"Thumbnail path: {thumbnail_path}")
        except Exception as e:
            # If thumbnail generation fails, use default thumbnail
            logger.error(f"Thumbnail generation failed: {str(e)}")
            thumbnail_path = DEFAULT_THUMBNAIL_PATH
            logger.info(f"Using default thumbnail: {thumbnail_path}")
        
        # Get the video duration
        try:
            logger.info("Calculating video duration")
            duration = get_video_duration(video_path)
            logger.info(f"Video duration: {duration} seconds")
        except Exception as e:
            # If duration calculation fails, set to 0
            logger.error(f"Duration calculation failed: {str(e)}")
            duration = 0
        
        # Create the video in the database
        logger.info("Creating video entry in database")
        db_video = Video(
            title=title,
            description=description,
            file_path=os.path.basename(video_path),
            thumbnail_path=os.path.basename(thumbnail_path),
            duration=duration,
            is_private=is_private,
            uploader_id=current_user.id
        )
        
        db.add(db_video)
        db.commit()
        db.refresh(db_video)
        logger.info(f"Video created with ID: {db_video.id}")
        
        return db_video
        
    except Exception as e:
        # Log the error
        logger.error(f"Error uploading video: {str(e)}")
        
        # Clean up any saved files
        if video_path and os.path.exists(video_path):
            logger.info(f"Cleaning up video file: {video_path}")
            delete_file(video_path)
        
        if thumbnail_path and thumbnail_path != DEFAULT_THUMBNAIL_PATH and os.path.exists(thumbnail_path):
            logger.info(f"Cleaning up thumbnail file: {thumbnail_path}")
            delete_file(thumbnail_path)
            
        # Roll back database changes if any
        db.rollback()
            
        # Re-raise the exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading video: {str(e)}"
        )


@router.get("/", response_model=List[VideoSchema])
async def get_videos(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Get a list of videos.
    """
    videos = db.query(Video).filter(Video.is_private == False).offset(skip).limit(limit).all()
    return videos


@router.get("/{video_id}", response_model=VideoSchema)
async def get_video(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """
    Get a video by ID.
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Check if the video is private and the user is not the uploader
    if video.is_private and current_user.id != video.uploader_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this video"
        )
    
    # Increment view count
    video.views += 1
    db.commit()
    
    return video


@router.put("/{video_id}", response_model=VideoSchema)
async def update_video(
    video_id: int,
    video_update: VideoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a video by ID.
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Check if the user is the uploader
    if current_user.id != video.uploader_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this video"
        )
    
    # Update the video fields
    if video_update.title is not None:
        video.title = video_update.title
    
    if video_update.description is not None:
        video.description = video_update.description
    
    if video_update.is_private is not None:
        video.is_private = video_update.is_private
    
    db.commit()
    db.refresh(video)
    
    return video


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a video by ID.
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Check if the user is the uploader
    if current_user.id != video.uploader_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this video"
        )
    
    # Delete the video file
    video_path = os.path.join(VIDEO_STORAGE_PATH, video.file_path)
    delete_file(video_path)
    
    # Delete the thumbnail file
    if video.thumbnail_path:
        thumbnail_path = os.path.join(THUMBNAIL_STORAGE_PATH, video.thumbnail_path)
        delete_file(thumbnail_path)
    
    # Delete the video from the database
    db.delete(video)
    db.commit()
    
    return


@router.post("/{video_id}/thumbnail", response_model=VideoSchema)
async def update_thumbnail(
    video_id: int,
    thumbnail_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a video's thumbnail.
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Check if the user is the uploader
    if current_user.id != video.uploader_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this video"
        )
    
    # Delete the old thumbnail
    if video.thumbnail_path:
        old_thumbnail_path = os.path.join(THUMBNAIL_STORAGE_PATH, video.thumbnail_path)
        delete_file(old_thumbnail_path)
    
    # Save the new thumbnail
    thumbnail_path = await save_thumbnail(thumbnail_file)
    
    # Update the video
    video.thumbnail_path = os.path.basename(thumbnail_path)
    
    db.commit()
    db.refresh(video)
    
    return video


@router.post("/{video_id}/like", response_model=VideoSchema)
async def like_video(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Like a video.
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Check if the video is private and the user is not the uploader
    if video.is_private and current_user.id != video.uploader_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to like this video"
        )
    
    # Check if the user has already liked the video
    if video in current_user.liked_videos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already liked this video"
        )
    
    # Add the like
    current_user.liked_videos.append(video)
    
    db.commit()
    db.refresh(video)
    
    return video


@router.post("/{video_id}/unlike", response_model=VideoSchema)
async def unlike_video(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Unlike a video.
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Check if the user has liked the video
    if video not in current_user.liked_videos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have not liked this video"
        )
    
    # Remove the like
    current_user.liked_videos.remove(video)
    
    db.commit()
    db.refresh(video)
    
    return video


@router.post("/{video_id}/comments", response_model=CommentSchema, status_code=status.HTTP_201_CREATED)
async def create_comment(
    video_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a comment on a video.
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Check if the video is private and the user is not the uploader
    if video.is_private and current_user.id != video.uploader_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to comment on this video"
        )
    
    # Check if the parent comment exists
    if comment.parent_id:
        parent_comment = db.query(Comment).filter(Comment.id == comment.parent_id).first()
        if not parent_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent comment not found"
            )
        if parent_comment.video_id != video_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent comment does not belong to this video"
            )
    
    # Create the comment
    db_comment = Comment(
        content=comment.content,
        user_id=current_user.id,
        video_id=video_id,
        parent_id=comment.parent_id
    )
    
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    return db_comment


@router.get("/{video_id}/comments", response_model=List[CommentSchema])
async def get_comments(
    video_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get comments for a video.
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    comments = db.query(Comment).filter(
        Comment.video_id == video_id,
        Comment.parent_id == None  # Only get top-level comments
    ).offset(skip).limit(limit).all()
    
    return comments


@router.put("/comments/{comment_id}", response_model=CommentSchema)
async def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a comment.
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Check if the user is the author of the comment
    if current_user.id != comment.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this comment"
        )
    
    # Update the comment
    if comment_update.content is not None:
        comment.content = comment_update.content
    
    db.commit()
    db.refresh(comment)
    
    return comment


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a comment.
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Check if the user is the author of the comment or the video uploader
    video = db.query(Video).filter(Video.id == comment.video_id).first()
    if current_user.id != comment.user_id and current_user.id != video.uploader_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this comment"
        )
    
    # Delete the comment
    db.delete(comment)
    db.commit()
    
    return


@router.post("/comments/{comment_id}/like", response_model=CommentSchema)
async def like_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Like a comment.
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Check if the user has already liked the comment
    if comment in current_user.liked_comments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already liked this comment"
        )
    
    # Add the like
    current_user.liked_comments.append(comment)
    
    db.commit()
    db.refresh(comment)
    
    return comment


@router.post("/comments/{comment_id}/unlike", response_model=CommentSchema)
async def unlike_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Unlike a comment.
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Check if the user has liked the comment
    if comment not in current_user.liked_comments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have not liked this comment"
        )
    
    # Remove the like
    current_user.liked_comments.remove(comment)
    
    db.commit()
    db.refresh(comment)
    
    return comment


@router.post("/{video_id}/watch-history", response_model=WatchHistorySchema)
async def update_watch_history(
    video_id: int,
    watch_history: WatchHistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update watch history for a video.
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Check if the video is private and the user is not the uploader
    if video.is_private and current_user.id != video.uploader_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update watch history for this video"
        )
    
    # Check if there's an existing watch history entry
    existing_history = db.query(WatchHistory).filter(
        WatchHistory.user_id == current_user.id,
        WatchHistory.video_id == video_id
    ).first()
    
    if existing_history:
        # Update the existing entry
        existing_history.timestamp = watch_history.timestamp
        existing_history.watched_at = db.query(WatchHistory).filter(
            WatchHistory.id == existing_history.id
        ).first().watched_at
        
        db.commit()
        db.refresh(existing_history)
        
        return existing_history
    else:
        # Create a new entry
        db_watch_history = WatchHistory(
            user_id=current_user.id,
            video_id=video_id,
            timestamp=watch_history.timestamp
        )
        
        db.add(db_watch_history)
        db.commit()
        db.refresh(db_watch_history)
        
        return db_watch_history


@router.get("/watch-history", response_model=List[WatchHistorySchema])
async def get_watch_history(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the current user's watch history.
    """
    watch_history = db.query(WatchHistory).filter(
        WatchHistory.user_id == current_user.id
    ).order_by(WatchHistory.watched_at.desc()).offset(skip).limit(limit).all()
    
    return watch_history


@router.get("/file/{filename}")
async def get_video_file(filename: str):
    """
    Get a video file by filename.
    """
    file_path = os.path.join(VIDEO_STORAGE_PATH, filename)
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video file not found"
        )
    
    return FileResponse(file_path)


@router.get("/thumbnail/{filename}")
async def get_thumbnail_file(filename: str):
    """
    Get a thumbnail file by filename.
    """
    file_path = os.path.join(THUMBNAIL_STORAGE_PATH, filename)
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thumbnail file not found"
        )
    
    return FileResponse(file_path) 