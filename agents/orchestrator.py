import logging
from typing import Literal
from langgraph.graph import StateGraph, END
from agents.state import AgentState
from models.data_models import (
    RiskAnalysis, ReadinessAnalysis, VulnerabilityMap, SkillGapAnalysis, CandidateProfile
)
from agents.resume_analyst import resume_analyst_node
from agents.question_strategist import question_strategist_node
from agents.difficulty_planner import difficulty_planner_node
from agents.question_generator import question_generator_node
from agents.validator import validator_node
from agents.coach import coach_node

logger = logging.getLogger(__name__)

# --- Conditional Logic ---
def route_after_validator(state: AgentState) -> Literal["question_generator", "coach"]:
    """
    Decides whether to retry generation or move to coaching.
    """
    results = state.get("validation_results", [])
    failed_count = sum(1 for v in results if v.get("status") == "FAIL")
    retry_count = state.get("retry_count", 0)
    MAX_RETRIES = 3
    
    if failed_count > 0 and retry_count < MAX_RETRIES:
        logger.info(f"Validation failed ({failed_count} errors). Retrying (Count: {retry_count + 1}).")
        return "question_generator"
    
    if failed_count > 0:
        logger.warning("Max retries reached. Proceeding with failures.")
    else:
        logger.info("Validation passed. Proceeding.")
        
    return "coach"

def entry_node(state: AgentState):
    """Entry point to initialize retry count if needed (usually handled in init)."""
    return {"retry_count": 0}

# --- Graph Construction ---
def build_interview_graph():
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("entry", entry_node) # Explicit entry to ensure clean state
    workflow.add_node("resume_analyst", resume_analyst_node)
    workflow.add_node("question_strategist", question_strategist_node)
    workflow.add_node("difficulty_planner", difficulty_planner_node)
    
    # Generator wraps the logic to increment retry count could be done here or in node
    # But for now, we just rely on state. We need a node that increments retry...
    # Actually, we can update retry_count inside the generator or validator.
    # Let's create a wrapper for generator to increment count if coming from validator?
    # Or just use the global state.
    
    workflow.add_node("question_generator", question_generator_node)
    workflow.add_node("validator", validator_node)
    workflow.add_node("coach", coach_node)
    
    # Add Edges
    workflow.set_entry_point("entry")
    workflow.add_edge("entry", "resume_analyst")
    workflow.add_edge("resume_analyst", "question_strategist")
    workflow.add_edge("question_strategist", "difficulty_planner")
    workflow.add_edge("difficulty_planner", "question_generator")
    workflow.add_edge("question_generator", "validator")
    
    # Conditional Edge
    workflow.add_conditional_edges(
        "validator",
        route_after_validator
    )
    
    workflow.add_edge("coach", END)
    
    return workflow.compile()

# --- Execution Wrapper ---
def run_interview_pipeline(
    resume_text: str, 
    candidate_profile: CandidateProfile, 
    job_description: str = ""
) -> dict:
    """
    Executes the LangGraph workflow.

    Args:
        resume_text (str): The raw text of the resume.
        candidate_profile (CandidateProfile): User's role, years of exp, and declared weaknesses.
        job_description (str, optional): Job description text. Defaults to "".
    """
    logger.info(f"Starting LangGraph Pipeline for Role: {candidate_profile.target_role}")
    
    # Initialize State
    initial_state = AgentState(
        resume_text=resume_text,
        job_description=job_description,
        candidate_profile=candidate_profile,
        claims=[],
        risk_analysis=RiskAnalysis(claim_risks=[], summary="Pending"),
        readiness_analysis=ReadinessAnalysis(score=0.0, level="Pending", breakdown={}),
        vulnerability_map=VulnerabilityMap(strong_claims=0, total_claims=0, strength_ratio=0.0, top_weaknesses=[], interview_focus=[]),
        skill_gap_analysis=SkillGapAnalysis(explicit_skills=[], implied_skills=[], missing_skills=[]),
        interview_strategy="",
        focus_areas=[],
        question_plan=[],
        generated_questions=[],
        coaching_insights=[],
        validation_results=[],
        retry_count=0,
        messages=[],
        errors=[],
        total_cost=0.0
    )
    
    app = build_interview_graph()
    
    # Run the graph
    # invoke returns the final state
    final_state = app.invoke(initial_state)
    
    logger.info("LangGraph Pipeline Complete.")
    
    
    final_cost = final_state.get("total_cost", 0.0) 

    
    try:
        from services.cost_tracker import CostTracker, LOG_FILE
        from datetime import datetime

        
        with open(LOG_FILE, "a", encoding="utf-8") as f:
             f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [PIPELINE_COMPLETE] TOTAL SESSION COST: ${final_cost:.5f}\n")
             f.write("-" * 50 + "\n")
    except Exception as e:
        logger.error(f"Failed to log final cost: {e}")

    return {
        "readiness_analysis": final_state["readiness_analysis"].model_dump(),
        "risk_analysis": final_state["risk_analysis"].model_dump(),
        "vulnerability_map": final_state["vulnerability_map"].model_dump(),
        "skill_gaps": final_state["skill_gap_analysis"].model_dump(),
        "strategy": final_state["interview_strategy"],
        "question_plan": final_state["question_plan"],
        "questions": [q.model_dump() for q in final_state["generated_questions"]],
        "coaching_insights": [c.model_dump() for c in final_state["coaching_insights"]],
        "claims": [c.model_dump() for c in final_state["claims"]],
        "total_cost": final_cost
    }
