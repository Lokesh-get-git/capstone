
import sys
import os
from pathlib import Path

# Add root to path
sys.path.append(str(Path(__file__).parent))

from agents.orchestrator import run_interview_pipeline
from models.data_models import CandidateProfile

from parsers.resume_parser import extract_text

RESUME_FILE = "sample_resume.txt"

def run_pipeline_test():
    print(f"Running Full Pipeline on {RESUME_FILE}...")
    
    if not os.path.exists(RESUME_FILE):
        print(f"File {RESUME_FILE} not found.")
        return

    # Extract text
    try:
        text = extract_text(RESUME_FILE)
        print(f"Extracted {len(text)} chars.")
    except Exception as e:
        print(f"Extraction Failed: {e}")
        return
    
    # Run Pipeline
    print("Invoking LangGraph Orchestrator...")
    try:
        profile = CandidateProfile(
            target_role="Senior Python Developer",
            experience_years=5,
            self_declared_weaknesses=["System Design"]
        )
        
        result = run_interview_pipeline(
            resume_text=text,
            job_description="Senior Python Developer",
            candidate_profile=profile
        )
    except Exception as e:
        print(f"Pipeline Failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "="*50)
    print("PIPELINE RESULT SUMMARY")
    print("="*50)
    
    # Check if data exists
    if "claims" in result:
        print(f"Claims Analyzed: {len(result['claims'])}")
    else:
        print("❌ No claims found in result.")
        
    if "questions" in result:
        print(f"Questions Generated: {len(result['questions'])}")
        for q in result['questions']:
            print(f"  - [{q.get('difficulty')}] {q.get('question', '')[:60]}...")
    else:
         print("❌ No questions found.")
         
    if "coaching_insights" in result:
        print(f"Coaching Insights: {len(result['coaching_insights'])}")
    else:
        print("❌ No coaching insights found.")
        
    # Check Cost Log
    print("\n" + "="*50)
    print("COST LOG VERIFICATION")
    print("="*50)
    if os.path.exists("cost_log.txt"):
        with open("cost_log.txt", "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print("❌ cost_log.txt NOT FOUND")

if __name__ == "__main__":
    run_pipeline_test()
