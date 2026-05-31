from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from utils.llm import get_llm
from agents.state import AgentState
from models.data_models import GeneratedQuestion
from utils.logger import get_logger

logger = get_logger(__name__)

# --- Structured Output Models ---
class QuestionItem(BaseModel):
    question: str = Field(description="The actual question string")
    difficulty: str = Field(description="Easy/Medium/Hard")
    target_claim: str = Field(description="The topic or claim being tested")
    reasoning: str = Field(description="Why this question matters")
    expected_answer_points: List[str] = Field(description="Key points expected in the answer")

class GeneratorResponse(BaseModel):
    questions: List[QuestionItem] = Field(description="List of generated interview questions")

class RefinedQuestionItem(BaseModel):
    index: int = Field(description="Index of the original question being refined")
    question: str = Field(description="The REWRITTEN question")
    difficulty: str = Field(description="Original difficulty")
    target_claim: str = Field(description="Original target")
    reasoning: str = Field(description="Why this question matters")
    expected_answer_points: List[str] = Field(description="Key points expected in the answer")

class RefinedResponse(BaseModel):
    refined_questions: List[RefinedQuestionItem] = Field(description="List of refined questions")

# --- Prompts ---
GENERATOR_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert Technical Interview Question Generator.
The interviewer is a busy software engineer speaking casually.

Avoid phrases:
"can you elaborate"
"walk me through in detail"
"describe comprehensively"

Prefer:
"What did you actually build?"
"What broke first?"
"How did you debug it?"

Rules:
- Each question must be ONE clear thought.
- Do not combine multiple questions.
- Prefer short conversational wording.
- Ask follow-up style questions like a real interviewer.
- Avoid long descriptive sentences.
- Maximum 20 words per question.
- Every question must be grounded in the provided claims.
- Do NOT invent companies, conferences, hackathons, or metrics not mentioned in the claims.

You MUST respond with valid JSON matching this exact schema:
{{
  "questions": [
    {{
      "question": "string - The actual question",
      "difficulty": "string - Easy/Medium/Hard",
      "target_claim": "string - The topic or claim being tested",
      "reasoning": "string - Why this question matters",
      "expected_answer_points": ["string - key point 1", "string - key point 2"]
    }}
  ]
}}"""),
    ("human", """INPUT:
Candidate Profile: {candidate_profile}
Question Plan:
{plan}
Resume Claims:
{claim_context}

TASK:
For EACH item in the plan, generate a concrete, actionable interview question.
Ensure the question aligns with the difficulty level implied by the plan (Warmup vs Core vs Challenge).""")
])

REFINE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert Technical Interview Question Generator.
Some of your previous questions failed validation. You must REWRITE them based on the feedback.

Rules:
- You MUST use the same 'index', 'difficulty', and 'target_claim' as the failed question.
- Do NOT generate questions for indices that are not in the input.
- Follow the original rules: ONE clear thought, conversational, max 20 words.

You MUST respond with valid JSON matching this exact schema:
{{
  "refined_questions": [
    {{
      "index": 0,
      "question": "string - The REWRITTEN question",
      "difficulty": "string - Original difficulty",
      "target_claim": "string - Original target",
      "reasoning": "string - Why this question matters",
      "expected_answer_points": ["string - key point 1", "string - key point 2"]
    }}
  ]
}}"""),
    ("human", """INPUT:
Candidate Profile: {candidate_profile}
Failed Questions & Feedback:
{feedback_context}

TASK:
Rewrite ONLY the failed questions.""")
])

def question_generator_node(state: AgentState) -> dict:
    """
    Generator Agent:
    Takes the abstract Plan and generates concrete Questions.
    Also handles REFINEMENT if validation feedback is present.
    """
    logger.info("Generator Agent: creating/refining questions...")

    # Check for feedback first
    validation_results = state.get("validation_results", [])
    current_questions = state.get("generated_questions", [])

    failed_indices = [v["index"] for v in validation_results if v.get("status") != "PASS"]

    if failed_indices and current_questions:
        logger.info(f"Refining {len(failed_indices)} failed questions...")

        # Prepare context for refinement
        feedback_context = ""
        for v in validation_results:
            if v.get("status") != "PASS":
                idx = v["index"]
                original_q = current_questions[idx]
                feedback_context += f"Q{idx} (Target: {original_q.target_claim}):\n"
                feedback_context += f"  - Original: {original_q.question}\n"
                feedback_context += f"  - Feedback: {v['feedback']}\n\n"

        llm = get_llm(temperature=0.7)
        chain = REFINE_PROMPT | llm.with_structured_output(RefinedResponse, method="json_mode")

        try:
            inputs = {
                "feedback_context": feedback_context,
                "candidate_profile": f"Role: {state.get('candidate_profile').target_role}, Weaknesses: {', '.join(state.get('candidate_profile').self_declared_weaknesses)}" if state.get("candidate_profile") else "Unknown"
            }
            response: RefinedResponse = chain.invoke(inputs)

            # COST TRACKING (Refinement)
            cost = 0.0
            try:
                from services.cost_tracker import CostTracker
                input_len = len(REFINE_PROMPT.format(**inputs))
                output_len = len(str(response.model_dump()))
                cost = CostTracker.track_cost("Generator (Refine)", input_len//4, output_len//4)
            except:
                pass

            refined_list = response.refined_questions

            # Update the original list safely
            new_questions = list(current_questions) # copy

            for r in refined_list:
                idx = r.index

                # Validation: Check if index is valid and was actually failed
                if idx is not None and idx in failed_indices and 0 <= idx < len(new_questions):
                     new_questions[idx] = GeneratedQuestion(
                        question=r.question,
                        difficulty=r.difficulty,
                        target_claim=r.target_claim,
                        reasoning=r.reasoning,
                        expected_answer_points=r.expected_answer_points
                    )
                else:
                    logger.warning(f"Refinement returned invalid index {idx} (Expected one of {failed_indices})")

            # Increment retry count
            current_retries = state.get("retry_count", 0)

            return {
                "generated_questions": new_questions,
                "retry_count": current_retries + 1,
                "messages": [SystemMessage(content=f"Refined {len(refined_list)} questions")],
                "total_cost": cost
            }

        except Exception as e:
             logger.error(f"Refinement failed: {e}", exc_info=True)
             return {"errors": [str(e)]}

    # Standard Generation Mode (No feedback or first run)
    plan = state.get("question_plan", [])
    if not plan:
        logger.warning("No plan found. generating default.")
        plan = ["Warmup: Introduction"]

    plan_str = "\n".join([f"{i+1}. {item}" for i, item in enumerate(plan)])

    llm = get_llm(temperature=0.6)
    chain = GENERATOR_PROMPT | llm.with_structured_output(GeneratorResponse, method="json_mode")

    claims = state.get("claims", [])
    claim_context = "\n".join([f"- {c.text}" for c in claims])
    if not claim_context:
        claim_context = "No claims detected."

    try:
        inputs = {
            "plan": plan_str,
            "claim_context": claim_context,
            "candidate_profile": f"Role: {state.get('candidate_profile').target_role}, Weaknesses: {', '.join(state.get('candidate_profile').self_declared_weaknesses)}" if state.get("candidate_profile") else "Unknown"
        }
        response: GeneratorResponse = chain.invoke(inputs)

        # COST TRACKING (Standard)
        cost = 0.0
        try:
            from services.cost_tracker import CostTracker
            input_len = len(GENERATOR_PROMPT.format(**inputs))
            output_len = len(str(response.model_dump()))
            cost = CostTracker.track_cost("Generator", input_len//4, output_len//4)
        except:
            pass

        generated_questions = []

        for q in response.questions:
            generated_questions.append(GeneratedQuestion(
                question=q.question,
                difficulty=q.difficulty,
                target_claim=q.target_claim,
                reasoning=q.reasoning,
                expected_answer_points=q.expected_answer_points
            ))

        logger.info(f"Generated {len(generated_questions)} questions.")

        return {
            "generated_questions": generated_questions,
            "messages": [SystemMessage(content=f"Generated {len(generated_questions)} questions")],
            "total_cost": cost
        }

    except Exception as e:
        logger.error(f"Generator failed: {e}", exc_info=True)
        return {
            "generated_questions": [],
            "errors": [str(e)]
        }
