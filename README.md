---
title: Aethera AI
emoji: 🧠
colorFrom: indigo
colorTo: violet
sdk: docker
app_port: 7860
pinned: false
---

# Aethera AI - Personalized RAG LLM ChatBot

Aethera AI is a production-grade, multi-user, context-adaptive personal AI assistant platform built with a **FastAPI backend** and a **Next.js frontend**. The system features continuous background memory learning, vector database retrieval, and support for the Groq API.

---

## Key Features

* **Groq LLM Service**: Powered by `llama-3.3-70b-versatile` for fast streaming chat responses and precise structured JSON memory extraction.
* **Continuous Background Memory Learning**: A background agent parses conversation turns in real-time, extracting preferences, goals, relationships, and facts.
* **Robust Hybrid RAG Memory**: 
  * Retrieves relevant context using Qdrant vector search.
  * If vector embeddings are rate-limited or unavailable, it automatically falls back to fetching recent active profile facts directly from SQLite.
* **Response Length Control Toggle**: Tester-friendly button selectors on the frontend (`Very Short` = 1 sentence, `Short` = 2-3 sentences, `Medium` = up to 5 sentences).
* **Conflict Resolution**: The memory agent automatically deactivates outdated or contradicting memories when a user updates their preference.
* **Windows Compatibility**: Unicode emojis removed from logs to prevent terminal encoding failures.

---

## Tech Stack

* **Frontend**: Next.js, Tailwind CSS, TypeScript, Zustand (State Management)
* **Backend**: FastAPI, Uvicorn, SQLAlchemy (Async), SQLite
* **Vector Database**: Qdrant Client (Persistent Local Database / In-Memory)
* **LLM Engine**: Groq SDK (`llama-3.3-70b-versatile`)
* **Embeddings**: Google Gemini API (`text-embedding-004`) with safe mock vector fallback.

---

## Installation & Local Setup

### Step 1: Configure Environment Variables
Create a `.env` file in the root folder (or copy `.env.example` to `.env`):
```env
# Groq API Key (Required for chat and memory extraction)
GROQ_API_KEY=your_groq_api_key_here

# Google Gemini API Key (Optional for embeddings fallback)
GOOGLE_API_KEY=your_gemini_api_key_here

DATABASE_URL=sqlite+aiosqlite:///./aethera.db
QDRANT_URL=memory
```

### Step 2: Start the Backend (FastAPI)
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the development server:
   ```bash
   python -m app.main
   ```
   *The Swagger interactive API documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).*

### Step 3: Start the Frontend (Next.js)
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install Node modules:
   ```bash
   npm install
   ```
3. Start the Next.js dev server:
   ```bash
   npm run dev
   ```
   *The user interface will be available at [http://localhost:3000](http://localhost:3000).*

---

## Running Automated Backend Tests

We include a test runner to verify database integrity, Groq connectivity, memory extraction, and fallbacks.

Navigate to the `backend` directory and run:
```bash
python test_services.py
```

---

## License

Open-source under the **MIT License**.
