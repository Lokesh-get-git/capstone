from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from utils.llm import get_llm
from agents.state import AgentState
from utils.logger import get_logger

logger = get_logger(__name__)

STRATEGIST_PROMPT = """
You are an expert Technical Interview Strategist.
Your goal is to analyze a candidate's resume analysis report and formulate a high-level interview strategy.

INPUT DATA:
1. Readiness Score: {readiness_score}/100 ({readiness_level})
2. Risk Analysis: {risk_summary}
3. Top Vulnerabilities: {top_vulnerabilities}
4. Skill Gaps (Implied but missing): {missing_skills}
5. Key Sections Overview:
{section_summaries}
6. Top Risky Claims:
{claim_summaries}

TASK:
1. Determine the interview tone.
2. Identify 3-5 specific Focus Areas.
   - MANDATORY: You must include at least one focus area related to **Projects** (if available) to verify hands-on experience.
   - MANDATORY: You must include at least one focus area related to **Experience/Work History** to assess depth.
   - Address any high risks or skill gaps.

OUTPUT FORMAT (JSON):
{{
    "interview_strategy": "A concise strategy description...",
    "focus_areas": [
        {{
            "topic": "Project: [Project Name or Tech]",
            "rationale": "Reasoning..."
        }},
        {{
            "topic": "Experience: [Role or Company]",
            "rationale": "Reasoning..."
        }},
        ...
    ]
}}
"""

def question_strategist_node(state: AgentState) -> dict:
    """
    Strategist Agent:
    Decides WHAT to ask based on the Analyst's findings.
    """
    logger.info("Strategist Agent: formulating strategy...")
    
    # Unpack state
    readiness = state["readiness_analysis"]
    risks = state["risk_analysis"]
    vulns = state["vulnerability_map"]
    gaps = state.get("skill_gap_analysis")
    
    # Format inputs
    missing_skills_str = ", ".join(gaps.missing_skills[:10]) if gaps else "None"
    top_vulns_str = ", ".join(vulns.top_weaknesses)
    
    # Group claims by section for overview
    sections = {}
    for c in state["claims"]:
        sec = c.section if c.section else "Other"
        if sec not in sections:
            sections[sec] = []
        sections[sec].append(c)
        
    section_summaries = []
    for sec, claims in sections.items():
        # Summary: "Experience: 5 claims (Avg Risk: 0.12)"
        avg_risk = sum(c.risk_score for c in claims) / len(claims) if claims else 0
        section_summaries.append(f"- {sec}: {len(claims)} claims (Avg Risk: {avg_risk:.2f})")
        # Add top 2 claims from this section to context
        top_sec_claims = sorted(claims, key=lambda x: x.risk_score, reverse=True)[:2]
        for tsc in top_sec_claims:
             section_summaries.append(f"  * {tsc.text[:80]}...")

    # Format top risky claims (global)
    claim_summaries = []
    sorted_claims = sorted(state["claims"], key=lambda c: c.risk_score, reverse=True)
    for c in sorted_claims[:3]: 
        claim_summaries.append(f"- '{c.text[:50]}...' (Risk: {c.risk_score:.2f}, Issues: {', '.join(c.vulnerabilities)})")
    
    prompt = ChatPromptTemplate.from_template(STRATEGIST_PROMPT)
    llm = get_llm(temperature=0.2)
    chain = prompt | llm | JsonOutputParser()
    
    try:
        response = chain.invoke({
            "readiness_score": readiness.score,
            "readiness_level": readiness.level,
            "risk_summary": risks.summary,
            "top_vulnerabilities": top_vulns_str,
            "missing_skills": missing_skills_str,
            "section_summaries": "\n".join(section_summaries),
            "claim_summaries": "\n".join(claim_summaries)
        })
        
        strategy_text = response.get("interview_strategy", "Standard Interview")
        focus_areas_list = [
            f"{f['topic']}: {f['rationale']}" 
            for f in response.get("focus_areas", [])
        ]
        
        logger.info(f"Strategy formulated: {strategy_text}")
        
        return {
            "interview_strategy": strategy_text,
            "focus_areas": focus_areas_list,
            "messages": [SystemMessage(content=f"Strategy Set: {strategy_text}")]
        }
        
    except Exception as e:
        logger.error(f"Strategist failed: {e}", exc_info=True)
        return {
            "interview_strategy": "Fallback Strategy: Verify core skills.",
            "focus_areas": ["Core Skills: Validate resume claims"],
            "errors": [str(e)]
        }
