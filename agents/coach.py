from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from utils.llm import get_llm
from agents.state import AgentState
from models.data_models import CoachingInsight
from utils.logger import get_logger

logger = get_logger(__name__)
COACH_PROMPT = """
You are a Technical Interview Preparation Coach.

The candidate will NOT answer questions now.
Your job is to prepare them for what interviewers are likely to challenge based on their resume.

INPUT:
1. Candidate Profile:
   Role: {target_role}
   Weaknesses: {declared_weaknesses}
2. Missing Skills (Gap Analysis):
{missing_skills}
3. Risk Analysis Summary:
{risk_summary}
4. Vulnerabilities:
{vulnerabilities}
5. Claims interviewers may question:
{claim_context}

TASK:
Identify the top 3 most critical areas for improvement.
Ensure advice differs based on role (e.g., Senior needs architecture advice, Junior needs syntax/concepts).

GOAL:
Predict what an interviewer will ask follow-up questions about and help the candidate prepare explanations.

IMPORTANT:
Do NOT recommend generic studying (e.g., "learn REST APIs").
Assume the candidate already has experience.

Instead:
- identify what parts of their resume look unclear or questionable
- explain why an interviewer would probe that area
- tell the candidate what they should be ready to explain

For each preparation insight provide:
1. Topic the interviewer will likely probe
2. Why the interviewer will question it
3. How the candidate should prepare their explanation
4. A helpful resource search query

OUTPUT FORMAT (JSON):
{{
    "insights": [
        {{
            "topic": "What interviewer will focus on",
            "advice": "How candidate should prepare and what they must be ready to explain",
            "resource_query": "Specific preparation search query"
        }}
    ]
}}
"""


def coach_node(state: AgentState) -> dict:
    # ... (code up to line 97) ...
    # ... (code up to line 102) ...
    
    # Re-fetch variables to be sure
    risk = state.get("risk_analysis")
    risk_summary = risk.summary if risk else "No risk analysis"
    
    vuln = state.get("vulnerability_map")
    vuln_list = vuln.top_weaknesses if vuln else []
    
    claims = state.get("claims", [])
    risky_claims = sorted(claims, key=lambda c: c.risk_score, reverse=True)[:3]
    claim_context = "\n".join([f"- {c.text[:120]}" for c in risky_claims])
    if not claim_context:
        claim_context = "No high-risk claims found."

    skill_gaps = state.get("skill_gap_analysis")
    missing = skill_gaps.missing_skills if skill_gaps else []
    
    # Profile Logic
    profile = state.get("candidate_profile")
    if profile:
        target_role = profile.target_role
        years = profile.experience_years
        role_context = f"{target_role} ({years} years exp)"
        declared_weaknesses = ", ".join(profile.self_declared_weaknesses)
    else:
        role_context = "Software Engineer"
        declared_weaknesses = "None"
    # Define Chain
    prompt = ChatPromptTemplate.from_template(COACH_PROMPT)
    llm = get_llm(temperature=0.5) 
    chain = prompt | llm | JsonOutputParser()
    
    try:
        response = chain.invoke({
            "target_role": role_context,
            "declared_weaknesses": declared_weaknesses,
            "missing_skills": ", ".join(missing),
            "risk_summary": risk_summary,
            "vulnerabilities": ", ".join(vuln_list),
            "claim_context": claim_context
        })
        
        raw_insights = response.get("insights", [])
        coaching_insights = []
        
        # Initialize LangChain Tavily Tool
        try:
            from langchain_community.tools.tavily_search import TavilySearchResults
            # API Key is picked up from TAVILY_API_KEY env var automatically or we can pass it
            search_tool = TavilySearchResults(max_results=2)
            logger.info("TavilySearchResults tool initialized.")
        except Exception as e:
            logger.warning(f"Tavily tool init failed: {e}. Using mock links.")
            search_tool = None

        for item in raw_insights:
            topic = item.get("topic", "General")
            query = item.get("resource_query", "")
            found_resources = []
            
            if search_tool and query:
                try:
                    # Invoke the tool
                    # tool.invoke returns a list of dicts: [{'url': '...', 'content': '...'}]
                    results = search_tool.invoke({"query": query})
                    for res in results:
                        # Handle potential different return formats (some versions return string)
                        if isinstance(res, dict):
                            url = res.get("url", "")
                            content = res.get("content", "")[:50] # Snippet
                            if url:
                                found_resources.append(f"[{content}...]({url})")
                        elif isinstance(res, str):
                             found_resources.append(res)
                except Exception as s_err:
                     logger.warning(f"Search failed for '{query}': {s_err}")
            
            # Fallback if no results
            if not found_resources:
                 found_resources = [f"[Google Search: {query}](https://www.google.com/search?q={query.replace(' ', '+')})"]

            coaching_insights.append(CoachingInsight(
                topic=topic,
                advice=item.get("advice", "Review this topic."),
                resources=found_resources
            ))
            
        logger.info(f"Generated {len(coaching_insights)} coaching insights.")
        
        return {
            "coaching_insights": coaching_insights,
            "messages": [SystemMessage(content=f"Coach: {len(coaching_insights)} insights generated")]
        }
        
    except Exception as e:
        logger.error(f"Coach failed: {e}", exc_info=True)
        return {
            "coaching_insights": [],
            "errors": [str(e)]
        }
