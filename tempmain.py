from parsers.resume_parser import parse_resume_sections, extract_text,extract_claims_from_sections
import pprint
from utils.logger import get_logger
logger = get_logger(__name__)
file_path = "sample_resume.txt"
text = extract_text(file_path)
sections = parse_resume_sections(text)
claims = extract_claims_from_sections(sections)
pprint.pprint(claims)
logger.info(claims)
