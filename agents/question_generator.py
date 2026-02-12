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

def question_generator_node(state: AgentState) -> dict:
    """
    Generator Agent:
    Takes the abstract Plan and generates concrete Questions.
    """
    logger.info("Generator Agent: creating questions from plan...")
    
    plan = state.get("question_plan", [])
    if not plan:
        logger.warning("No plan found. generating default.")
        plan = ["Warmup: Introduction"]
        
    plan_str = "\n".join([f"{i+1}. {item}" for i, item in enumerate(plan)])
    
    prompt = ChatPromptTemplate.from_template(GENERATOR_PROMPT)
    llm = get_llm(temperature=0.6) # Technical creativity needed
    chain = prompt | llm | JsonOutputParser()
    
    try:
        response = chain.invoke({
            "plan": plan_str
        })
        
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
            "messages": [SystemMessage(content=f"Generated {len(generated_questions)} questions")]
        }
        
    except Exception as e:
        logger.error(f"Generator failed: {e}", exc_info=True)
        return {
            "generated_questions": [],
            "errors": [str(e)]
        }
