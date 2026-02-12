# from parsers.resume_parser import parse_resume_sections, extract_text,extract_claims_from_sections
# import pprint
from utils.logger import get_logger
logger = get_logger(__name__)
# file_path = "del_resume.pdf"
# text = extract_text(file_path)
# sections = parse_resume_sections(text)
# claims = extract_claims_from_sections(sections)
# pprint.pprint(claims)
# logger.info(claims)


# from nlp.tokenizer import count_tokens, truncate_text

# sample_text = """
# Led a team of 8 engineers to redesign the payment processing system,
# reducing transaction failures by 40%.
# Implemented CI/CD pipeline using Jenkins and Docker, cutting release time
# from 2 weeks to 2 days.
# Built REST APIs serving 50,000 daily users using FastAPI.
# """

# print("---- TOKEN COUNT ----")
# print(count_tokens(sample_text))

# print("\n---- TRUNCATED TEXT (50 tokens) ----")
# print(truncate_text(sample_text, 50))

# from parsers.resume_parser import extract_text, parse_resume_sections, extract_claims_from_sections
# from nlp.clarity_scorer import score_clarity

# # load resume
# text = extract_text("sample_resume.txt")

# # parse
# sections = parse_resume_sections(text)

# # claims
# claims = extract_claims_from_sections(sections)

# print("\n=== CLAIM CLARITY ANALYSIS ===\n")

# for claim in claims:
#     result = score_clarity(claim["text"])
#     print("CLAIM:")
#     print(claim["text"])
#     print("CLARITY:", result)
#     print("-" * 60)
#     logger.info(result)

# from sklearn.feature_extraction.text import TfidfVectorizer
# from nlp.tokenizer import clean_text_for_tfidf

# claims = [
#     "Developed RESTful APIs using FastAPI and PostgreSQL",
#     "Built machine learning model using Scikit-learn and Pandas",
#     "Created CI/CD pipeline with Docker and GitHub Actions",
# ]

# job_description = """
# Looking for a backend engineer with experience in FastAPI, databases,
# API development, and scalable web services.
# """

# cleaned_claims = [clean_text_for_tfidf(c) for c in claims]
# cleaned_job = clean_text_for_tfidf(job_description)

# print("CLEANED CLAIMS:")
# for c in cleaned_claims:
#     print("-", c)


# vectorizer = TfidfVectorizer()
# documents = cleaned_claims + [cleaned_job]

# tfidf_matrix = vectorizer.fit_transform(documents)

# from sklearn.metrics.pairwise import cosine_similarity

# job_vector = tfidf_matrix[-1]
# claim_vectors = tfidf_matrix[:-1]

# similarities = cosine_similarity(job_vector, claim_vectors)

# print("\nSIMILARITY TO JOB DESCRIPTION:")
# for claim, score in zip(claims, similarities[0]):
#     print(f"{round(score, 3)}  ->  {claim}")
#     logger.info(f"{round(score, 3)}  ->  {claim}")

# from nlp.keyword_extractor import extractor

# sample_claims = [
#     "Developed REST APIs using FastAPI and PostgreSQL deployed on AWS using Docker.",
#     "Built machine learning model using Python, Pandas and Scikit-learn.",
#     "Implemented CI/CD pipeline with GitHub Actions and Jenkins.",
#     "Created frontend dashboard using React and TypeScript.",
#     "Optimized Redis caching improving response time by 40%."
# ]

# print("\n---- KEYWORD EXTRACTION DEMO ----\n")

# for claim in sample_claims:
#     print("CLAIM:")
#     print(claim)

#     keywords = extractor.extract_keywords(claim)
#     print("KEYWORDS:")
#     for category, words in keywords.items():
#         print(f"  {category}: {words}")

#     print("-" * 50)
#     logger.info(keywords)
# from nlp.ontology import get_implied_skills

# explicit = {"fastapi", "postgresql", "docker"}

# expanded = get_implied_skills(explicit)

# print("Explicit skills:")
# print(explicit)

# print("\nImplied knowledge:")
# for s in sorted(expanded):
#     print("-", s)


# from nlp.cross_reference import cross_reference_claims

# claims = [
#     {"text": "Built REST APIs using FastAPI and PostgreSQL", "section": "projects"},
#     {"text": "Trained machine learning models using scikit-learn", "section": "projects"},
# ]

# result = cross_reference_claims(claims)

# print("\nEXPLICIT SKILLS:")
# print(result["explicit_skills"])

# print("\nIMPLIED SKILLS:")
# print(result["implied_skills"])

# print("\nPOTENTIAL INTERVIEW GAPS:")
# print(result["potential_gaps"])

# print("\nPER CLAIM ANALYSIS:")
# for c in result["per_claim"]:
#     print("\nClaim:", c["claim"])
#     print("Gaps:", c["gaps"])

# output:
# EXPLICIT SKILLS:
# ['fastapi', 'machine learning', 'rest api', 'scikit-learn']      

# IMPLIED SKILLS:
# ['api', 'authentication', 'backend', 'caching', 'database design', 'evaluation metrics', 'fastapi', 'http', 'http methods', 'idempotency', 'machine learning', 'overfitting', 'python', 'rest', 'rest api', 'scikit-learn', 'status codes', 'supervised learning']  

# POTENTIAL INTERVIEW GAPS:
# ['api', 'authentication', 'backend', 'caching', 'database design', 'evaluation metrics', 'http', 'http methods', 'idempotency', 'overfitting', 'python', 'rest', 'status codes', 'supervised learning']

# PER CLAIM ANALYSIS:

# Claim: Built REST APIs using FastAPI and PostgreSQL
# Gaps: {'backend', 'caching', 'http', 'http methods', 'idempotency', 'rest', 'database design', 'api', 'authentication', 'status codes', 'python'}

# Claim: Trained machine learning models using scikit-learn        
# Gaps: {'evaluation metrics', 'supervised learning', 'overfitting'}

# from parsers.resume_parser import extract_text, parse_resume_sections, extract_claims_from_sections
# from ml.feature_builder import build_feature_vector

# # ---- Load a resume ----
# resume_path = "sample_resume.txt"  # put any resume pdf here

# print("\n=== STEP 1: Extract text ===")
# text = extract_text(resume_path)
# print(f"Characters extracted: {len(text)}")

# print("\n=== STEP 2: Parse sections ===")
# sections = parse_resume_sections(text)
# print("Sections detected:", list(sections.keys()))

# print("\n=== STEP 3: Extract claims ===")
# claims = extract_claims_from_sections(sections)
# print(f"Total claims: {len(claims)}")

# # show first 3 claims
# for i, c in enumerate(claims[:3], 1):
#     print(f"\nClaim {i}:")
#     print(c["text"])

# print("\n=== STEP 4: Feature Extraction ===")

# example_claim = claims[0]
# features = build_feature_vector(example_claim)

# print("\nFeature Vector:")
# for k, v in features.items():
#     print(f"{k:25} : {v}")


# Step 1: Generate training data (run once)
# from ml.synthetic_data import generate_synthetic_dataset
# df = generate_synthetic_dataset(200)
# df.to_csv("synthetic_resume_training.csv", index=False)
# print(f"Generated {len(df)} training samples")

# # Step 2: Train the classifier
# from ml.risk_classifier import RiskClassifier
# clf = RiskClassifier()
# metrics = clf.train("synthetic_resume_training.csv")
# print("\n=== MODEL METRICS ===")
# for k, v in metrics.items():
#     print(f"  {k}: {v}")

# # Step 3: Show feature importance (explainability)
# print("\n=== TOP RISK SIGNALS ===")
# for name, weight in clf.get_feature_importance(10):
#     direction = "→ HIGH risk" if weight > 0 else "→ LOW risk"
#     print(f"  {name:30} : {weight:+.4f}  {direction}")

# # Step 4: Predict on real claims
# from ml.feature_builder import build_feature_vector

# test_claims = [
#     {"text": "Led a team of 8 engineers to redesign payment system, reducing failures by 40%", "section": "experience"},
#     {"text": "Responsible for backend maintenance", "section": "experience"},
#     {"text": "Built CI/CD pipeline with Docker and Jenkins cutting release time by 3x", "section": "projects"},
#     {"text": "Helped with various projects", "section": "experience"},
# ]

# print("\n=== PREDICTIONS ===")
# for claim in test_claims:
#     features = build_feature_vector(claim)
#     result = clf.predict(features)
#     print(f"\n  \"{claim['text'][:60]}...\"")
#     print(
#         f"Risk: {result['risk_label'].upper()} "
#         f"(confidence: {result['risk_score']:.1f}%, "
#         f"prob: {result['risk_probability']:.4f})"
#     )


# =========================================================
# FULL PIPELINE TEST: Both models on real resumes
# =========================================================
# from parsers.resume_parser import extract_text, parse_resume_sections, extract_claims_from_sections
# from ml.feature_builder import build_feature_vector
# from ml.risk_classifier import RiskClassifier
# from ml.readiness_scorer import ReadinessScorer

# # Load models
# clf = RiskClassifier.load("models/risk_model.joblib")
# scorer = ReadinessScorer.load("models/readiness_model.joblib")

# RESUMES = ["sample_resume.txt", "del_resume.pdf"]

# for resume_path in RESUMES:
#     print("\n" + "=" * 70)
#     print(f"  RESUME: {resume_path}")
#     print("=" * 70)

#     # Step 1: Extract text
#     text = extract_text(resume_path, filename=resume_path)
#     print(f"\nExtracted {len(text)} characters")

#     # Step 2: Parse sections
#     sections = parse_resume_sections(text)
#     print(f"Sections: {list(sections.keys())}")

#     # Step 3: Extract claims
#     claims = extract_claims_from_sections(sections)
#     print(f"Claims extracted: {len(claims)}")

#     # Step 4: Risk Classifier — per-claim analysis
#     print(f"\n--- RISK ANALYSIS (per claim) ---")
#     for i, claim in enumerate(claims, 1):
#         features = build_feature_vector(claim)
#         risk = clf.predict(features)
#         label = risk["risk_label"].upper()
#         score = risk["risk_score"]
#         print(f"  [{label:10} {score:5.1f}%] {claim['text'][:70]}")

#     # Step 5: Readiness Scorer — resume-level score (grounded by risk classifier)
#     readiness = scorer.predict_with_risk(claims, clf)
#     print(f"\n--- READINESS SCORE ---")
#     print(f"  Score: {readiness['readiness_score']}/100")
#     print(f"  Level: {readiness['readiness_level'].upper()}")
#     print(f"  Breakdown:")
#     for k, v in readiness["breakdown"].items():
#         print(f"    {k}: {v}")

#     # Step 6: Vulnerability Mapping (Commit 25)
#     from ml.vulnerability_mapper import map_resume_vulnerabilities
#     vuln_report = map_resume_vulnerabilities(claims, clf)

#     print(f"\n--- VULNERABILITY MAP ---")
#     print(f"  Strong claims: {vuln_report['summary']['strong_claims']}/{vuln_report['summary']['total_claims']}")
#     print(f"  Strength ratio: {vuln_report['summary']['strength_ratio']}%")

#     if vuln_report["top_vulnerabilities"]:
#         print(f"\n  Top Weaknesses:")
#         for v in vuln_report["top_vulnerabilities"]:
#             print(f"    ⚠ {v['label']}: {v['count']} claims ({v['percentage']}%)")

#     if vuln_report["interview_focus_areas"]:
#         print(f"\n  Interview Focus Areas:")
#         for area in vuln_report["interview_focus_areas"]:
#             print(f"    → {area['area']}: {area['probe']}")

import os
import sys
from pprint import pprint

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.logger import get_logger
from parsers.resume_parser import extract_text
from agents.resume_analyst import resume_analyst_node
from agents.state import AgentState

logger = get_logger(__name__)

def run_demo():
    print("=== Resume Analyst Demo ===")
    
    # 1. Load Resume Text
    resume_path = "sample_resume.txt"
    if not os.path.exists(resume_path):
        # Fallback if file missing
        print(f"Warning: {resume_path} not found. Using sample text.")
        resume_text = """
        John Doe
        Software Engineer
        
        Summary
        Experienced developer with 5 years in Python and backend systems.
        
        Experience
        Software Engineer | Tech Corp | 2020 - Present
        - Built a scalable API using FastAPI and deployed on Kubernetes.
        - Optimized database queries reducing latency by 50%.
        - Led a team of 3 juniors.
        
        Skills
        Python, Django, SQL, Docker, AWS
        """
    else:
        print(f"Loading {resume_path}...")
        resume_text = extract_text(resume_path)

    # 2. Initialize State
    state = AgentState(
        resume_text=resume_text,
        job_description="", 
        claims=[],
        risk_analysis={},
        readiness_analysis={},
        vulnerability_map={},
        skill_gap_analysis={},
        messages=[],
        errors=[]
    )
    
    # 3. Run Analyst Node
    print("\nRunning Resume Analyst Node...")
    try:
        result = resume_analyst_node(state)
        
        # 4. Display Results
        print("\n=== ANALYSIS RESULTS ===")
        
        print(f"\n[Readiness Score]: {result['readiness_analysis'].score:.1f}/100 ({result['readiness_analysis'].level})")
        
        print("\n[Risk Analysis Summary]")
        print(result['risk_analysis'].summary)
        
        print("\n[Skill Gap Analysis]")
        gaps = result.get('skill_gap_analysis')
        if gaps:
            print(f"Explicit Skills: {', '.join(gaps.explicit_skills)}")
            print(f"Implied Skills:  {', '.join(gaps.implied_skills)}")
            print(f"MISSING GAPS:    {', '.join(gaps.missing_skills)}")
        else:
            print("No gap analysis returned.")

        print("\n[Vulnerability Map]")
        vm = result['vulnerability_map']
        print(f"Strength Ratio: {vm.strength_ratio:.1f}%")
        print("Top Weaknesses:")
        for w in vm.top_weaknesses:
            print(f"  - {w}")
            
        print("\n[Interview Focus Areas]")
        for f in vm.interview_focus:
            print(f"  - {f}")
            
        print("\n[Analyzed Claims (Sample)]")
        # Print first few claims to verify risk scoring
        for i, c in enumerate(result['claims'][:3]):
            print(f"{i+1}. {c.text[:60]}... (Risk: {c.risk_score:.2f}, Label: {c.risk_label})")
            if c.vulnerabilities:
                print(f"   Vulnerabilities: {', '.join(c.vulnerabilities)}")

    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"Error: {e}")

if __name__ == "__main__":
    run_demo()