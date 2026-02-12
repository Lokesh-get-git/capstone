import os
import sys
from pprint import pprint

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.question_strategist import question_strategist_node
from agents.state import AgentState
from models.data_models import (
    ResumeClaim, RiskAnalysis, ReadinessAnalysis, 
    VulnerabilityMap, SkillGapAnalysis
)

def run_test():
    print("=== Testing Question Strategist Agent ===")
    
    # Mock Analysis Data (Output of Analyst)
    # Scenario: Strong candidate but with "Buzzword Stacking" and missing REST skills
    
    claims = [
        ResumeClaim(text="Built API using FastAPI", section="Projects", risk_score=0.1, risk_label="low", vulnerabilities=[]),
        ResumeClaim(text="Architected microservices on AWS", section="Experience", risk_score=0.5, risk_label="medium", vulnerabilities=["Buzzword Stacking"]),
        ResumeClaim(text="Optimized SQL queries reducing latency by 50%", section="Experience", risk_score=0.2, risk_label="low", vulnerabilities=[]),
        ResumeClaim(text="Implemented e-commerce platform using React", section="Projects", risk_score=0.15, risk_label="low", vulnerabilities=[]),
    ]
    
    state = AgentState(
        resume_text="Mock Resume Text",
        job_description="",
        claims=claims,
        risk_analysis=RiskAnalysis(claim_risks=[], summary="Medium risk profile."),
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
    
    print("\n[Input State]")
    print(f"Readiness: {state['readiness_analysis'].score}")
    print(f"Gaps: {state['skill_gap_analysis'].missing_skills}")
    
    print("\nRunning Strategist Node (Calls Groq)...")
    try:
        result = question_strategist_node(state)
        
        print("\n=== STRATEGIST OUTPUT ===")
        print(f"Strategy: {result.get('interview_strategy')}")
        print("Focus Areas:")
        for area in result.get('focus_areas', []):
            print(f"  - {area}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_test()
