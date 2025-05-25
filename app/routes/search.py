from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional

from ..database.database import get_db
from ..database.models import Video, User
from ..models.schemas import Video as VideoSchema, VideoSearchParams

# Create router
router = APIRouter(prefix="/search", tags=["search"])


@router.get("/videos", response_model=List[VideoSchema])
async def search_videos(
    params: VideoSearchParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    Search for videos based on various parameters.
    """
    # Base query: only public videos
    query = db.query(Video).filter(Video.is_private == False)
    
    # Apply text search if provided
    if params.query:
        search_term = f"%{params.query}%"
        query = query.filter(
            or_(
                Video.title.ilike(search_term),
                Video.description.ilike(search_term)
            )
        )
    
    # Filter by uploader if provided
    if params.uploader:
        query = query.join(User).filter(User.username == params.uploader)
    
    # Filter by duration if provided
    filters = []
    if params.min_duration is not None:
        filters.append(Video.duration >= params.min_duration)
    if params.max_duration is not None:
        filters.append(Video.duration <= params.max_duration)
    
    if filters:
        query = query.filter(and_(*filters))
    
    # Apply sorting
    if params.sort_by == "views":
        if params.sort_order == "asc":
            query = query.order_by(Video.views)
        else:
            query = query.order_by(Video.views.desc())
    elif params.sort_by == "duration":
        if params.sort_order == "asc":
            query = query.order_by(Video.duration)
        else:
            query = query.order_by(Video.duration.desc())
    else:  # Default: created_at
        if params.sort_order == "asc":
            query = query.order_by(Video.created_at)
        else:
            query = query.order_by(Video.created_at.desc())
    
    # Apply pagination
    query = query.offset(params.offset).limit(params.limit)
    
    return query.all()


@router.get("/trending", response_model=List[VideoSchema])
async def get_trending_videos(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get trending videos based on views.
    """
    # For a real application, this would use a more complex algorithm
    # that takes into account views, likes, and recency
    # Here we just use a simple views-based approach
    videos = db.query(Video).filter(
        Video.is_private == False
    ).order_by(Video.views.desc()).limit(limit).all()
    
    return videos


@router.get("/latest", response_model=List[VideoSchema])
async def get_latest_videos(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get the latest videos.
    """
    videos = db.query(Video).filter(
        Video.is_private == False
    ).order_by(Video.created_at.desc()).limit(limit).all()
    
    return videos 