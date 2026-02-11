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