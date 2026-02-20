from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REFERENCE_DIR = DATA_DIR / "reference"

ROLE_PROFILE_PATH = REFERENCE_DIR / "role_profile_ai_business_automation.json"
TITLE_DICTIONARY_PATH = REFERENCE_DIR / "title_dictionary_de_at_ch.csv"
OFFICIAL_RESOURCES_PATH = REFERENCE_DIR / "official_resources_list_de_at_ch.json"


def ensure_dirs() -> None:
    """Ensure that the basic directory structure exists."""
    for p in [DATA_DIR, RAW_DIR, PROCESSED_DIR, REFERENCE_DIR]:
        p.mkdir(parents=True, exist_ok=True)
# --- Official catalogs fetch config ---

OFFICIAL_KEYWORDS_DE = [
    "Künstliche Intelligenz",
    "KI",
    "Automation",
    "Prozess",
    "Business",
    "Digitalisierung"
]

OFFICIAL_KEYWORDS_AT = [
    "Künstliche Intelligenz",
    "KI",
    "Automation",
    "Digitalisierung",
    "Prozess"
]

OFFICIAL_KEYWORDS_CH = [
    "Künstliche Intelligenz",
    "KI",
    "Automation",
    "Digital Business",
    "Prozess"
]

MAX_BERUFE_DE = 200      # целевой объём для BERUFENET
MAX_BERUFE_AT = 50       # целевой объём для AMS
MAX_BERUFE_CH = 50       # целевой объём для BVZ
