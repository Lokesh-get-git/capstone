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
1. Candidate Profile:
   Role: {target_role} ({experience_level})
   Self-Declared Weaknesses: {weaknesses}
2. Resume Risk Analysis:
   {risk_summary}
3. Vulnerability Map:
   Top Weaknesses: {top_weaknesses}
   Interview Focus: {interview_focus}
4. Job Description (Optional):
   {job_description}
5. Readiness Score: {readiness_score}/100 ({readiness_level})
6. Skill Gaps (Implied but missing): {missing_skills}
7. Key Sections Overview:
{section_summaries}
8. Top Risky Claims:
{claim_summaries}

TASK:
Formulate a high-level interview strategy.
- If the candidate is Senior, focus on system design and architectural decisions.
- If Junior, focus on fundamentals and coding.
- Address their self-declared weaknesses + the resume vulnerabilities.

You are designing a CLAIM VERIFICATION interview.

Your objective is to verify whether the candidate actually performed the resume claims.

Rules:
1. Each focus area must map to a specific resume claim or vulnerability.
2. High-risk claims MUST be directly challenged.
3. If a claim has "No Technical Specifics", you must probe implementation details.
4. If a claim has "No Quantified Impact", you must probe measurement and metrics.
5. Avoid generic topics like "Explain microservices" or "What is React".

Instead, questions should resemble:
- "You mentioned X — how exactly did you implement it?"
- "Walk me through what YOU personally did."
- "What went wrong during this project?"

Output focus areas as verification goals, not topics.



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
    
    vuln = state.get("vulnerability_map", None)
    top_weaknesses = vuln.top_weaknesses if vuln else []
    interview_focus = vuln.interview_focus if vuln else []
    
    profile = state.get("candidate_profile")
    if profile:
        target_role = profile.target_role
        years = profile.experience_years
        # Infer level for proper context
        if years < 3:
            experience_level = f"Junior ({years} years)"
        elif years < 7:
            experience_level = f"Mid-Level ({years} years)"
        else:
            experience_level = f"Senior ({years} years)"
            
        weaknesses = ", ".join(profile.self_declared_weaknesses)
    else:
        target_role = "Software Engineer"
        experience_level = "Mid-Level (3 years)"
        weaknesses = "None declared"

    prompt = ChatPromptTemplate.from_template(STRATEGIST_PROMPT)
    llm = get_llm(temperature=0.7)
    chain = prompt | llm | JsonOutputParser()
    
    try:
        inputs = {
            "target_role": target_role,
            "experience_level": experience_level,
            "weaknesses": weaknesses,
            "risk_summary": risks.summary,
            "top_weaknesses": ", ".join(top_weaknesses),
            "interview_focus": ", ".join(interview_focus),
            "job_description": state.get("job_description", "Generic Software Role"),
            "readiness_score": readiness.score,
            "readiness_level": readiness.level,
            "missing_skills": missing_skills_str,
            "section_summaries": "\n".join(section_summaries),
            "claim_summaries": "\n".join(claim_summaries)
        }
        
        response = chain.invoke(inputs)
        
        # COST TRACKING
        cost = 0.0
        try:
            from services.cost_tracker import CostTracker
            input_len = len(prompt.format(**inputs))
            output_len = len(str(response))
            cost = CostTracker.track_cost("Strategist", input_len//4, output_len//4)
        except:
            pass
        
        strategy_text = response.get("interview_strategy", "Standard Interview")
        focus_areas_list = [
            f"{f['topic']}: {f['rationale']}" 
            for f in response.get("focus_areas", [])
        ]
        
        logger.info(f"Strategy formulated: {strategy_text}")
        
        return {
            "interview_strategy": strategy_text,
            "focus_areas": focus_areas_list,
            "messages": [SystemMessage(content=f"Strategy Set: {strategy_text}")],
            "total_cost": cost
        }
        
    except Exception as e:
        logger.error(f"Strategist failed: {e}", exc_info=True)
        return {
            "interview_strategy": "Fallback Strategy: Verify core skills.",
            "focus_areas": ["Core Skills: Validate resume claims"],
            "errors": [str(e)]
        }
