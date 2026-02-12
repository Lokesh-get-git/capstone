import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.question_strategist import question_strategist_node
from agents.difficulty_planner import difficulty_planner_node
from agents.question_generator import question_generator_node
from agents.validator import validator_node
from agents.state import AgentState
from models.data_models import (
    ResumeClaim, RiskAnalysis, ReadinessAnalysis, 
    VulnerabilityMap, SkillGapAnalysis
)

def run_test():
    print("=== Testing Planner & Generator Pipeline ===")
    
    claims = [
        ResumeClaim(text="Built API using FastAPI", section="Projects", risk_score=0.1, risk_label="low", vulnerabilities=[]),
        ResumeClaim(text="Architected microservices on AWS", section="Experience", risk_score=0.5, risk_label="medium", vulnerabilities=["Buzzword Stacking"]),
        ResumeClaim(text="Optimized SQL queries reducing latency by 50%", section="Experience", risk_score=0.2, risk_label="low", vulnerabilities=[]),
        ResumeClaim(text="Implemented e-commerce platform using React", section="Projects", risk_score=0.15, risk_label="low", vulnerabilities=[]),
    ]
    
    state = AgentState(
        resume_text="Mock Resume",
        job_description="",
        claims=claims,
        risk_analysis=RiskAnalysis(claim_risks=[], summary="Medium risk."),
        readiness_analysis=ReadinessAnalysis(score=75.0, level="good", breakdown={}),
        vulnerability_map=VulnerabilityMap(
            strong_claims=5, total_claims=10, strength_ratio=50.0,
            top_weaknesses=["Buzzword Stacking"], interview_focus=["Probe specific contributions"]
        ),
        skill_gap_analysis=SkillGapAnalysis(
            explicit_skills=["FastAPI", "AWS", "Python"],
            implied_skills=["REST", "Docker", "Database"],
            missing_skills=["REST", "Database Design"]
        ),
        messages=[],
        errors=[]
    )
    
    # 1. Strategist
    print("\n[1] Running Strategist Node...")
    strat_out = question_strategist_node(state)
    state.update(strat_out)
    print(f"Strategy: {state['interview_strategy'][:100]}...")
    
    # 2. Planner
    print("\n[2] Running Difficulty Planner Node...")
    plan_out = difficulty_planner_node(state)
    state.update(plan_out)
    print("Question Plan:")
    for item in state['question_plan']:
        print(f"  - {item}")
        
    # 3. Generator
    # 3. Generator & 4. Validator Loop
    MAX_RETRIES = 2
    for attempt in range(MAX_RETRIES + 1):
        print(f"\n[3] Running Question Generator Node (Attempt {attempt+1})...")
        gen_out = question_generator_node(state)
        state.update(gen_out)
        
        print("\n[4] Running Validator Node...")
        val_out = validator_node(state)
        state.update(val_out)
        
        # Check validation status
        results = state.get("validation_results", [])
        failed_count = sum(1 for v in results if v.get("status") == "FAIL")
        
        if failed_count == 0:
            print("\n>>> All questions PASSED validation!")
            break
        else:
            print(f"\n>>> {failed_count} questions FAILED validation. Retrying...")
            if attempt == MAX_RETRIES:
                print(">>> Max retries reached. Proceeding with best effort.")

    print("\n=== FINAL GENERATED QUESTIONS ===")
    for i, q in enumerate(state['generated_questions']):
        status = "UNKNOWN"
        if i < len(state.get("validation_results", [])):
             status = state["validation_results"][i].get("status", "UNKNOWN")
        
        print(f"[{q.difficulty}] {q.question}")
        print(f"   Target: {q.target_claim}")
        print(f"   Validation: {status}")
        if status == "FAIL":
             fb = state["validation_results"][i].get("feedback", "")
             print(f"   Feedback: {fb}")
        print("-" * 50)

if __name__ == "__main__":
    run_test()
