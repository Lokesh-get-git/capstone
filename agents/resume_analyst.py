from langchain_core.messages import SystemMessage
from parsers.resume_parser import parse_resume_sections, extract_claims_from_sections
from ml.risk_classifier import RiskClassifier
from ml.readiness_scorer import ReadinessScorer
from ml.vulnerability_mapper import map_resume_vulnerabilities
from nlp.cross_reference import cross_reference_claims
from agents.state import AgentState
from models.data_models import (
    ResumeClaim, RiskAnalysis, ReadinessAnalysis, 
    VulnerabilityMap, SkillGapAnalysis
)
from ml.feature_builder import build_feature_vector

# Load ML models once (global cache)
_RISK_MODEL = None
_READINESS_MODEL = None

def get_risk_model():
    global _RISK_MODEL
    if _RISK_MODEL is None:
        _RISK_MODEL = RiskClassifier.load("models/risk_model.joblib")
    return _RISK_MODEL

def get_readiness_model():
    global _READINESS_MODEL
    if _READINESS_MODEL is None:
        _READINESS_MODEL = ReadinessScorer.load("models/readiness_model_v2.joblib")
    return _READINESS_MODEL

def resume_analyst_node(state: AgentState) -> dict:
    """
    Orchestrates the resume analysis pipeline:
    1. Parse raw text -> Sections
    2. Extract Claims
    3. Run Risk Classifier (per claim)
    4. Run Semantic Gap Analysis (Skill Consistency)
    5. Run Readiness Scorer (overall + vulnerability map)
    6. Populate state
    """
    
    text = state["resume_text"]
    
    # 1. Parse
    sections = parse_resume_sections(text)
    
    # 2. Extract
    raw_claims = extract_claims_from_sections(sections)
    
    # 3. Analyze Claims (Risk)
    clf = get_risk_model()
    analyzed_claims = []
    
    risk_data = [] # for legacy summary
    risk_predictions = []

    for c in raw_claims:
        # Get risk prediction
        feat = build_feature_vector(c)
        pred = clf.predict(feat)
        
        # Create ResumeClaim object
        claim_obj = ResumeClaim(
            text=c["text"],
            section=c.get("section", "unknown"),
            risk_label=pred["risk_label"],
            risk_score=pred["risk_score"],
            vulnerabilities=[], # filled next
            interview_questions=[]
        )
        analyzed_claims.append(claim_obj)
        risk_data.append(pred)
        pred = clf.predict(feat)
        risk_predictions.append(pred)


    # 4. Semantic Gap Analysis (Commit 16)
    gap_data = cross_reference_claims(raw_claims)
    skill_gap_analysis = SkillGapAnalysis(
        explicit_skills=gap_data["explicit_skills"],
        implied_skills=gap_data["implied_skills"],
        missing_skills=gap_data["potential_gaps"]
    )

    # 5. Vulnerability Map & Readiness
    vuln_report = map_resume_vulnerabilities(raw_claims, risk_predictions)

    
    # Map back vulnerabilities to our ResumeClaim objects
    for i, analysis in enumerate(vuln_report["per_claim"]):
        vulns = [v["label"] for v in analysis["vulnerabilities"]]
        analyzed_claims[i].vulnerabilities = vulns

    # 6. TF-IDF Relevance Scoring (NEW)
    from nlp.tfidf_manager import TfidfManager
    relevance_score = 0.0
    missing_keywords = []
    
    job_description = state.get("job_description", "")
    

    if job_description:
        tfidf = TfidfManager()
        relevance_score = tfidf.calculate_similarity(text, job_description)
        missing_keywords = tfidf.get_missing_keywords(text, job_description)

    # Score Readiness (with relevance)
    scorer = get_readiness_model()
    readiness = scorer.predict_with_risk(raw_claims, clf, relevance_score=relevance_score)
    
    # Get Model Insights (Explainability)
    model_insights = clf.get_feature_importance(5)

    # Construct output models
    risk_analysis = RiskAnalysis(
        claim_risks=risk_data,
        model_insights=model_insights,
        summary=f"Analyzed {len(analyzed_claims)} claims. Average risk score: {readiness['breakdown'].get('avg_risk', 0):.2f}"
    )
    
    vuln_map = VulnerabilityMap(
        strong_claims=vuln_report["summary"]["strong_claims"],
        total_claims=vuln_report["summary"]["total_claims"],
        strength_ratio=vuln_report["summary"]["strength_ratio"],
        top_weaknesses=[f"{v['label']} ({v['count']})" for v in vuln_report["top_vulnerabilities"]],
        interview_focus=[f"{a['area']}: {a['probe']}" for a in vuln_report["interview_focus_areas"]]
    )
    
    readiness_analysis = ReadinessAnalysis(
        score=readiness["readiness_score"],
        level=readiness["readiness_level"],
        relevance_score=relevance_score,
        missing_keywords=missing_keywords,
        breakdown=readiness["breakdown"]
    )

    return {
        "claims": analyzed_claims,
        "risk_analysis": risk_analysis,
        "readiness_analysis": readiness_analysis,
        "vulnerability_map": vuln_map,
        "skill_gap_analysis": skill_gap_analysis,
        "messages": [SystemMessage(content="Resume analysis complete.")]
    }
