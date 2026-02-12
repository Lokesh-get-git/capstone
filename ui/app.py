import streamlit as st
import requests
import pandas as pd
import json

# API Config
API_URL = "http://localhost:8000/api"

st.set_page_config(
    page_title="AntiGravity | AI Interview Coach",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Feel
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    div[data-testid="stExpander"] {
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        background-color: #ffffff;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .risk-high { color: #e74c3c; font-weight: bold; }
    .risk-medium { color: #f39c12; font-weight: bold; }
    .risk-low { color: #27ae60; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.title("🚀 AntiGravity")
    st.markdown("### Candidate Profile")
    target_role = st.text_input("Target Role", "Senior Backend Engineer")
    experience_years = st.number_input("Years of Experience", 0, 50, 5)
    
    with st.expander("Advanced Settings"):
        job_description = st.text_area("Job Description (Optional)", height=100)
        tech_stack_str = st.text_area("Tech Stack", "Python, Docker, AWS, Kubernetes")
        weaknesses_str = st.text_area("Known Weaknesses", "System Design, Public Speaking")
        
    st.markdown("---")
    uploaded_file = st.file_uploader("Upload Resume (PDF/TXT)", type=["pdf", "txt"])
    
    analyze_btn = st.button("🚀 Analyze Resume", type="primary", use_container_width=True)

# --- Main App ---
if "results" not in st.session_state:
    st.session_state.results = None

if analyze_btn and uploaded_file:
    with st.status("Analyzing Resume...", expanded=True) as status:
        # 1. Extract
        st.write("Extracting text from resume...")
        try:
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            response_extract = requests.post(f"{API_URL}/extract_text", files=files)
            response_extract.raise_for_status()
            resume_text = response_extract.json().get("text", "")
        except Exception as e:
            status.update(label="Extraction Failed", state="error")
            st.error(f"Extraction Error: {e}")
            st.stop()
            
        # 2. Analyze
        st.write("Running Multi-Agent Simulation (Analyst -> Strategist -> Planner -> Coach)...")
        try:
            payload = {
                "resume_text": resume_text,
                "job_description": job_description,
                "candidate_profile": {
                    "target_role": target_role,
                    "experience_years": experience_years,
                    "tech_stack": [t.strip() for t in tech_stack_str.split(",") if t.strip()],
                    "self_declared_weaknesses": [w.strip() for w in weaknesses_str.split(",") if w.strip()]
                }
            }
            res = requests.post(f"{API_URL}/analyze", json=payload)
            res.raise_for_status()
            st.session_state.results = res.json()
            status.update(label="Analysis Complete!", state="complete", expanded=False)
        except Exception as e:
            status.update(label="Analysis Failed", state="error")
            st.error(f"API Error: {e}")
            st.stop()

# --- Display Results ---
if st.session_state.results:
    results = st.session_state.results
    readiness = results.get("readiness_analysis", {})
    risk = results.get("risk_analysis", {})
    
    # Header Metrics
    st.markdown(f"## Dashboard: {target_role}")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Readiness Score", f"{readiness.get('score', 0)}/100", delta=readiness.get("level"),
                 help="Derived from the 'Resume Analyst' agent. based on claim verifiability, quantifiable metrics, and consistency.")
    with col2:
        st.metric("Claims Analyzed", len(results.get("claims", [])),
                 help="Total number of distinct professional claims extracted from your resume sections.")
    with col3:
        # Skill Gaps
        skill_gaps = results.get("skill_gaps", {})
        missing_count = len(skill_gaps.get("missing_skills", []))
        st.metric("Skill Gaps Identified", missing_count, delta=f"-{missing_count}", delta_color="inverse",
                 help="Missing skills identified by the 'Resume Analyst' by comparing your profile against industry standards for your role.")
    with col4:
        st.metric("Vulnerabilities", len(results.get("vulnerability_map", {}).get("top_weaknesses", [])),
                 help="Critical weaknesses identified by 'Vulnerability Mapper' (e.g., vague claims, missing metrics).")

    st.markdown("---")

    # Tabs
    tab_overview, tab_practice, tab_coach = st.tabs(["📊 Resume Analysis", "🎤 Practice Inteview", "💡 AI Coach"])

    # TAB 1: OVERVIEW
    with tab_overview:
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.subheader("🔍 Claim Risk Analysis")
            st.caption("Source: **Resume Analyst Agent**. We analyzed every claim in your resume for credibility (Rule-based & ML).")
            
            claims = results.get("claims", [])
            if claims:
                # Prepare DataFrame for Display
                df_claims = pd.DataFrame(claims)
                
                # Filter Columns
                if "text" in df_claims.columns and "risk_label" in df_claims.columns:
                    # Sort by Risk Score (Descending) if available, else by label
                    if "risk_score" in df_claims.columns:
                         df_claims = df_claims.sort_values(by="risk_score", ascending=False)
                    
                    df_display = df_claims[["text", "risk_label"]].copy()
                    df_display.columns = ["Claim", "Risk Level"]
                    
                    # Define Color Map
                    def color_risk(val):
                        if "high" in val.lower():
                            return 'background-color: #ffcccc; color: #990000' # Red
                        elif "medium" in val.lower():
                            return 'background-color: #ffebcc; color: #995500' # Orange
                        elif "low" in val.lower():
                            return 'background-color: #ccffcc; color: #006600' # Green
                        return ''

                    # Apply Validation
                    st.dataframe(
                        df_display.style.map(color_risk, subset=["Risk Level"]),
                        column_config={
                            "Claim": st.column_config.TextColumn("Claim", width="large"),
                            "Risk Level": st.column_config.TextColumn("Risk Level", width="small")
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.error("Claims data format issue.")
            else:
                st.warning("No claims analyzed.")
                

        with col_right:
            st.subheader("⚠️ Vulnerabilities")
            st.caption("Source: **Vulnerability Mapper**. Common resume pitfalls.")
            vuln = results.get("vulnerability_map", {})
            for w in vuln.get("top_weaknesses", []):
                st.error(f"**{w}**")
            
            st.subheader("🎯 Interviewer Focus")
            st.caption("Source: **Question Strategist Agent**. Predicted topics.")
            for f in vuln.get("interview_focus", []):
                st.markdown(f"- {f}")

    # TAB 2: PRACTICE
    with tab_practice:
        st.subheader("📚 Tailored Interview Questions")
        st.caption("Source: **Question Generator Agent**. Questions are generated based on your resume's risks and validated by the **Validator Agent**.")
        
        questions = results.get("questions", [])
        
        for i, q in enumerate(questions):
            with st.expander(f"Q{i+1}: {q.get('question')}  [{q.get('difficulty')}]"):
                st.markdown(f"**Target Claim:** `{q.get('target_claim')}`")
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Why they're asking (Reasoning):**")
                    st.write(q.get("reasoning"))
                with c2:
                    st.markdown("**What you should cover:**")
                    for pt in q.get("expected_answer_points", []):
                        st.markdown(f"- {pt}")
        
    # TAB 3: COACH
    with tab_coach:
        st.subheader("👨‍🏫 Personalized Coaching")
        st.caption("Source: **Coach Agent** (powered by Tavily Search). Provides actionable advice and learning resources.")
        insights = results.get("coaching_insights", [])
        if not insights:
            st.warning("No coaching insights generated.")
        
        cols = st.columns(3)
        for i, insight in enumerate(insights):
            with cols[i % 3]:
                with st.container(border=True):
                    st.markdown(f"#### {insight.get('topic')}")
                    st.write(insight.get('advice'))
                    if insight.get('resources'):
                        st.markdown("**Studying Resources:**")
                        for r in insight.get('resources'):
                            st.markdown(f"- {r}")

