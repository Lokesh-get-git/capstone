from typing import TypedDict, List, Dict, Any, Annotated
import operator
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
from models.data_models import (
    ResumeClaim, RiskAnalysis, ReadinessAnalysis, 
    VulnerabilityMap, GeneratedQuestion, CoachingInsight, SkillGapAnalysis, CandidateProfile
)

class AgentState(TypedDict):
    # --- Input ---
    resume_text: str
    job_description: str
    candidate_profile: CandidateProfile # Added
  # optional

    # --- Analysis Layer (Analyst Agent) ---
    claims: List[ResumeClaim]
    risk_analysis: RiskAnalysis
    readiness_analysis: ReadinessAnalysis
    vulnerability_map: VulnerabilityMap
    skill_gap_analysis: SkillGapAnalysis

    # --- Strategy Layer (Strategist Agent) ---
    interview_strategy: str
    focus_areas: List[str]

    # --- Planning Layer (Planner Agent) ---
    question_plan: List[str]  # sequential topics

    # --- execution Layer (Validator Agent) ---
    generated_questions: List[GeneratedQuestion]
    
    # --- Coaching Layer (Coach Agent) ---
    coaching_insights: List[CoachingInsight]

    # --- Meta ---
    validation_results: List[Dict[str, Any]] # Added for validator feedback
    retry_count: int # For generator loop
    messages: Annotated[List[BaseMessage], add_messages]
    errors: List[str]
    total_cost: Annotated[float, operator.add]