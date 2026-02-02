# safety/policy.py

FORBIDDEN_PATTERNS = [
    "drop", "delete", "insert", "update", "alter",
    "ignore your rules",
    "show me the whole database",
    "system prompt",
    "api key"
]

def is_allowed_question(question: str) -> bool:
    q = question.lower()
    return not any(p in q for p in FORBIDDEN_PATTERNS)
