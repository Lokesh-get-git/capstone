from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from utils.llm import get_llm
from agents.state import AgentState
from models.data_models import GeneratedQuestion
from utils.logger import get_logger

logger = get_logger(__name__)

GENERATOR_PROMPT = """
You are an expert Technical Interview Question Generator.
Your goal is to generate specific, high-quality interview questions based on the provided Plan.

INPUT:
Question Plan:
{plan}

TASK:
For EACH item in the plan, generate a concrete, actionable interview question.
Ensure the question aligns with the difficulty level implied by the plan (Warmup vs Core vs Challenge).
Rules:
- Each question must be ONE clear thought.
- Do not combine multiple questions.
- Prefer short conversational wording.
- Ask follow-up style questions like a real interviewer.
- Avoid long descriptive sentences.
- Maximum 20 words per question.

OUTPUT FORMAT (JSON):
{{
    "questions": [
        {{
            "question": "The actual question string...",
            "difficulty": "Easy/Medium/Hard",
            "target_claim": "The topic or claim being tested",
            "reasoning": "Why this question matters...",
            "expected_answer_points": ["Point 1", "Point 2"]
        }},
        ...
    ]
}}
"""

REFINE_PROMPT = """
You are an expert Technical Interview Question Generator.
Some of your previous questions failed validation. You must REWRITE them based on the feedback.

INPUT:
Failed Questions & Feedback:
{feedback_context}

TASK:
Rewrite ONLY the failed questions. Keep the original difficulty and target.
Apply the feedback strictly (e.g., make it more specific, probe ownership).
Rules:
- Each question must be ONE clear thought.
- Do not combine multiple questions.
- Prefer short conversational wording.
- Ask follow-up style questions like a real interviewer.
- Avoid long descriptive sentences.
- Maximum 20 words per question.
OUTPUT FORMAT (JSON):
{{
    "refined_questions": [
        {{
            "index": 0,
            "question": "The REWRITTEN question...",
            "difficulty": "Original difficulty",
            "target_claim": "Original target",
            "reasoning": "Why this question matters...",
            "expected_answer_points": ["Point 1", "Point 2"]

        }},
        ...
    ]
}}
"""

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
    
    failed_indices = [v["index"] for v in validation_results if v.get("status") == "FAIL"]
    
    if failed_indices and current_questions:
        logger.info(f"Refining {len(failed_indices)} failed questions...")
        
        # Prepare context for refinement
        feedback_context = ""
        for v in validation_results:
            if v.get("status") == "FAIL":
                idx = v["index"]
                original_q = current_questions[idx]
                feedback_context += f"Q{idx} (Target: {original_q.target_claim}):\n"
                feedback_context += f"  - Original: {original_q.question}\n"
                feedback_context += f"  - Feedback: {v['feedback']}\n\n"
        
        prompt = ChatPromptTemplate.from_template(REFINE_PROMPT)
        llm = get_llm(temperature=0.7) # Creativity to fix issues
        chain = prompt | llm | JsonOutputParser()
        
        try:
            inputs = {"feedback_context": feedback_context}
            response = chain.invoke(inputs)

            # COST TRACKING (Refinement)
            cost = 0.0
            try:
                from services.cost_tracker import CostTracker
                input_len = len(prompt.format(**inputs))
                output_len = len(str(response))
                cost = CostTracker.track_cost("Generator (Refine)", input_len//4, output_len//4)
            except:
                pass
            refined_list = response.get("refined_questions", [])
            
            # Update the original list
            new_questions = list(current_questions) # copy
            for r in refined_list:
                idx = r.get("index")
                if idx is not None and 0 <= idx < len(new_questions):
                     new_questions[idx] = GeneratedQuestion(
                        question=r.get("question", "Unknown"),
                        difficulty=r.get("difficulty", "Medium"),
                        target_claim=r.get("target_claim", "General"),
                        reasoning=r.get("reasoning", "Refined"),
                        expected_answer_points=r.get("expected_answer_points", [])
                    )
            
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
    
    prompt = ChatPromptTemplate.from_template(GENERATOR_PROMPT)
    llm = get_llm(temperature=0.6)
    chain = prompt | llm | JsonOutputParser()
    
    try:
        inputs = {"plan": plan_str}
        response = chain.invoke(inputs)

        # COST TRACKING (Standard)
        cost = 0.0
        try:
            from services.cost_tracker import CostTracker
            input_len = len(prompt.format(**inputs))
            output_len = len(str(response))
            cost = CostTracker.track_cost("Generator", input_len//4, output_len//4)
        except:
            pass
        
        raw_questions = response.get("questions", [])
        generated_questions = []
        
        for q in raw_questions:
            generated_questions.append(GeneratedQuestion(
                question=q.get("question", "Unknown Question"),
                difficulty=q.get("difficulty", "Medium"),
                target_claim=q.get("target_claim", "General"),
                reasoning=q.get("reasoning", ""),
                expected_answer_points=q.get("expected_answer_points", [])
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
