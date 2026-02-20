import re
from skills_dictionary import HARD_SKILLS, TOOLS, SOFT_SKILLS

def extract_skills_from_text(text: str):
    text = text.lower()

    found = {
        "hard_skills": set(),
        "tools": set(),
        "soft_skills": set()
    }

    for group, keywords in HARD_SKILLS.items():
        for kw in keywords:
            if kw in text:
                found["hard_skills"].add(group)

    for group, keywords in TOOLS.items():
        for kw in keywords:
            if kw in text:
                found["tools"].add(group)

    for kw in SOFT_SKILLS:
        if kw in text:
            found["soft_skills"].add(kw)

    return found
