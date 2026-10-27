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


class UserNameUpdate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be empty")
        if len(value) > 255:
            raise ValueError("Name must be 255 characters or fewer")
        return value


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

    @field_validator("technical_skills", "soft_skills")
    @classmethod
    def validate_skills(cls, values):
        if values is None:
            return None
        if len(values) > 100:
            raise ValueError("Use no more than 100 skills per category")
        result = []
        for value in values:
            value = value.strip()
            if not value or len(value) > 80:
                raise ValueError("Each skill must contain 1 to 80 characters")
            if value.lower() not in [s.lower() for s in result]:
                result.append(value)
        return result

    @field_validator("graduation_year")
    @classmethod
    def validate_year(cls, value):
        if value in (None, ""):
            return value
        if not value.isdigit() or not 1950 <= int(value) <= datetime.now().year + 15:
            raise ValueError("Enter a valid graduation year")
        return value

    @field_validator(
        "qualification",
        "degree",
        "specialization",
        "institution",
        "work_experience",
        "previous_role",
        "certifications",
    )
    @classmethod
    def validate_profile_text(cls, value):
        if value and len(value) > 500:
            raise ValueError("Keep this field within 500 characters")
        return value.strip() if value else value


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
