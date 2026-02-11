import re
from pathlib import Path
from typing import BinaryIO, Union, Dict

import pdfplumber
from utils.logger import get_logger

logger = get_logger(__name__)

# =========================================================
# ---------------- FILE HANDLING ---------------------------
# =========================================================

def _reset_stream(file):
    """Reset file pointer (important for FastAPI UploadFile)."""
    try:
        if hasattr(file, "seek"):
            file.seek(0)
    except Exception:
        pass
def normalize_pdf_text(text: str) -> str:
    """
    Safe normalization for PDF resumes.
    Only fixes extraction artifacts — NEVER rewrites real words.
    """

    # --- Merge split acronyms: "AP I" -> "API"
    text = re.sub(r'\b([A-Z])\s+([A-Z])\s+([A-Z])\b', r'\1\2\3', text)
    text = re.sub(r'\b([A-Z])\s+([A-Z])\b', r'\1\2', text)

    # --- Fix hyphen spacing: "real - time" -> "real-time"
    text = re.sub(r'\s*-\s*', '-', text)

    # --- Add missing space after commas: "FastAPI,SQLAlchemy"
    text = re.sub(r',([A-Za-z])', r', \1', text)

    # --- Clean punctuation spacing
    text = re.sub(r'\s+,', ',', text)
    text = re.sub(r'\s+\.', '.', text)

    # --- Normalize bullets
    text = text.replace("●", "-")
    text = text.replace("•", "-")

    # --- Collapse multiple spaces
    text = re.sub(r' {2,}', ' ', text)

    return text

def extract_text_from_pdf(file: Union[BinaryIO, str, Path]) -> str:
    """
    Extract text using pdfplumber (much better for resumes than PyPDF2)
    """
    try:
        _reset_stream(file)

        text_parts = []

        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text(x_tolerance=2, y_tolerance=2)
                if page_text:
                    text_parts.append(page_text)

        full_text = "\n".join(text_parts)

        # normalize extracted text
        full_text = normalize_pdf_text(full_text)


        logger.info(f"Extracted {len(full_text)} characters from PDF")
        return full_text


    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        raise

def extract_text_from_txt(file: Union[BinaryIO, str, Path]) -> str:
    """Read raw text from a TXT file."""
    try:
        if isinstance(file, (str, Path)):
            with open(file, "r", encoding="utf-8") as f:
                return f.read()
        else:
            _reset_stream(file)
            content = file.read()
            return content.decode("utf-8") if isinstance(content, bytes) else content
    except Exception as e:
        logger.error(f"Failed to extract text from TXT: {e}")
        raise

def extract_text(file: Union[BinaryIO, str, Path], filename: str = "") -> str:
    """Auto detect file type."""
    filename = filename.lower()

    if filename.endswith(".pdf") or (isinstance(file, str) and file.lower().endswith(".pdf")):
        return extract_text_from_pdf(file)

    return extract_text_from_txt(file)


# =========================================================
# ---------------- SECTION DETECTION -----------------------
# =========================================================

SECTION_PATTERNS = [
    r"(?i)(summary|profile|objective|about\s*me)",
    r"(?i)(experience|work\s*experience|professional\s*experience|employment)",
    r"(?i)(education|academic|qualifications)",
    r"(?i)(skills|technical\s*skills|core\s*competencies|technologies)",
    r"(?i)(projects|personal\s*projects|key\s*projects)",
    r"(?i)(certifications?|licenses?)",
]

SECTION_NORMALIZATION = {
    "summary": "summary",
    "profile": "summary",
    "objective": "summary",
    "about me": "summary",

    "experience": "experience",
    "work experience": "experience",
    "professional experience": "experience",
    "employment": "experience",

    "education": "education",
    "academic": "education",
    "qualifications": "education",

    "skills": "skills",
    "technical skills": "skills",
    "core competencies": "skills",
    "technologies": "skills",

    "projects": "projects",
    "personal projects": "projects",
    "key projects": "projects",

    "certification": "certifications",
    "certifications": "certifications",
    "license": "certifications",
    "licenses": "certifications",
}

def looks_like_heading(line: str, next_lines: list[str]) -> bool:
    """
    Decide if a line is a true section heading using context.
    """

    clean = line.strip()

    # too long = not a heading
    if len(clean) > 40:
        return False

    # must contain letters
    if not re.search(r"[A-Za-z]", clean):
        return False

    # reject name lines (2 words, capitalized)
    if re.match(r"^[A-Z][a-z]+ [A-Z][a-z]+$", clean):
        return False

    # reject GPA and similar metadata
    if re.search(r"gpa|cgpa|grade", clean, re.I):
        return False

    # check if next lines look like bullet content
    bullet_count = 0
    for nl in next_lines[:3]:
        if nl.strip().startswith(("-", "•", "*")):
            bullet_count += 1

    # a real section usually introduces bullets
    if bullet_count >= 1:
        return True

    return False

# remove contact junk
CONTACT_PATTERNS = [
    r"linkedin\.com",
    r"github\.com",
    r"@\w+\.",
    r"\+?\d{8,}",
]

def parse_resume_sections(text: str) -> Dict[str, Dict]:
    """
    Split resume into logical sections using contextual heading detection.
    Returns:
    {
        section_name: {
            "text": "...",
            "type": "skills" | "paragraph"
        }
    }
    """

    lines = text.split("\n")
    sections = {}
    current_section = "header"
    current_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        # preserve spacing (important for bullets)
        if not stripped:
            current_lines.append("")
            continue

        # remove contact info
        if any(re.search(p, stripped, re.I) for p in CONTACT_PATTERNS):
            continue

        detected_section = None

        # ---------- known headings ----------
        for pattern in SECTION_PATTERNS:
            match = re.search(pattern, stripped)
            if match:
                raw = match.group(1).lower().strip()
                detected_section = SECTION_NORMALIZATION.get(raw, raw)
                break

        # ---------- contextual unknown headings ----------
        if not detected_section:
            next_lines = lines[i+1:i+4]
            if looks_like_heading(stripped, next_lines):
                detected_section = stripped.lower()

        # ---------- switch section ----------
        if detected_section:
            if current_lines:
                sections[current_section] = {
                    "text": "\n".join(current_lines).strip(),
                    "type": "skills" if current_section == "skills" else "paragraph",
                }
            current_section = detected_section
            current_lines = []
        else:
            current_lines.append(stripped)

    # save last section
    if current_lines:
        sections[current_section] = {
            "text": "\n".join(current_lines).strip(),
            "type": "skills" if current_section == "skills" else "paragraph",
        }

    # fallback if nothing detected
    if len(sections) <= 1:
        logger.warning("No clear headings detected — using full_text fallback")
        return {"full_text": {"text": text.strip(), "type": "paragraph"}}

    logger.info(f"Parsed {len(sections)} sections: {list(sections.keys())}")
    return sections

# =========================================================
# ---------------- CLAIM EXTRACTION ------------------------
# =========================================================

DATE_PATTERN = r"(19|20)\d{2}"

JOB_HEADER_PATTERN = re.compile(
    rf"""
    ^(
        .*?\|\s*.*?\|\s*{DATE_PATTERN}.*$ |  # Title | Company | Year
        .*?\|\s*{DATE_PATTERN}.*$        |   # Title | Year
        .+?\s-\s.+$                      |   # Project - Name
        .+?\s@\s.+$                      |   # Title @ Company
        ^[A-Z][A-Za-z0-9\s&]{{2,40}}$       # Short title lines (Project names)
    )
    """,
    re.VERBOSE
)

def looks_like_job_header(line: str) -> bool:
    line = line.strip()

    if len(line) < 6:
        return False

    # never treat bullets as headers
    if re.match(r'^\s*[•\-\*]', line):
        return False

    # sentences are not headers
    if line.endswith(('.', ',', ';')):
        return False

    # very long lines are not headers
    if len(line.split()) > 8:
        return False

    # contains verbs → probably a sentence
    if re.search(r"\b(implemented|developed|built|designed|led|optimized)\b", line, re.I):
        return False

    return bool(JOB_HEADER_PATTERN.match(line))

def _split_into_sentences(text: str) -> list[str]:
    """
    Split text into resume claims.
    Bullet points are treated as primary claims.
    Sentences are fallback when bullets are absent.
    """

    lines = text.split("\n")
    claims = []
    current_bullet = []

    bullet_pattern = re.compile(r'^\s*[•\-\*]\s+')

    # -------- Step 1: Group multi-line bullets --------
    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        # -------- ENTRY HEADER (hard boundary) --------
        if looks_like_job_header(stripped):
            if current_bullet:
                claims.append(" ".join(current_bullet))
                current_bullet = []
            continue

        # -------- BULLET --------
        if bullet_pattern.match(stripped):
            if current_bullet:
                claims.append(" ".join(current_bullet))
                current_bullet = []

            stripped = bullet_pattern.sub("", stripped)
            current_bullet.append(stripped)
            continue

        # -------- CONTINUATION --------
        if current_bullet:
            current_bullet.append(stripped)
        else:
            # only keep standalone lines that look like real sentences
            if stripped.endswith('.'):
                claims.append(stripped)



    if current_bullet:
        claims.append(" ".join(current_bullet))

    # -------- Step 2: sentence fallback --------
    final_claims = []
    for claim in claims:
        # if claim already long enough, keep it
        if len(claim.split()) > 6:
            final_claims.append(claim)
        else:
            # split into sentences
            sentences = re.split(r'(?<=[.!?])\s+', claim)
            final_claims.extend(sentences)

    # -------- Step 3: cleanup --------
    cleaned = []
    for c in final_claims:
        c = c.strip()

        # filter noise
        if len(c) < 10:
            continue
        if re.match(r'^\d{4}\s*-\s*\d{4}$', c):
            continue

        cleaned.append(c)

    return cleaned

ACTION_VERBS = [
    "built","developed","implemented","designed","led","created","optimized",
    "improved","reduced","increased","deployed","architected","mentored",
    "automated","analyzed","managed","integrated"
]
def is_role_header(text: str) -> bool:
    """
    Detect job title lines like:
    Software Engineer | Google | 2023
    """

    t = text.strip().lower()

    # Must contain a year
    if not re.search(r'(19|20)\d{2}', t):
        return False

    # Typical job header patterns
    if "|" in t or " - " in t or "@" in t:
        if not any(v in t for v in ACTION_VERBS):
            return True

    return False


def is_noise_claim(text: str) -> bool:
    """
    Check if a claim is just noise (headers, dates, meta).
    """
    if is_role_header(text):
        return True
    
    # single project titles (no verbs)
    t = text.strip().lower()
    if len(t.split()) <= 6 and not any(v in t for v in ACTION_VERBS):
        if not t.endswith('.'):
            return True
            
    return False

def normalize_section(section_name: str) -> str:
    """
    Map parser sections into semantic sections used by the system.
    """

    s = section_name.lower().strip()

    # tech stack pseudo-sections -> projects
    if s.startswith("(") and "," in s:
        return "projects"

    # safety: technology-only section names
    if any(t in s for t in ["python", "fastapi", "sql", "docker", "ml"]):
        if len(s.split()) <= 5:
            return "projects"

    return section_name

def extract_claims_from_sections(sections: dict[str, dict]) -> list[dict]:
    """
    Convert parsed sections into a flat list of raw claims.
    """

    all_claims = []

    SKIP_SECTIONS = {"header", "skills", "education", "certifications"}


    for section_name, section_data in sections.items():

        if section_name in SKIP_SECTIONS:
            continue

        text = section_data.get("text", "")
        if not text:
            continue

        claims = _split_into_sentences(text)

        for claim in claims:
            if is_noise_claim(claim):
                continue

            normalized_section = normalize_section(section_name)

            all_claims.append({
                "text": claim,
                "section": normalized_section
            })


    logger.info(f"Extracted {len(all_claims)} raw claims from sections")
    return all_claims
