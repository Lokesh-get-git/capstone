"""
Pydantic Data Models.
Defines all structured data types used throughout the system.
"""

from pydantic import BaseModel, Field
from typing import Optional


class CandidateProfile(BaseModel):
    """Candidate's self-declared profile information."""
    name: str = Field(description="Candidate's full name")
    target_role: str = Field(description="Role they are applying for")
    years_experience: int = Field(description="Total years of professional experience")
    tech_stack: list[str] = Field(default_factory=list, description="Technologies the candidate knows")
    strengths: list[str] = Field(default_factory=list, description="Self-declared strengths")
    weaknesses: list[str] = Field(default_factory=list, description="Self-declared weaknesses")


class ResumeClaim(BaseModel):
    """A single claim/statement extracted from a resume."""
    text: str = Field(description="The claim text as extracted from the resume")
    section: str = Field(description="Resume section: experience, skills, education, projects, etc.")
    claim_type: str = Field(description="Type: quantitative, qualitative, technical, soft_skill")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0,
                              description="How clearly the claim is stated (0-1)")
    risk_level: str = Field(default="medium",
                            description="Risk of being challenged: low, medium, high")
    risk_reasons: list[str] = Field(default_factory=list,
                                    description="Reasons why this claim is risky")


class ParsedResume(BaseModel):
    """Result of parsing a resume document."""
    raw_text: str = Field(description="Full raw text extracted from the resume")
    sections: dict[str, str] = Field(default_factory=dict,
                                     description="Section name -> section text")
    claims: list[ResumeClaim] = Field(default_factory=list,
                                     description="All extracted claims")
    candidate_profile: Optional[CandidateProfile] = Field(default=None,
                                                          description="Linked candidate profile")


class InterviewQuestion(BaseModel):
    """A generated interview question targeting a resume claim."""
    question: str = Field(description="The interview question text")
    category: str = Field(description="Category: technical, behavioral, situational, clarification")
    difficulty: str = Field(default="medium", description="Difficulty: easy, medium, hard")
    target_claim: str = Field(description="The resume claim this question targets")
    reasoning: str = Field(description="Why this question was generated")


class VulnerabilityItem(BaseModel):
    """A single entry in the resume vulnerability map."""
    claim_text: str = Field(description="The vulnerable claim")
    risk_level: str = Field(description="low, medium, or high")
    risk_reasons: list[str] = Field(default_factory=list, description="Why this is risky")
    section: str = Field(description="Which resume section this comes from")
    suggested_improvement: str = Field(default="", description="How to strengthen this claim")


class ReadinessReport(BaseModel):
    """Complete interview readiness analysis report."""
    overall_score: float = Field(ge=0.0, le=100.0,
                                 description="Overall interview readiness score (0-100)")
    category_scores: dict[str, float] = Field(
        default_factory=dict,
        description="Per-category breakdowns, e.g. technical: 75, behavioral: 60"
    )
    vulnerability_map: list[VulnerabilityItem] = Field(
        default_factory=list,
        description="Weak claims with risk levels and reasons"
    )
    questions: list[InterviewQuestion] = Field(
        default_factory=list,
        description="Curated interview question set"
    )
    coaching_insights: list[str] = Field(
        default_factory=list,
        description="Personalized preparation recommendations"
    )
    reasoning: str = Field(
        default="",
        description="Explanation of reasoning behind scores and questions"
    )
