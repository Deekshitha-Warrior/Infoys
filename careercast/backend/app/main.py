"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import auth, profile, resume

# Create all DB tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CareerCast API",
    version="1.0.0",
    description="Week 1 – Authentication, Profile, and Resume parsing",
)

# CORS – allow the React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
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


@app.get("/")
def root():
    return {"message": "CareerCast API is running", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok"}
