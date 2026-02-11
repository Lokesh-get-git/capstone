# from parsers.resume_parser import parse_resume_sections, extract_text,extract_claims_from_sections
# import pprint
# from utils.logger import get_logger
# logger = get_logger(__name__)
# file_path = "del_resume.pdf"
# text = extract_text(file_path)
# sections = parse_resume_sections(text)
# claims = extract_claims_from_sections(sections)
# pprint.pprint(claims)
# logger.info(claims)
from nlp.tokenizer import count_tokens, truncate_text

sample_text = """
Led a team of 8 engineers to redesign the payment processing system,
reducing transaction failures by 40%.
Implemented CI/CD pipeline using Jenkins and Docker, cutting release time
from 2 weeks to 2 days.
Built REST APIs serving 50,000 daily users using FastAPI.
"""

print("---- TOKEN COUNT ----")
print(count_tokens(sample_text))

print("\n---- TRUNCATED TEXT (50 tokens) ----")
print(truncate_text(sample_text, 50))

