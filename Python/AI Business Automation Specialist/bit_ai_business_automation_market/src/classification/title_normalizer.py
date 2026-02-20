import re
from typing import Optional

TITLE_NORMALIZATION_RULES = [
    ("ai_business_automation_specialist", [
        r"\bai business automation specialist\b",
        r"\bki[-\s]?business[-\s]?automation[-\s]?spezialist",
    ]),
    ("ai_automation_specialist", [
        r"\bai automation specialist\b",
        r"\bki[-\s]?automation",
    ]),
    ("business_process_automation_specialist", [
        r"business process automation",
        r"geschäftsprozessautomati(s|z)ierung",
        r"process automation specialist",
    ]),
    ("business_analyst", [
        r"\bbusiness[-\s]?analyst",
    ]),
    ("digital_analyst", [
        r"\bdigital[-\s]?analyst",
        r"\bweb[-\s]?analyst",
    ]),
    ("data_scientist", [
        r"\bdata scientist\b",
    ]),
    ("process_manager", [
        r"prozess[-\s]?manager",
        r"process manager",
    ]),
    ("crm_automation_specialist", [
        r"crm.*automation",
        r"marketing automation specialist",
    ]),
    ("generic_ai_role", [
        r"\bai\b",
        r"\bki\b",
        r"artificial intelligence",
        r"machine learning",
    ]),
]


def normalize_title(raw_title: str) -> Optional[str]:
    """
    Heuristically map a raw job title to a normalized cluster.
    Returns a string cluster id or None if no clear mapping.
    """
    if not raw_title:
        return None

    t = raw_title.strip().lower()

    # Hard-clean some noise
    t = re.sub(r"\s+", " ", t)

    for cluster, patterns in TITLE_NORMALIZATION_RULES:
        for pattern in patterns:
            if re.search(pattern, t, flags=re.IGNORECASE):
                return cluster

    return None
