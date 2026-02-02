import unidecode
import re

def normalize_text(text: str) -> str:
    text = unidecode.unidecode(text)
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
