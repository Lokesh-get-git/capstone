"""
Resume Parser Module.
Extracts text from PDF/text files, parses sections, and extracts claims.
"""

import re
import sys
from pathlib import Path
from typing import BinaryIO, Union

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import get_logger
from new_data_models import ResumeClaim, ParsedResume, CandidateProfile

logger = get_logger(__name__)


# ============================================================
# Text Extraction
# ============================================================

def extract_text_from_pdf(file: Union[BinaryIO, str, Path]) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        file: File-like object, file path string, or Path.
    
    Returns:
        Extracted text as a string.
    """
    from PyPDF2 import PdfReader
    
    try:
        if isinstance(file, (str, Path)):
            reader = PdfReader(str(file))
        else:
            reader = PdfReader(file)
        
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        
        full_text = "\n".join(text_parts)
        logger.info(f"Extracted {len(full_text)} chars from PDF ({len(reader.pages)} pages)")
        return full_text
    
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        raise


def extract_text_from_txt(file: Union[BinaryIO, str, Path]) -> str:
    """
    Extract text from a plain text file.
    
    Args:
        file: File-like object, file path string, or Path.
    
    Returns:
        Text content as a string.
    """
    try:
        if isinstance(file, (str, Path)):
            with open(file, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            content = file.read()
            text = content.decode("utf-8") if isinstance(content, bytes) else content
        
        logger.info(f"Extracted {len(text)} chars from text file")
        return text
    
    except Exception as e:
        logger.error(f"Failed to extract text from file: {e}")
        raise


def extract_text(file: Union[BinaryIO, str, Path], filename: str = "") -> str:
    """
    Auto-detect file type and extract text.
    
    Args:
        file: File object or path.
        filename: Original filename (used for type detection).
    
    Returns:
        Extracted text.
    """
    if isinstance(file, (str, Path)):
        filename = str(file)
    
    if filename.lower().endswith(".pdf"):
        return extract_text_from_pdf(file)
    else:
        return extract_text_from_txt(file)


# ============================================================
# Section Parsing
# ============================================================

# Common resume section headings
SECTION_PATTERNS = [
    r"(?i)^(summary|profile|objective|about\s*me)",
    r"(?i)^(experience|work\s*experience|professional\s*experience|employment)",
    r"(?i)^(education|academic|qualifications)",
    r"(?i)^(skills|technical\s*skills|core\s*competencies|technologies)",
    r"(?i)^(projects|personal\s*projects|key\s*projects)",
    r"(?i)^(certifications?|licenses?)",
    r"(?i)^(achievements?|accomplishments?|awards?)",
    r"(?i)^(publications?|research)",
    r"(?i)^(volunteer|community|extracurricular)",
    r"(?i)^(interests?|hobbies)",
    r"(?i)^(references?)",
    r"(?i)^(languages?)",
]


def parse_resume_sections(text: str) -> dict[str, str]:
    """
    Split resume text into named sections.
    
    Detects section headings by looking for lines that match common
    resume section names, then groups text under each heading.
    
    Args:
        text: Full resume text.
    
    Returns:
        Dictionary of section_name -> section_text.
    """
    lines = text.split("\n")
    sections = {}
    current_section = "header"  # Text before any section heading
    current_lines = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            current_lines.append("")
            continue
        
        # Check if this line is a section heading
        is_heading = False
        for pattern in SECTION_PATTERNS:
            if re.match(pattern, stripped):
                # Save the previous section
                section_text = "\n".join(current_lines).strip()
                if section_text:
                    sections[current_section] = section_text
                
                # Start new section
                current_section = re.match(pattern, stripped).group(1).lower().strip()
                # Normalize section names
                if "experience" in current_section or "employment" in current_section:
                    current_section = "experience"
                elif "education" in current_section or "academic" in current_section:
                    current_section = "education"
                elif "skill" in current_section or "competenc" in current_section or "technolog" in current_section:
                    current_section = "skills"
                elif "project" in current_section:
                    current_section = "projects"
                elif "certif" in current_section:
                    current_section = "certifications"
                elif "achieve" in current_section or "accomplish" in current_section or "award" in current_section:
                    current_section = "achievements"
                elif "summary" in current_section or "profile" in current_section or "objective" in current_section or "about" in current_section:
                    current_section = "summary"
                
                current_lines = []
                is_heading = True
                break
        
        if not is_heading:
            current_lines.append(stripped)
    
    # Save last section
    section_text = "\n".join(current_lines).strip()
    if section_text:
        sections[current_section] = section_text
    
    logger.info(f"Parsed {len(sections)} sections: {list(sections.keys())}")
    return sections


# ============================================================
# Claim Extraction
# ============================================================

def _split_into_sentences(text: str) -> list[str]:
    """Split text into sentences."""
    # Split on sentence-ending punctuation followed by space/newline
    sentences = re.split(r'(?<=[.!?])\s+|\n+', text)
    # Also split on bullet points
    expanded = []
    for s in sentences:
        # Split bullet points (•, -, *, numbered)
        parts = re.split(r'(?:^|\n)\s*(?:[•\-\*]|\d+[.)]\s)', s)
        expanded.extend(parts)
    
    # Clean up (filter out short fragments like dates, headers)
    result = []
    for s in expanded:
        s = s.strip()
        if not s: continue
        
        words = s.split()
        if len(words) < 5: continue # Slightly stricter
        
        # Heuristic: If it's mostly capitalized words and short, it's likely a header
        cap_words = [w for w in words if w[0].isupper()]
        if len(cap_words) / len(words) > 0.8 and len(words) < 10:
            continue
            
        result.append(s)
    return result


def _classify_claim_type(text: str) -> str:
    """Classify a claim as quantitative, qualitative, technical, or soft_skill."""
    text_lower = text.lower()
    
    # Quantitative: contains numbers, percentages, metrics
    if re.search(r'\d+%|\d+\s*(users?|customers?|clients?|team|members?|engineers?|people)', text_lower):
        return "quantitative"
    if re.search(r'\$\d+|\d+x|\d+\s*(million|billion|thousand|k\b)', text_lower):
        return "quantitative"
    
    # Technical: contains tech keywords
    tech_keywords = [
        "python", "java", "javascript", "react", "node", "sql", "aws", "docker",
        "kubernetes", "api", "database", "algorithm", "machine learning", "ai",
        "framework", "library", "deployed", "implemented", "architected",
        "built", "developed", "designed", "automated", "optimized", "integrated",
        "microservice", "cloud", "devops", "ci/cd", "git", "agile", "scrum"
    ]
    if any(kw in text_lower for kw in tech_keywords):
        return "technical"
    
    # Soft skill keywords
    soft_keywords = [
        "led", "managed", "mentored", "collaborated", "communicated",
        "leadership", "teamwork", "problem-solving", "presented",
        "stakeholder", "cross-functional", "initiative"
    ]
    if any(kw in text_lower for kw in soft_keywords):
        return "soft_skill"
    
    return "qualitative"


def extract_claims(sections: dict[str, str]) -> list[ResumeClaim]:
    """
    Extract individual claims from resume sections.
    
    Each sentence/bullet point becomes a claim with type classification
    and section attribution.
    
    Args:
        sections: Dictionary of section_name -> section_text.
    
    Returns:
        List of ResumeClaim objects.
    """
    claims = []
    
    for section_name, section_text in sections.items():
        # Skip header section (usually just name/contact info)
        if section_name == "header":
            continue
        
        sentences = _split_into_sentences(section_text)
        
        for sentence in sentences:
            claim_type = _classify_claim_type(sentence)
            
            claim = ResumeClaim(
                text=sentence,
                section=section_name,
                claim_type=claim_type,
                confidence=0.5,  # Will be updated by NLP clarity scorer
                risk_level="medium",  # Will be updated by ML classifier
            )
            claims.append(claim)
    
    logger.info(f"Extracted {len(claims)} claims from {len(sections)} sections")
    return claims


# ============================================================
# Full Parse Pipeline
# ============================================================

def parse_resume_text(text: str, profile: CandidateProfile = None) -> ParsedResume:
    """
    Parse resume from raw text string (no file I/O).
    
    Args:
        text: Raw resume text content.
        profile: Optional candidate profile to attach.
    
    Returns:
        ParsedResume with raw text, sections, claims, and profile.
    """
    sections = parse_resume_sections(text)
    claims = extract_claims(sections)
    
    result = ParsedResume(
        raw_text=text,
        sections=sections,
        claims=claims,
        candidate_profile=profile,
    )
    
    logger.info(f"Resume parsed from text: {len(text)} chars, {len(sections)} sections, {len(claims)} claims")
    return result


def parse_resume(file: Union[BinaryIO, str, Path], filename: str = "",
                 profile: CandidateProfile = None) -> ParsedResume:
    """
    Full resume parsing pipeline: extract text -> parse sections -> extract claims.
    
    Args:
        file: Resume file (PDF or text).
        filename: Original filename for type detection.
        profile: Optional candidate profile to attach.
    
    Returns:
        ParsedResume with raw text, sections, claims, and profile.
    """
    # Step 1: Extract text
    raw_text = extract_text(file, filename)
    
    # Step 2: Parse sections
    sections = parse_resume_sections(raw_text)
    
    # Step 3: Extract claims
    claims = extract_claims(sections)
    
    result = ParsedResume(
        raw_text=raw_text,
        sections=sections,
        claims=claims,
        candidate_profile=profile,
    )
    
    logger.info(f"Resume parsed: {len(raw_text)} chars, {len(sections)} sections, {len(claims)} claims")
    return result
