from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import tempfile
import os
from typing import List
from database import create_tables
from routers import auth_router, history_router
from rag import (
    load_document, chunk_with_metadata,
    build_vector_store, save_vector_store,
    load_vector_store, ask
)
from voice import transcribe_audio, text_to_speech
from auth import get_current_user

# Create tables
create_tables()

app = FastAPI(title="Enterprise Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(history_router.router)

# Global state
vector_store  = None
indexed_files = []
chat_history  = []

class QuestionRequest(BaseModel):
    question:   str
    use_memory: bool = True

@app.get("/")
def root():
    return {"status": "running", "message": "Enterprise Chatbot API is live"}

@app.get("/status")
def get_status(current_user=Depends(get_current_user)):
    return {
        "vector_store_loaded": vector_store is not None,
        "indexed_files":       indexed_files,
        "total_messages":      len(chat_history)
    }

@app.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    current_user=Depends(get_current_user)
):
    global vector_store, indexed_files, chat_history
    all_chunks = []
    processed  = []

    for file in files:
        ext = file.filename.split(".")[-1].lower()
        if ext not in ["pdf", "docx", "xlsx", "txt"]:
            raise HTTPException(status_code=400, detail=f"Unsupported: .{ext}")

        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        try:
            text   = load_document(tmp_path, file.filename)
            chunks = chunk_with_metadata(text, file.filename)
            all_chunks.extend(chunks)
            processed.append({
                "filename":   file.filename,
                "chunks":     len(chunks),
                "characters": len(text)
            })
        finally:
            os.unlink(tmp_path)

    vector_store  = build_vector_store(all_chunks)
    save_vector_store(vector_store)
    indexed_files = [f["filename"] for f in processed]
    chat_history  = []

    return {
        "success": True,
        "message": f"Processed {len(files)} files, {len(all_chunks)} chunks",
        "files":   processed
    }

@app.post("/ask")
async def ask_question(
    request: QuestionRequest,
    current_user=Depends(get_current_user)
):
    global vector_store, chat_history

    if vector_store is None:
        raise HTTPException(status_code=400, detail="No documents loaded.")

    history = chat_history if request.use_memory else []
    answer, sources = ask(request.question, vector_store, history)

    if request.use_memory:
        chat_history.append({"role": "user",     "content": request.question})
        chat_history.append({"role": "assistant", "content": answer})
        if len(chat_history) > 20:
            chat_history = chat_history[-20:]

    return {"answer": answer, "sources": sources, "question": request.question}

@app.post("/transcribe")
async def transcribe_voice(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    ext = file.filename.split(".")[-1].lower()
    allowed = ["wav", "mp3", "m4a", "ogg", "webm"]
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format: .{ext}"
        )

    suffix = f".{ext}"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        transcript = transcribe_audio(tmp_path)
        if not transcript.strip():
            raise HTTPException(
                status_code=400,
                detail="No speech detected. Please speak clearly."
            )
        return {"transcript": transcript}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_path)

@app.post("/speak")
async def speak(
    text: str = Form(...),
    current_user=Depends(get_current_user)
):
    audio_path = text_to_speech(text, "response.mp3")
    return FileResponse(audio_path, media_type="audio/mpeg")

@app.post("/clear")
def clear_chat(current_user=Depends(get_current_user)):
    global chat_history
    chat_history = []
    return {"success": True}

@app.post("/load-index")
def load_saved_index(current_user=Depends(get_current_user)):
    global vector_store
    try:
        vector_store = load_vector_store()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))