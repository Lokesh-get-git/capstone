from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from utils.llm import get_llm
from agents.state import AgentState
from models.data_models import GeneratedQuestion
from utils.logger import get_logger

logger = get_logger(__name__)

VALIDATOR_PROMPT = """

INPUT:
Questions to Validate:
{questions}

You are a Technical Interview Quality Reviewer.

You are NOT checking if each question is a full interview.

Instead classify the PURPOSE of each question.

Each question should serve ONE role:

OWNERSHIP – what the candidate personally did
IMPLEMENTATION – how they built it
DEBUGGING – bugs or failures
DECISIONS – why they chose an approach
IMPACT – how success was measured

PASS if:
- related to the claim
- conversational and realistic

FAIL only if:
- generic trivia (e.g., "What is REST?")
- unrelated to claim
- academic or theoretical

A question does NOT need multiple roles.


OUTPUT FORMAT (JSON):
STRICT REQUIREMENT: YOUR RESPONSE MUST BE A VALID JSON OBJECT ONLY. 
DO NOT INCLUDE ANY CONVERSATIONAL TEXT, PREAMBLE, OR POSTAMBLE.
DO NOT WRAP IN MARKDOWN CODE BLOCKS.

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
        
        if not response:
            raise ValueError("LLM returned empty response")
            
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
