"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import auth, profile, resume, intelligence

# Create all DB tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CareerCast API",
    version="2.0.0",
    description="Career profiles, spaCy resume parsing, trained career prediction and Top-K recommendations",
)

# CORS – allow the React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(resume.router)
app.include_router(intelligence.router)


@app.get("/")
def root():
    return {"message": "CareerCast API is running", "version": "2.0.0"}


@app.get("/health")
def health():
    return {"status": "ok"}
