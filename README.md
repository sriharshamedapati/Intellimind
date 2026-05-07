# IntelliMind — AI Learning Intelligence

> A personalised AI tutor for engineering students — powered by Gemini AI, FastAPI, and Supabase.

---

## Project Structure

```
intellimind/
│
├── frontend/                              ← Open with VS Code Live Server
│   ├── index.html                         ← Landing page
│   │
│   ├── css/                               ← Landing page styles
│   ├── js/                                ← Landing page component scripts
│   │
│   ├── shared/                            ← Shared assets across all pages
│   │   ├── css/
│   │   │   ├── variables.css              ← Design tokens (colors, fonts)
│   │   │   ├── reset.css                  ← CSS reset
│   │   │   └── topbar.css                 ← Common navigation bar
│   │   └── js/
│   │       ├── auth.js                    ← Session guard + sign-out
│   │       ├── config.js                  ← API base URL config
│   │       ├── markdown.js                ← Markdown → HTML renderer
│   │       └── toast.js                   ← Toast notification system
│   │
│   ├── login/                             ← Login page (Supabase Auth)
│   ├── chat/                              ← AI Text Chat (Karthik)
│   ├── voice/                             ← AI Voice Chat
│   ├── doc/                               ← Document Analyser (Srikanth)
│   └── roadmap/                           ← Roadmap Planner (Bhagya)
│
└── backend/                               ← FastAPI Python server
    ├── main.py                            ← App entry point + CORS + router registration
    └── app/
        ├── routes/
        │   ├── chat.py                    ← POST /chat — AI tutor with smart intent detection
        │   ├── doc.py                     ← POST /analyze-doc, POST /doc/chat
        │   ├── roadmap.py                 ← /roadmap/* — AI study plan generator
        │   ├── student.py                 ← GET /student-summary, /student-activity
        │   ├── analytics.py               ← GET /progress/{user_id}
        │   └── debug.py                   ← Dev-only diagnostic endpoints
        │
        └── services/
            ├── gemini.py                  ← Shared Gemini API client (raw HTTP)
            ├── summarizer.py              ← Chat session summarizer + performance scorer
            ├── recommender.py             ← Study topic recommendations
            ├── maya_service.py            ← Maya platform data fetcher
            ├── student_service.py         ← Supabase RPC calls for student data
            ├── hoot_data.py               ← HOOT LSRW data fetcher
            ├── intent.py                  ← Smart intent detection for chat
            └── prompts.py                 ← Prompt templates for chat/voice modes
```

---

## How the App Works

### Login → Chat
```
Student enters roll number on login page
        ↓
authService.js calls Supabase Auth (signInWithPassword)
        ↓
On success → sessionStorage.setItem("im_roll", "23A91A0509")
        ↓
Redirects to chat/index.html
        ↓
FastAPI detects intent → fetches only needed data (Maya/HOOT/Memory)
        ↓
Builds Gemini prompt (Multi-modal) → personalised AI response
```

### Document Analyser (Srikanth)
```
Student navigates to doc/index.html
        ↓
Upload a study document (PDF, DOCX, TXT, MD, CSV)
        ↓
POST /analyze-doc → returns session_id + AI analysis
        ↓
Three-panel workspace: Summary | Split | Chat
```

### Roadmap Planner (Bhagya)
```
Student navigates to roadmap/index.html
        ↓
Select duration (7 / 15 / 21 / 30 days)
        ↓
POST /roadmap/generate → AI creates personalised study plan
```

---

## Running the Project

### Prerequisites
- Python 3.10+
- VS Code with the **Live Server** extension

### 1. Configure the Backend
Create `backend/.env` with `GEMINI_API_KEY`, `SUPABASE_URL`, and `SUPABASE_KEY`.

### 2. Install Dependencies & Start Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Visit the App

| Page              | URL                                                  |
|-------------------|------------------------------------------------------|
| Landing page      | http://127.0.0.1:5501/index.html                     |
| Chat (AI Tutor)   | http://127.0.0.1:5501/chat/index.html                |
| Voice Chat        | http://127.0.0.1:5501/voice/index.html               |
| Document Analyser | http://127.0.0.1:5501/doc/index.html                 |
| Roadmap Planner   | http://127.0.0.1:5501/roadmap/index.html             |

---

## Backend API Endpoints

| Method | Endpoint                              | Description                                      |
|--------|---------------------------------------|--------------------------------------------------|
| POST   | `/chat`                               | AI tutoring with smart intent-based data fetching |
| POST   | `/analyze-doc`                        | Upload study doc → AI summary + session_id       |
| POST   | `/doc/chat`                           | Follow-up Q&A about uploaded document            |
| POST   | `/roadmap/generate`                   | Generate AI study plan (max 3/month)             |
| GET    | `/student-summary/{roll}`             | Student performance summary                      |

---

## Architecture Decisions

### Smart Intent Detection
The chat route detects intent (e.g., `performance`, `maya`, `hoot`) and only fetches relevant data sources, reducing latency and token usage.

### Session-Based Document Chat
Uploaded documents are stored in session memory, allowing for deep follow-up Q&A within the AI tutor context.

### Roadmap Rules
Students can generate max 3 plans per month to encourage focus and consistent progress tracking.
