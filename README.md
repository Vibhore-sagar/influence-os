# Influence OS (Local LLM Scaffold)

MVP scaffold for Influence OS with FastAPI backend + Next.js frontend.
Uses **HuggingFace Transformers (local pipeline)** for text generation (no API keys).

## Run Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Run Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:3000  
Backend API: http://localhost:8000/docs
