from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import os

from .database import Base

# Helper function to generate unique filenames
def generate_filename():
    return str(uuid.uuid4())

# Subscription association table
subscription = Table(
    'subscription',
    Base.metadata,
    Column('subscriber_id', Integer, ForeignKey('users.id')),
    Column('channel_id', Integer, ForeignKey('users.id'))
)

# Video likes association table
video_likes = Table(
    'video_likes',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('video_id', Integer, ForeignKey('videos.id'))
)

# Comment likes association table
comment_likes = Table(
    'comment_likes',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('comment_id', Integer, ForeignKey('comments.id'))
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    profile_picture = Column(String, nullable=True)
    banner_image = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    videos = relationship("Video", back_populates="uploader")
    comments = relationship("Comment", back_populates="user")
    
    # Subscribers relationship
    subscribers = relationship(
        "User", 
        secondary=subscription,
        primaryjoin=(subscription.c.channel_id == id),
        secondaryjoin=(subscription.c.subscriber_id == id),
        backref="subscriptions"
    )
    
    # Video history
    watch_history = relationship("WatchHistory", back_populates="user")
    
    # Liked videos
    liked_videos = relationship(
        "Video",
        secondary=video_likes,
        back_populates="likes"
    )
    
    # Liked comments
    liked_comments = relationship(
        "Comment",
        secondary=comment_likes,
        back_populates="likes"
    )


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    file_path = Column(String)
    thumbnail_path = Column(String, nullable=True)
    duration = Column(Integer, default=0)  # in seconds
    views = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_private = Column(Boolean, default=False)
    
    # Foreign keys
    uploader_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    uploader = relationship("User", back_populates="videos")
    comments = relationship("Comment", back_populates="video", cascade="all, delete-orphan")
    watch_history = relationship("WatchHistory", back_populates="video", cascade="all, delete-orphan")
    
    # Likes relationship
    likes = relationship(
        "User",
        secondary=video_likes,
        back_populates="liked_videos"
    )


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    video_id = Column(Integer, ForeignKey("videos.id"))
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="comments")
    video = relationship("Video", back_populates="comments")
    replies = relationship("Comment", backref="parent", remote_side=[id])
    
    # Likes relationship
    likes = relationship(
        "User",
        secondary=comment_likes,
        back_populates="liked_comments"
    )


class WatchHistory(Base):
    __tablename__ = "watch_history"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(Integer, default=0)  # Position in seconds where user left off
    watched_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    video_id = Column(Integer, ForeignKey("videos.id"))
    
    # Relationships
    user = relationship("User", back_populates="watch_history")
    video = relationship("Video", back_populates="watch_history") 