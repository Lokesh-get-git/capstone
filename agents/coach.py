from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from utils.llm import get_llm
from agents.state import AgentState
from models.data_models import CoachingInsight
from utils.logger import get_logger

logger = get_logger(__name__)

# --- Structured Output Model ---
class InsightItem(BaseModel):
    category: str = Field(description="Strength, Weakness, Practice Tip, or Study Area")
    topic: str = Field(description="Specific context")
    advice: str = Field(description="Actionable coaching advice")
    priority: str = Field(description="High, Medium, or Low")
    resource_query: Optional[str] = Field(default=None, description="Specific preparation search query (optional, mostly for Study Areas or Weaknesses)")

class CoachResponse(BaseModel):
    insights: List[InsightItem] = Field(description="List of coaching insights")

COACH_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a Technical Interview Preparation Coach.

The candidate will NOT answer questions now.
Your job is to prepare them for what interviewers are likely to challenge based on their resume.

TASK:
Identify specific preparation insights for the candidate.
Categorize them as:
1. Strength: What they should highlight.
2. Weakness: What they must defend or explain better.
3. Practice Tip: Actionable logic/behavioral interviewing tips.
4. Study Area: Specific topics to research.

Ensure advice differs based on role (e.g., Senior needs architecture advice, Junior needs concepts).

GOAL:
Predict what an interviewer will ask and help the candidate prepare.

You MUST respond with valid JSON matching this exact schema:
{{
  "insights": [
    {{
      "category": "Strength | Weakness | Practice Tip | Study Area",
      "topic": "string - Specific context",
      "advice": "string - Actionable coaching advice",
      "priority": "High | Medium | Low",
      "resource_query": "string or null - Search query for preparation resources"
    }}
  ]
}}"""),
    ("human", """INPUT:
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
6. AI Risk Factors (Explainability):
{model_insights}""")
])


def coach_node(state: AgentState) -> dict:
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
    llm = get_llm(temperature=0.5)
    chain = COACH_PROMPT | llm.with_structured_output(CoachResponse, method="json_mode")

    inputs = {
            "target_role": role_context,
            "declared_weaknesses": declared_weaknesses,
            "missing_skills": ", ".join(missing),
            "risk_summary": risk_summary,
            "vulnerabilities": ", ".join(vuln_list),
            "claim_context": claim_context,
            # Pass Model Insights for Explainability
            "model_insights": "\n".join([f"- {feature}: {weight:.2f}" for feature, weight in risk.model_insights]) if risk and risk.model_insights else "No ML insights available."
    }

    try:
        response: CoachResponse = chain.invoke(inputs)

        # COST TRACKING
        cost = 0.0
        try:
            from services.cost_tracker import CostTracker
            input_len = len(COACH_PROMPT.format(**inputs))
            output_len = len(str(response.model_dump()))
            cost = CostTracker.track_cost("Coach", input_len//4, output_len//4)
        except:
            pass

        raw_insights = response.insights
        coaching_insights = []

        # Initialize LangChain Tavily Tool
        try:
            from langchain_community.tools.tavily_search import TavilySearchResults
            search_tool = TavilySearchResults(max_results=2)
            logger.info("TavilySearchResults tool initialized.")
        except Exception as e:
            logger.warning(f"Tavily tool init failed: {e}. Using mock links.")
            search_tool = None

        for item in raw_insights:
            category = item.category
            topic = item.topic
            query = item.resource_query or ""
            priority = item.priority
            found_resources = []

            # Search if query exists and category warrants it
            if search_tool and query and category in ["Weakness", "Study Area"]:
                try:
                    results = search_tool.invoke({"query": query})
                    for res in results:
                        if isinstance(res, dict):
                            url = res.get("url", "")
                            content = res.get("content", "")[:50]
                            if url:
                                found_resources.append(f"[{content}...]({url})")
                        elif isinstance(res, str):
                             found_resources.append(res)
                except Exception as s_err:
                     logger.warning(f"Search failed for '{query}': {s_err}")

            # Fallback for Study Areas/Weaknesses if no results
            if not found_resources and category in ["Weakness", "Study Area"] and query:
                 found_resources = [f"[Google Search: {query}](https://www.google.com/search?q={query.replace(' ', '+')})"]

            coaching_insights.append(CoachingInsight(
                category=category,
                topic=topic,
                advice=item.advice,
                priority=priority,
                resources=found_resources
            ))

        logger.info(f"Generated {len(coaching_insights)} coaching insights.")

        return {
            "coaching_insights": coaching_insights,
            "messages": [SystemMessage(content=f"Coach: {len(coaching_insights)} insights generated")],
            "total_cost": cost
        }

    except Exception as e:
        logger.error(f"Coach failed: {e}", exc_info=True)
        return {
            "coaching_insights": [],
            "errors": [str(e)]
        }
