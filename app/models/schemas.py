from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Union
from datetime import datetime


# Base User Schema
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    bio: Optional[str] = None


# User Creation Schema
class UserCreate(UserBase):
    password: str


# User Update Schema
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    password: Optional[str] = None


# User Response Schema
class User(UserBase):
    id: int
    profile_picture: Optional[str] = None
    banner_image: Optional[str] = None
    created_at: datetime
    is_active: bool
    
    class Config:
        orm_mode = True


# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str


# Token Data Schema
class TokenData(BaseModel):
    username: Optional[str] = None


# Base Video Schema
class VideoBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_private: Optional[bool] = False


# Video Creation Schema
class VideoCreate(VideoBase):
    pass


# Video Update Schema
class VideoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_private: Optional[bool] = None


# Video Response Schema
class Video(VideoBase):
    id: int
    file_path: str
    thumbnail_path: Optional[str] = None
    duration: int
    views: int
    created_at: datetime
    updated_at: datetime
    uploader_id: int
    uploader: User
    
    class Config:
        orm_mode = True


# Base Comment Schema
class CommentBase(BaseModel):
    content: str
    parent_id: Optional[int] = None


# Comment Creation Schema
class CommentCreate(CommentBase):
    video_id: int


# Comment Update Schema
class CommentUpdate(BaseModel):
    content: Optional[str] = None


# Comment Response Schema
class Comment(CommentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    user_id: int
    video_id: int
    user: User
    likes_count: Optional[int] = 0
    
    class Config:
        orm_mode = True


# Watch History Schema
class WatchHistoryCreate(BaseModel):
    video_id: int
    timestamp: int


# Watch History Response Schema
class WatchHistory(BaseModel):
    id: int
    timestamp: int
    watched_at: datetime
    user_id: int
    video_id: int
    video: Video
    
    class Config:
        orm_mode = True


# Video Search Parameters
class VideoSearchParams(BaseModel):
    query: Optional[str] = None
    uploader: Optional[str] = None
    min_duration: Optional[int] = None
    max_duration: Optional[int] = None
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"
    limit: Optional[int] = 10
    offset: Optional[int] = 0 