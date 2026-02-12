from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

# --- Core Data Models ---

class CandidateProfile(BaseModel):
    target_role: str = "Software Engineer"
    experience_years: int = 3 # Years of experience
    tech_stack: List[str] = []
    self_declared_weaknesses: List[str] = []

class Section(BaseModel):
    name: str  # Experience, Education, Skills, etc.

class ResumeClaim(BaseModel):
    text: str
    section: str
    risk_label: str = "UNKNOWN"
    risk_score: float = 0.0
    vulnerabilities: List[str] = []
    interview_questions: List[str] = []

class RiskAnalysis(BaseModel):
    claim_risks: List[dict]
    summary: str

class VulnerabilityMap(BaseModel):
    strong_claims: int
    total_claims: int
    strength_ratio: float
    top_weaknesses: List[str]
    interview_focus: List[str]

class ReadinessAnalysis(BaseModel):
    score: float
    level: str
    breakdown: Dict[str, Any]

class GeneratedQuestion(BaseModel):
    question: str
    difficulty: str  # Easy, Medium, Hard
    target_claim: str
    reasoning: str
    expected_answer_points: List[str]

class SkillGapAnalysis(BaseModel):
    explicit_skills: List[str]
    implied_skills: List[str]
    missing_skills: List[str]  # implied but not explicit

class CoachingInsight(BaseModel):
    topic: str
    advice: str
    resources: List[str]



