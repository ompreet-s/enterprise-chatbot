from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db, ChatSession, ChatMessage, User
from auth import get_current_user
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/history", tags=["History"])

# ── SCHEMAS ───────────────────────────────────────────────────────────────────

class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    sources: str
    timestamp: datetime

    class Config:
        from_attributes = True

class SessionOut(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    documents: str
    message_count: Optional[int] = 0

class SaveMessageRequest(BaseModel):
    session_id: Optional[int] = None
    role: str
    content: str
    sources: List[str] = []
    documents: List[str] = []

class UpdateTitleRequest(BaseModel):
    title: str

# ── CREATE SESSION ────────────────────────────────────────────────────────────

@router.post("/session")
def create_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = ChatSession(
        user_id=current_user.id,
        title="New Chat",
        documents=""
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"session_id": session.id, "title": session.title}

# ── SAVE MESSAGE ──────────────────────────────────────────────────────────────

@router.post("/message")
def save_message(
    req: SaveMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Create session if none
    if not req.session_id:
        session = ChatSession(
            user_id=current_user.id,
            title="New Chat",
            documents=",".join(req.documents)
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        session_id = session.id
    else:
        session = db.query(ChatSession).filter(
            ChatSession.id == req.session_id,
            ChatSession.user_id == current_user.id
        ).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found.")
        session_id = req.session_id

        # Update documents list
        if req.documents:
            existing = set(session.documents.split(",")) if session.documents else set()
            existing.update(req.documents)
            session.documents = ",".join(filter(None, existing))

        # Auto-title from first user message
        msg_count = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).count()
        if msg_count == 0 and req.role == "user":
            session.title = req.content[:50] + ("..." if len(req.content) > 50 else "")

        session.updated_at = datetime.utcnow()
        db.commit()

    # Save message
    message = ChatMessage(
        session_id=session_id,
        role=req.role,
        content=req.content,
        sources=",".join(req.sources)
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    return {
        "session_id": session_id,
        "message_id": message.id,
        "title": session.title
    }

# ── GET ALL SESSIONS ──────────────────────────────────────────────────────────

@router.get("/sessions", response_model=List[SessionOut])
def get_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(desc(ChatSession.updated_at)).all()

    result = []
    for s in sessions:
        count = db.query(ChatMessage).filter(
            ChatMessage.session_id == s.id
        ).count()
        result.append(SessionOut(
            id=s.id,
            title=s.title,
            created_at=s.created_at,
            updated_at=s.updated_at,
            documents=s.documents,
            message_count=count
        ))
    return result

# ── GET SESSION MESSAGES ──────────────────────────────────────────────────────

@router.get("/session/{session_id}/messages")
def get_session_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.timestamp).all()

    return {
        "session": {
            "id": session.id,
            "title": session.title,
            "documents": session.documents,
            "created_at": session.created_at
        },
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "sources": m.sources.split(",") if m.sources else [],
                "timestamp": m.timestamp
            }
            for m in messages
        ]
    }

# ── DELETE SESSION ────────────────────────────────────────────────────────────

@router.delete("/session/{session_id}")
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    db.delete(session)
    db.commit()
    return {"success": True, "message": "Session deleted."}

# ── UPDATE SESSION TITLE ──────────────────────────────────────────────────────

@router.put("/session/{session_id}/title")
def update_title(
    session_id: int,
    req: UpdateTitleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    session.title = req.title
    db.commit()
    return {"success": True}