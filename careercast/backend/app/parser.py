"""Resume text extraction and spaCy-based parsing utilities."""
import io
import json
import re
from pathlib import Path
from typing import Dict, List

# ── Text extraction ────────────────────────────────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract plain text from PDF bytes using PyMuPDF."""
    try:
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz  # older PyMuPDF alias
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages = [page.get_text() for page in doc]
        doc.close()
        return "\n".join(pages).strip()
    except Exception as exc:
        raise ValueError(f"Could not extract text from PDF: {exc}") from exc


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract plain text from DOCX bytes using python-docx."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [para.text for para in doc.paragraphs]
        return "\n".join(paragraphs).strip()
    except Exception as exc:
        raise ValueError(f"Could not extract text from DOCX: {exc}") from exc


def extract_text(file_bytes: bytes, filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_bytes)
    if ext in (".docx", ".doc"):
        return extract_text_from_docx(file_bytes)
    raise ValueError(f"Unsupported file type: {ext}")


# ── spaCy NLP parsing ──────────────────────────────────────────────────────────

# Broad technical-skill keyword list used for pattern matching.
TECHNICAL_SKILLS_LIST = [
    # Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "c", "ruby",
    "go", "golang", "rust", "swift", "kotlin", "scala", "r", "matlab",
    "php", "perl", "bash", "shell", "sql", "html", "css", "xml",
    # Frameworks / Libraries
    "react", "angular", "vue", "next.js", "node.js", "express", "django",
    "flask", "fastapi", "spring", "spring boot", "hibernate", "laravel",
    "rails", "tensorflow", "pytorch", "keras", "scikit-learn", "pandas",
    "numpy", "matplotlib", "seaborn", "opencv", "nltk", "spacy",
    # Databases
    "mysql", "postgresql", "mongodb", "sqlite", "redis", "oracle",
    "cassandra", "dynamodb", "firebase",
    # Cloud / DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
    "jenkins", "git", "github", "gitlab", "ci/cd", "terraform", "ansible",
    "linux", "unix",
    # Other tools / concepts
    "rest api", "graphql", "microservices", "agile", "scrum", "jira",
    "tableau", "power bi", "excel", "machine learning", "deep learning",
    "nlp", "computer vision", "data science", "data analysis",
    "hadoop", "spark", "kafka", "elasticsearch",
]

EDUCATION_KEYWORDS = [
    "bachelor", "master", "b.tech", "m.tech", "b.e", "m.e", "bsc", "msc",
    "b.sc", "m.sc", "phd", "mba", "diploma", "12th", "10th", "ssc", "hsc",
    "undergraduate", "postgraduate", "university", "college", "institute",
    "engineering", "science", "arts", "commerce", "technology",
]

JOB_ROLE_PATTERNS = [
    r"software\s+engineer", r"software\s+developer", r"web\s+developer",
    r"frontend\s+developer", r"backend\s+developer", r"full[\s-]?stack",
    r"data\s+scientist", r"data\s+analyst", r"data\s+engineer",
    r"machine\s+learning\s+engineer", r"ml\s+engineer", r"ai\s+engineer",
    r"devops\s+engineer", r"cloud\s+engineer", r"system\s+analyst",
    r"product\s+manager", r"project\s+manager", r"business\s+analyst",
    r"ui[\s/]ux\s+designer", r"qa\s+engineer", r"test\s+engineer",
    r"security\s+engineer", r"network\s+engineer", r"database\s+administrator",
    r"intern", r"trainee", r"junior\s+developer", r"senior\s+developer",
    r"lead\s+developer", r"tech\s+lead", r"architect",
]

EXPERIENCE_PATTERNS = [
    r"\d+\+?\s*years?\s+of\s+experience",
    r"\d+\+?\s*years?\s+experience",
    r"experience\s+of\s+\d+\+?\s*years?",
    r"\d+\s*months?\s+experience",
    r"worked\s+(?:at|for|with|as)\s+[\w\s,]+",
    r"(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\s*[-–]\s*(?:present|current|\d{4})",
]


def _load_spacy():
    """Load spaCy model, falling back to a blank English model if needed."""
    import spacy
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        # Model not downloaded – use a blank pipeline (still works for our
        # rule-based patterns, just won't have pre-trained NER).
        return spacy.blank("en")


def parse_resume(text: str) -> Dict[str, List[str]]:
    """
    Rule-based resume parser using spaCy tokenization + keyword/pattern matching.
    Returns a dict with keys: technical_skills, education, job_roles, experience.
    """
    nlp = _load_spacy()
    doc = nlp(text[:50000])  # limit to 50k chars to keep it fast
    lower_text = text.lower()

    # 1. Technical skills – keyword match against full text
    found_skills: List[str] = []
    for skill in TECHNICAL_SKILLS_LIST:
        # Use word-boundary matching (handles "C++" and multi-word skills)
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, lower_text):
            found_skills.append(skill.title() if len(skill) > 3 else skill.upper())

    # 2. Education – sentence-level keyword detection
    education_lines: List[str] = []
    seen_edu = set()
    for sent in doc.sents:
        sent_lower = sent.text.lower()
        if any(kw in sent_lower for kw in EDUCATION_KEYWORDS):
            clean = sent.text.strip()
            if clean and clean not in seen_edu and len(clean) < 300:
                education_lines.append(clean)
                seen_edu.add(clean)
                if len(education_lines) >= 6:
                    break

    # 3. Job roles – regex over full text
    found_roles: List[str] = []
    seen_roles = set()
    for pattern in JOB_ROLE_PATTERNS:
        for match in re.finditer(pattern, lower_text):
            role = match.group().strip().title()
            if role not in seen_roles:
                found_roles.append(role)
                seen_roles.add(role)

    # 4. Experience – regex over full text
    found_experience: List[str] = []
    seen_exp = set()
    for pattern in EXPERIENCE_PATTERNS:
        for match in re.finditer(pattern, lower_text, re.IGNORECASE):
            exp = match.group().strip()
            if exp not in seen_exp and len(exp) < 200:
                found_experience.append(exp)
                seen_exp.add(exp)
                if len(found_experience) >= 8:
                    break

    return {
        "technical_skills": found_skills[:30],
        "education": education_lines[:6],
        "job_roles": found_roles[:10],
        "experience": found_experience[:8],
        "raw_text_preview": text[:500],
    }
