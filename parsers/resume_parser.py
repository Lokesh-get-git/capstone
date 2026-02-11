import re
from pathlib import Path
from typing import BinaryIO, Union
from PyPDF2 import PdfReader
from utils.logger import get_logger

logger = get_logger(__name__)

def extract_text_from_pdf(file: Union[BinaryIO, str, Path]) -> str:
    # Extract raw text from a PDF file
    try:
        reader = PdfReader(file)
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        
        full_text = "\n".join(text_parts)
        logger.info(f"Extracted {len(full_text)} characters from PDF")
        return full_text
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        raise

def extract_text_from_txt(file: Union[BinaryIO, str, Path]) -> str:
    #Read raw text from a .txt file
    try:
        if isinstance(file, (str, Path)):
            with open(file, "r", encoding="utf-8") as f:
                return f.read()
        else:
            content = file.read()
            return content.decode("utf-8") if isinstance(content, bytes) else content
    except Exception as e:
        logger.error(f"Failed to extract text from TXT: {e}")
        raise

def extract_text(file: Union[BinaryIO, str, Path], filename: str = "") -> str:
    #Wrapper to auto-detect file type and extract text
    if filename.lower().endswith(".pdf") or (isinstance(file, str) and file.lower().endswith(".pdf")):
        return extract_text_from_pdf(file)
    else:
        return extract_text_from_txt(file)