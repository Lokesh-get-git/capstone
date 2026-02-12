from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from utils.llm import get_llm
from agents.state import AgentState
from utils.logger import get_logger

logger = get_logger(__name__)

PLANNER_PROMPT = """
You are an expert Technical Interview Planner.

You are NOT designing a normal software engineering interview.
You are designing a CLAIM-VERIFICATION interview.

The purpose of this interview is to verify whether the candidate actually performed the accomplishments written on their resume.

INPUT:
1. Strategy: {strategy}
2. Focus Areas:
{focus_areas}
3. Candidate Readiness: {readiness_level} ({readiness_score})
4. Key Resume Claims To Verify:
{claim_context}
5. Time Constraints: ~45 minutes


IMPORTANT DEFINITIONS:
A "claim" is a statement about something the candidate says they personally accomplished.

TASK:
The interview should feel like a natural conversation, not a scripted questionnaire.
Questions should evolve based on curiosity and suspicion, not categories.


Each plan item MUST:
• reference a specific claim
• probe ownership ("what did YOU personally do?")
• probe implementation details
• avoid generic theory questions

Do NOT introduce unrelated technologies, frameworks, or hypothetical projects.
TASK:
You are creating a conversation flow, not a questionnaire.

Create EXACTLY 6 conversation beats.

Each beat is a single moment in a natural technical interview conversation.

The flow should:
1. Start casual
2. Clarify what the project was
3. Ask how they implemented it
4. Ask about a problem they faced
5. Challenge a decision they made
6. Ask how they knew it worked

Rules:
- One short sentence per beat (max 12 words)
- Do NOT create sections (no warmup/core/deep dive)
- Do NOT create multiple questions inside a beat
- Do NOT write interview questions
- Do NOT use academic wording


OUTPUT FORMAT (JSON):
STRICT REQUIREMENT: YOUR RESPONSE MUST BE A VALID JSON OBJECT ONLY. 
DO NOT INCLUDE ANY CONVERSATIONAL TEXT, PREAMBLE, OR POSTAMBLE.
DO NOT WRAP IN MARKDOWN CODE BLOCKS.

{{
    "rationale": "Brief explanation of the investigation flow...",
    "plan": [
        "Warmup: ...",
        "Core: ...",
        "Deep Dive: ..."
    ]
}}
"""


def difficulty_planner_node(state: AgentState) -> dict:
    """
    Planner Agent:
    Orders the topics into a logical flow (Warmup -> Core -> Challenge).
    """
    logger.info("Planner Agent: creating question plan...")
    
    strategy = state.get("interview_strategy", "Standard Interview")
    focus_areas = state.get("focus_areas", [])
    readiness = state["readiness_analysis"]
    claims = state.get("claims", [])
    top_claims = [c for c in claims if c.risk_score >= 25]

    if len(top_claims) < 3:
        top_claims = sorted(claims, key=lambda c: c.risk_score, reverse=True)[:3]

    claim_context = "\n".join(
        [f"- {c.text[:140]}... (risk={c.risk_score:.1f}, issues={', '.join(c.vulnerabilities)})"
        for c in top_claims]
    )

    # Format focus areas
    focus_str = "\n".join([f"- {f}" for f in focus_areas])
    
    prompt = ChatPromptTemplate.from_template(PLANNER_PROMPT)
    llm = get_llm(temperature=0.4) # Slightly higher temp for creative flow
    chain = prompt | llm | JsonOutputParser()
    
    inputs = {
            "strategy": strategy,
            "focus_areas": focus_str,
            "readiness_level": readiness.level,
            "readiness_score": readiness.score,
            "claim_context": claim_context
    }
    
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
            cost = CostTracker.track_cost("Planner", input_len//4, output_len//4)
        except:
             pass

        
        plan = response.get("plan", [])
        logger.info(f"Plan created with {len(plan)} steps.")
        
        return {
            "question_plan": plan,
            "messages": [SystemMessage(content=f"Plan Created: {len(plan)} items")],
            "total_cost": cost
        }
        
    except Exception as e:
        logger.error(f"Planner failed: {e}", exc_info=True)
        return {
            "question_plan": ["Warmup: Experience overview", "Core: Tech stack verification"],
            "errors": [str(e)]
        }
