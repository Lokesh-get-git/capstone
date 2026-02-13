
import new_resume_parser
from parsers import resume_parser as old_resume_parser
import pprint

RESUME_FILE = "del_resume.pdf"

print(f"Comparing Parsers on: {RESUME_FILE}")

# --- OLD PARSER (Current Production) ---
print("\n" + "="*50)
print("OLD PARSER RESULTS")
print("="*50)
claims_old = []
try:
    text_old = old_resume_parser.extract_text(RESUME_FILE)
    sections_old = old_resume_parser.parse_resume_sections(text_old)
    # The crucial fix was in this function in 'parsers/resume_parser.py'
    claims_old = old_resume_parser.extract_claims_from_sections(sections_old)
    
    print(f"Text Length: {len(text_old)}")
    print(f"Sections Detected: {list(sections_old.keys())}")
    print(f"Total Claims: {len(claims_old)}")
    print("\nSample Claims (Old):")
    for c in claims_old[:3]:
        print(f"- [{c.get('section', 'unk')}] {c['text'][:100]}...")

except Exception as e:
    print(f"Old parser failed: {e}")


# --- NEW PARSER (New Module) ---
print("\n" + "="*50)
print("NEW PARSER RESULTS")
print("="*50)
parsed_new = None
try:
    # New parser returns a 'ParsedResume' object
    parsed_new = new_resume_parser.parse_resume(RESUME_FILE)
    
    print(f"Text Length: {len(parsed_new.raw_text)}")
    print(f"Sections Detected: {list(parsed_new.sections.keys())}")
    print(f"Total Claims: {len(parsed_new.claims)}")
    print("\nSample Claims (New):")
    for c in parsed_new.claims[:3]:
        # New claims are objects, not dicts
        print(f"- [{c.section}] {c.text[:100]}... (Type: {c.claim_type})")

except Exception as e:
    print(f"New parser failed: {e}")
    import traceback
    traceback.print_exc()

# --- COMPARISON SUMMARY ---
if parsed_new and claims_old:
    print("\n" + "="*50)
    print("COMPARISON")
    print("="*50)
    diff_claims = len(parsed_new.claims) - len(claims_old)
    print(f"Claim Difference: {diff_claims} (New - Old)")

    # Check if section keys match
    old_keys = set(sections_old.keys())
    new_keys = set(parsed_new.sections.keys())

    print(f"Only in Old Sections: {old_keys - new_keys}")
    print(f"Only in New Sections: {new_keys - old_keys}")
else:
    print("\nCannot compare: One or both parsers failed.")
