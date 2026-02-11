from parsers.resume_parser import parse_resume_sections, extract_text,extract_claims_from_sections
import pprint
file_path = "sample_resume.txt"
text = extract_text(file_path)
sections = parse_resume_sections(text)
claims = extract_claims_from_sections(sections)
pprint.pprint(claims)