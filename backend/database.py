from sqlalchemy import (
    create_engine, Column, Integer,
    String, Text, DateTime, ForeignKey, Boolean
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./enterprise_chatbot.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id               = Column(Integer, primary_key=True, index=True)
    username         = Column(String(50), unique=True, index=True, nullable=False)
    email            = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password  = Column(String(200), nullable=False)
    created_at       = Column(DateTime, default=datetime.utcnow)
    is_active        = Column(Boolean, default=True)
    sessions         = relationship("ChatSession", back_populates="user",
                                    cascade="all, delete-orphan")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    title      = Column(String(200), default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    documents  = Column(Text, default="")
    user       = relationship("User", back_populates="sessions")
    messages   = relationship("ChatMessage", back_populates="session",
                              cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id         = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role       = Column(String(20), nullable=False)
    content    = Column(Text, nullable=False)
    sources    = Column(Text, default="")
    timestamp  = Column(DateTime, default=datetime.utcnow)
    session    = relationship("ChatSession", back_populates="messages")

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables ready")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()