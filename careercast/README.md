# CareerCast – Week 1

**AI-Powered Career Path Prediction and Recommendation System**

## Week 1 Modules Completed

| Module | Status |
|---|---|
| User Registration & Login (JWT) | ✅ |
| Protected Dashboard | ✅ |
| User Profile (CRUD) | ✅ |
| Resume Upload (PDF / DOCX) | ✅ |
| spaCy Resume Parsing | ✅ |
| SQLite Database | ✅ |

---

## Project Structure

```
careercast/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          ← FastAPI entry point
│   │   ├── database.py      ← SQLAlchemy + SQLite setup
│   │   ├── models.py        ← ORM models (User, Profile, Resume)
│   │   ├── schemas.py       ← Pydantic request/response schemas
│   │   ├── auth.py          ← JWT + bcrypt helpers
│   │   ├── parser.py        ← PDF/DOCX extraction + spaCy parsing
│   │   └── routers/
│   │       ├── auth.py      ← /api/auth/register, /api/auth/login
│   │       ├── profile.py   ← /api/profile/me  (GET, POST, PUT)
│   │       └── resume.py    ← /api/resume/upload, /latest, /apply
│   ├── uploads/             ← Uploaded resume files
│   ├── careercast.db        ← SQLite database (auto-created)
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/
    ├── src/
    │   ├── App.jsx           ← Routes + auth guards
    │   ├── main.jsx
    │   ├── api.js            ← Axios instance with JWT interceptor
    │   ├── index.css         ← Tailwind base + custom styles
    │   ├── context/
    │   │   └── AuthContext.jsx
    │   ├── components/
    │   │   ├── Sidebar.jsx
    │   │   ├── TopNav.jsx
    │   │   └── DashboardLayout.jsx
    │   └── pages/
    │       ├── LoginPage.jsx
    │       ├── RegisterPage.jsx
    │       ├── DashboardPage.jsx
    │       ├── ProfilePage.jsx
    │       └── ResumeUploadPage.jsx
    ├── tailwind.config.js
    ├── vite.config.js
    └── package.json
```

---

## Prerequisites

- **Python 3.11 – 3.14**
- **Node.js 18+**

---

## Installation

### 1. Backend

```powershell
cd careercast\backend

# Install Python dependencies
pip install -r requirements.txt

# Download spaCy English model
python -m spacy download en_core_web_sm
```

> **Python 3.14 users:** If pydantic-core fails to build, run:
> ```
> pip install "pydantic>=2.9" "pydantic-settings>=2.4"
> ```

> **bcrypt note:** `bcrypt==4.0.1` is pinned for passlib compatibility.

### 2. Frontend

```powershell
cd careercast\frontend
npm install
```

---

## Running the Application

Open **two terminals** and run each command in a separate one.

### Terminal 1 — Backend

```powershell
cd careercast\backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: http://localhost:8000  
Interactive docs: http://localhost:8000/docs

### Terminal 2 — Frontend

```powershell
cd careercast\frontend
npm run dev
```

Open the app at: http://localhost:5173

---

## Usage Flow

1. Open http://localhost:5173
2. Click **Create Account** and register
3. You are automatically logged in and redirected to the Dashboard
4. Click **Complete Profile** → fill in education and skills → **Save Profile**
5. Click **Upload Resume** → drag & drop or browse for a PDF/DOCX file
6. Review extracted information, make corrections → **Save to Profile**
7. Return to Dashboard to see your updated profile summary

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | /api/auth/register | Register new user |
| POST | /api/auth/login | Login and receive JWT |
| GET  | /api/profile/me | Get current user's profile |
| POST | /api/profile/me | Create or replace profile |
| PUT  | /api/profile/me | Partial update profile |
| POST | /api/resume/upload | Upload + parse resume |
| GET  | /api/resume/latest | Get most recent resume |
| GET  | /api/resume/all | List all uploaded resumes |
| POST | /api/resume/{id}/apply | Save parsed data to profile |

---

## Database

SQLite file: `backend/careercast.db`  
Created automatically on first run.

Tables: `users`, `profiles`, `resumes`

---

## Known Limitations

1. **Image-only PDFs** (scanned documents) cannot be parsed — text extraction requires a text-based PDF. An error message is shown and manual entry is offered.
2. **spaCy model** used is `en_core_web_sm` (small model). Education and experience extraction is rule-based, not NER-trained on resume data.
3. **Session persistence** uses `localStorage`. Clearing browser storage will log the user out. The backend JWT is valid for 8 hours.
4. **No email verification** — users can register with any email format.
5. **Single user per device** — the frontend stores one token; multiple tabs for different users are not supported.
