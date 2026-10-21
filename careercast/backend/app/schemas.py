"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    confirm_password: str

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    email: str


class UserOut(BaseModel):
    user_id: int
    name: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Profile ───────────────────────────────────────────────────────────────────

class ProfileBase(BaseModel):
    qualification: Optional[str] = None
    degree: Optional[str] = None
    specialization: Optional[str] = None
    institution: Optional[str] = None
    graduation_year: Optional[str] = None
    technical_skills: Optional[List[str]] = None
    soft_skills: Optional[List[str]] = None
    work_experience: Optional[str] = None
    previous_role: Optional[str] = None
    certifications: Optional[str] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileOut(ProfileBase):
    profile_id: int
    user_id: int
    name: str
    email: str

    model_config = {"from_attributes": True}


# ── Resume ────────────────────────────────────────────────────────────────────

class ParsedResumeInfo(BaseModel):
    technical_skills: List[str] = []
    education: List[str] = []
    job_roles: List[str] = []
    experience: List[str] = []
    raw_text_preview: str = ""


class ResumeOut(BaseModel):
    resume_id: int
    filename: str
    upload_date: datetime
    parsed_information: Optional[ParsedResumeInfo] = None

    model_config = {"from_attributes": True}


class ApplyParsedData(BaseModel):
    technical_skills: Optional[List[str]] = None
    soft_skills: Optional[List[str]] = None
    education: Optional[List[str]] = None
    job_roles: Optional[List[str]] = None
    experience: Optional[List[str]] = None
