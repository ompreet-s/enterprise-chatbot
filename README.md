# 🤖 Enterprise Chatbot

An AI-powered document Q&A system that lets you upload documents and ask questions about them using text or voice — powered by RAG (Retrieval-Augmented Generation), LLaMA 3.3, and FAISS.

![Enterprise Chatbot Screenshot](frontend/src/assets/Screenshot%202026-06-19%20110829.png)

🔗 **Repository:** [github.com/ompreet-s/enterprise-chatbot](https://github.com/ompreet-s/enterprise-chatbot)

---

## ✨ Features

- 📄 **Multi-format document support** — PDF, DOCX, XLSX, TXT
- 🔍 **High-accuracy RAG pipeline** — query expansion + reranking + self-verification
- 🎙️ **Voice transcription** — powered by OpenAI Whisper
- 🔊 **Text-to-speech answers** — powered by gTTS
- 🧠 **Conversation memory** — remembers context across a chat session
- 🔐 **Authentication** — JWT-based login and registration with bcrypt password hashing
- 📋 **Chat history** — every conversation saved and searchable, with reload support
- 🌙 **Dark VS Code-themed UI** — built with React

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, Vite, Axios, react-dropzone, react-icons |
| Backend | FastAPI, Python |
| LLM | Groq (LLaMA 3.3 70B) |
| Embeddings | BAAI/bge-large-en-v1.5 (HuggingFace) |
| Vector Store | FAISS |
| Reranker | CrossEncoder (ms-marco-MiniLM) |
| Speech-to-Text | OpenAI Whisper |
| Text-to-Speech | gTTS |
| Database | SQLite + SQLAlchemy |
| Auth | JWT + bcrypt |

---

## 📐 Architecture

```
USER
  │
  ├── Text Query ──┐
  ├── Document Upload ──┤
  └── Voice Query ──┘
              │
       Document Loader (PDF/DOCX/XLSX/TXT)
              │
         Text Extraction
              │
       Chunking (500-1000 chars)
              │
     Embedding Model (BAAI/bge-large)
              │
          Vector Database (FAISS)
              │
       Retriever + Reranker
              │
         Context Builder
              │
        LLM (Groq LLaMA 3.3)
              │
         Generated Answer
              │
     ┌────────┴────────┐
Text Output      Text-to-Speech
                       │
                  Voice Output
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- A free [Groq API key](https://console.groq.com)

### 1. Clone the repository

```bash
git clone https://github.com/ompreet-s/enterprise-chatbot.git
cd enterprise-chatbot
```

### 2. Backend setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file inside `backend/`:
```
GROQ_API_KEY=your_groq_api_key_here
```

Run the backend:
```bash
uvicorn main:app --reload --port 8000
```

Backend runs at `http://localhost:8000` — visit `/docs` for the interactive API documentation.

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

### 4. Open the app

Go to `http://localhost:5173`, create an account, upload a document, and start asking questions!

---

## 📂 Project Structure

```
enterprise-chatbot/
├── backend/
│   ├── main.py              # FastAPI app and routes
│   ├── rag.py                # RAG pipeline: chunking, embedding, retrieval, LLM
│   ├── voice.py               # Whisper STT + gTTS
│   ├── auth.py                # JWT + bcrypt password hashing
│   ├── database.py            # SQLAlchemy models
│   ├── routers/
│   │   ├── auth_router.py     # Login/register endpoints
│   │   └── history_router.py  # Chat history endpoints
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   ├── main.css
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── Chat.jsx
│   │   │   └── History.jsx
│   │   └── components/
│   │       ├── Sidebar.jsx
│   │       ├── ChatArea.jsx
│   │       └── Message.jsx
│   └── package.json
├── assets/
│   └── screenshot.png
└── README.md
```

---

## 🎯 How It Works (RAG Pipeline)

1. **Document Loader** — Reads PDF/DOCX/XLSX/TXT and extracts plain text
2. **Chunking** — Splits text into ~1000-character overlapping chunks
3. **Embedding** — Converts each chunk into a vector using BAAI/bge-large-en-v1.5
4. **Vector Store** — Stores vectors in FAISS for fast similarity search
5. **Query Expansion** — Rephrases the user's question 3 different ways
6. **Retrieval** — Finds top relevant chunks for each query variant
7. **Reranking** — A CrossEncoder model scores and picks the best 5 chunks
8. **Context Building** — Assembles chunks into a strict prompt
9. **LLM Generation** — LLaMA 3.3 70B generates an answer using only the provided context
10. **Verification** — A second LLM call checks the answer is fully supported by the context

This pipeline minimizes hallucination and keeps answers grounded in the actual uploaded documents.

---

## 📝 License

This project is open source and available for personal and educational use.

---

## 🙋 Author

Built by [ompreet-s](https://github.com/ompreet-s)
