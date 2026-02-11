from langgraph.graph import StateGraph, END
from agents.state import AgentState
from models.data_models import InterviewQuestion, ResumeClaim
from parsers.resume_parser import parse_resume_sections, extract_claims_from_sections, extract_text

def analyst_node(state: AgentState):
    """
    1. Parse the raw text
    2. Extract claims
    3. Generate simple heuristic questions
    """
    sections = parse_resume_sections(state["raw_text"])
    claims = extract_claims_from_sections(sections)
    
    # Simple Rule-Based Question Generation (Placeholder for LLM)
    generated_questions = []
    
    for claim in claims:
        txt = claim["text"].lower()
        question = None
        
        if "python" in txt:
            question = "How have you optimized Python code for performance in this project?"
        elif "api" in txt or "fastapi" in txt:
            question = "How did you handle authentication and rate limiting for your APIs?"
        elif "deploy" in txt or "docker" in txt:
            question = "Describe your CI/CD pipeline and how you handle rollback strategies."
            
        if question:
            generated_questions.append(InterviewQuestion(
                question=question,
                target_claim=claim["text"][:50] + "...",
                reasoning="Keyword match trigger"
            ))
            
    print(f"--- 3. GENERATED {len(generated_questions)} QUESTIONS ---")
    
    return {
        "sections": sections,
        "claims": [ResumeClaim(text=c["text"], section=c["section"]) for c in claims],
        "questions": generated_questions,
        "metadata": {"status": "analyzed_v1"}
    }

def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("analyst", analyst_node)
    workflow.set_entry_point("analyst")
    workflow.add_edge("analyst", END)
    return workflow.compile()

if __name__ == "__main__":
    # Integration Test
    app = build_graph()
    
    # Simulate an upload
    from pathlib import Path
    sample_path = "sample_resume.txt" # Make sure this exists or use a string
    
    # If sample file exists, run it
    if Path(sample_path).exists():
        text = extract_text(sample_path)
    else:
        text = "Experienced Python Developer who built REST APIs using FastAPI and deployed with Docker."
        
    initial_state = {
        "raw_text": text,
        "sections": {},
        "claims": [],
        "questions": [],
        "messages": [],
        "metadata": {}
    }
    
    result = app.invoke(initial_state)
    
    print("\n=== FINAL OUTPUT ===")
    for q in result["questions"]:
        print(f"Q: {q.question}")
        print(f"   (Source: {q.target_claim})")