from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from utils.llm import get_llm
from agents.state import AgentState
from models.data_models import GeneratedQuestion
from utils.logger import get_logger

logger = get_logger(__name__)

VALIDATOR_PROMPT = """
You are an expert Technical Interview Validator (Quality Control).
Your goal is to ensure every interview question is a rigorous verification of a resume claim.

INPUT:
Questions to Validate:
{questions}

STRICT VALIDATION RULES:
1. NO GENERIC TRIVIA: Questions like "What is X?" or "Explain Y" are BANNED.
   - Requirement: Must probe "How did you use X to solve Problem Z?"
2. TITLE/OWNERSHIP PROBE: Must ask "What was YOUR specific role?" or "How did YOU implement..."
3. TECHNICAL DEPTH: Must probe "Why did you choose A over B?" or "Walk through the implementation."
4. CLAIM ALIGNMENT: The question must directly target the specific claim context provided.

TASK:
For each question, determine if it PASSES or FAILS.
- PASS: Meets all rules.
- FAIL: Violates one or more rules. Provide specific, constructive feedback for the Generator to fix it.

OUTPUT FORMAT (JSON):
{{
    "validation_results": [
        {{
            "index": 0,
            "status": "PASS",
            "feedback": "Good ownership probe."
        }},
        {{
            "index": 1,
            "status": "FAIL",
            "feedback": "Too generic. Rewrite to ask about the specific API endpoint mentioned in the claim."
        }},
        ...
    ]
}}
"""

def validator_node(state: AgentState) -> dict:
    """
    Validator Agent:
    Reviews questions and returns Pass/Fail status with feedback.
    Does NOT rewrite questions.
    """
    logger.info("Validator Agent: validating questions...")
    
    questions = state.get("generated_questions", [])
    if not questions:
        return {"validation_results": [], "messages": ["No questions to validate."]}
        
    # Format questions for LLM
    q_str = ""
    for i, q in enumerate(questions):
        q_str += f"Q{i}: [{q.difficulty}] {q.question} (Target: {q.target_claim})\n"
    
    prompt = ChatPromptTemplate.from_template(VALIDATOR_PROMPT)
    llm = get_llm(temperature=0.1) # Strict validation
    chain = prompt | llm | JsonOutputParser()
    
    inputs = {"questions": q_str}
    
    try:
        response = chain.invoke(inputs)
        
        # COST TRACKING
        cost = 0.0
        try:
            from services.cost_tracker import CostTracker
            input_len = len(prompt.format(**inputs))
            output_len = len(str(response))
            cost = CostTracker.track_cost("Validator", input_len//4, output_len//4)
        except:
            pass
        
        validation_results = response.get("validation_results", [])
        
        # Calculate pass rate
        pass_count = sum(1 for v in validation_results if v.get("status") == "PASS")
        logger.info(f"Validator: {pass_count}/{len(questions)} questions passed.")
        
        # Return validation results (to be used by graph for routing)
        # We can store them in state or just return them for the test script
        return {
            "validation_results": validation_results, 
            "messages": [SystemMessage(content=f"Validation: {pass_count}/{len(questions)} passed")],
            "total_cost": cost
        }
        
    except Exception as e:
        logger.error(f"Validator failed: {e}", exc_info=True)
        return {
            "validation_results": [],
            "errors": [str(e)]
        }
