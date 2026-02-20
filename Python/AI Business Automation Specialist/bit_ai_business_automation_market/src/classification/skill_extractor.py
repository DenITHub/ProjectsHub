import re
from typing import Dict, List

SKILL_KEYWORDS = {
    "skill_n8n": [r"\bn8n\b"],
    "skill_make": [r"\bmake\.com\b", r"\bintegromat\b"],
    "skill_zapier": [r"\bzapier\b"],
    "skill_power_automate": [r"power automate", r"microsoft flow"],
    "skill_llm": [r"\bllm\b", r"large language model", r"chatgpt", r"gpt-", r"azure openai"],
    "skill_api": [r"\bapi\b", r"rest api"],
    "skill_sql": [r"\bsql\b"],
    "skill_python": [r"\bpython\b"],
    "skill_gdpr": [r"\bgdpr\b", r"ds(g|g)vo"],
    "skill_bpmn": [r"\bbpmn\b"],
}


def extract_skills(text: str) -> Dict[str, int]:
    """
    Very simple keyword-based skill extractor.
    Returns dict {skill_col: 0/1}.
    """
    if not text:
        text = ""
    lower_text = text.lower()

    result = {}
    for skill_col, patterns in SKILL_KEYWORDS.items():
        found = any(re.search(p, lower_text) for p in patterns)
        result[skill_col] = int(bool(found))

    return result


def extract_skills_bulk(texts: List[str]) -> List[Dict[str, int]]:
    return [extract_skills(t) for t in texts]
