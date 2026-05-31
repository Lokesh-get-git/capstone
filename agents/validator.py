from typing import List
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from utils.llm import get_llm
from agents.state import AgentState
from models.data_models import GeneratedQuestion
from utils.logger import get_logger

logger = get_logger(__name__)

# --- Structured Output Model ---
class ValidationResult(BaseModel):
    index: int = Field(description="Question index being validated")
    status: str = Field(description="PASS or FAIL")
    feedback: str = Field(description="Feedback on the question quality")

class ValidatorResponse(BaseModel):
    validation_results: List[ValidationResult] = Field(description="List of validation results")

VALIDATOR_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Technical Interview Quality Reviewer.

FRAMEWORK:
Classify the purpose of each question (OWNERSHIP, IMPLEMENTATION, DEBUGGING, DECISIONS, IMPACT).

DECISION RULES:
- PASS if: Related to claim AND properly phrased (conversational, clear).
- FAIL if: Generic trivia, unrelated to claim, academic, or too long.

OUTPUT INSTRUCTIONS:
1. Provide validation results ONLY for the question indices listed in the input.
2. Do NOT generate results for questions that are not in the input.
3. The "status" field MUST be exactly "PASS" or "FAIL". Do not use role names like "IMPACT" as status.

You MUST respond with valid JSON matching this exact schema:
{{
  "validation_results": [
    {{
      "index": 0,
      "status": "PASS or FAIL",
      "feedback": "string - Feedback on question quality"
    }}
  ]
}}"""),
    ("human", """INPUT:
Candidate Profile: {candidate_profile}
Questions to Validate (Indices are important!):
{questions}""")
])

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

    # --- OPTIMIZATION: Only validate new or previously failed questions ---
    previous_results = state.get("validation_results", [])
    passed_indices = {v["index"] for v in previous_results if v.get("status") == "PASS"}

    # Identify questions that need validation (not passed yet)
    questions_to_validate = []
    skipped_indices = set()

    q_str = ""
    for i, q in enumerate(questions):

        if i in passed_indices:
            skipped_indices.add(i)
            continue

        questions_to_validate.append((i, q))
        q_str += f"Q{i}: [{q.difficulty}] {q.question} (Target: {q.target_claim})\n"

    # If everything already passed, we are done
    if not questions_to_validate:
        logger.info("All questions already passed validation. Skipping LLM.")
        return {
            "validation_results": previous_results,
            "messages": ["All questions valid (cached)."]
        }

    logger.info(f"Validating {len(questions_to_validate)} waiting questions (Skipped {len(skipped_indices)} passed)...")

    llm = get_llm(temperature=0.1)
    chain = VALIDATOR_PROMPT | llm.with_structured_output(ValidatorResponse, method="json_mode")

    inputs = {
        "questions": q_str,
        "candidate_profile": f"Target Role: {state.get('candidate_profile').target_role}, Weaknesses: {', '.join(state.get('candidate_profile').self_declared_weaknesses)}" if state.get("candidate_profile") else "Unknown"
    }

    try:
        response: ValidatorResponse = chain.invoke(inputs)

        # COST TRACKING
        cost = 0.0
        try:
            from services.cost_tracker import CostTracker
            input_len = len(VALIDATOR_PROMPT.format(**inputs))
            output_len = len(str(response.model_dump()))
            cost = CostTracker.track_cost("Validator", input_len//4, output_len//4)
        except:
            pass

        new_results = [r.model_dump() for r in response.validation_results]

        # Merge Results
        # Start with cached passed results
        final_results = [v for v in previous_results if v["index"] in passed_indices]


        if len(new_results) != len(questions_to_validate):
            logger.warning(f"Validator LLM returned {len(new_results)} results, expected {len(questions_to_validate)}. Mapping as many as possible.")

        for i, res in enumerate(new_results):
            if i < len(questions_to_validate):
                real_index, _ = questions_to_validate[i]
                res["index"] = real_index # Force correct index
                final_results.append(res)
            else:
                logger.warning(f"Extra validation result ignored: {res}")

        # Sort by index for consistency
        final_results.sort(key=lambda x: x["index"])

        # Calculate pass rate
        pass_count = sum(1 for v in final_results if v.get("status") == "PASS")
        logger.info(f"Validator: {pass_count}/{len(questions)} questions passed.")

        # Return validation results (to be used by graph for routing)
        return {
            "validation_results": final_results,
            "messages": [SystemMessage(content=f"Validation: {pass_count}/{len(questions)} passed")],
            "total_cost": cost
        }

    except Exception as e:
        logger.error(f"Validator failed: {e}", exc_info=True)
        return {
            "validation_results": [],
            "errors": [str(e)]
        }
