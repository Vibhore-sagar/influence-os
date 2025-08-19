# app/models.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.db import Base

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    body = Column(Text)
    hashtags = Column(String)
    hashtags_raw = Column(String, nullable=True)
    hooks = Column(String, nullable=True)
    created_at = Column(String)
    scheduled_at = Column(String, nullable=True)
    status = Column(String, default="draft")


class Metrics(Base):
    __tablename__ = "metrics"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    impressions = Column(Integer, default=0)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    li_person_urn = Column(String, nullable=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(String, nullable=True)
