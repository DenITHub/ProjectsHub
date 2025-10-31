import os
import json
import re
from datetime import datetime, timedelta
from collections import Counter

# === path ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
SKILLS_DIR = os.path.join(BASE_DIR, "skills")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SKILLS_DIR, exist_ok=True)

# === IO ===
def read_json_file(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def list_data_files(folder=DATA_DIR):
    return [fn for fn in os.listdir(folder) if fn.endswith(".json")]

def load_all_json(folder=DATA_DIR):
    dataset = []
    for fname in list_data_files(folder):
        try:
            data = read_json_file(os.path.join(folder, fname))
            if isinstance(data, list):
                dataset.extend(data)
        except Exception as e:
            print(f"[WARN] Не удалось прочитать {fname}: {e}")
    return dataset

# === date ===
def safe_parse_date(s):
    if not s:
        return None
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d")
    except Exception:
        return None

def filter_recent(dataset, months=6):
    cutoff = datetime.utcnow() - timedelta(days=30*months)
    out = []
    for job in dataset:
        dt = safe_parse_date(job.get("publishedAt") or job.get("date") or "")
        if dt is None or dt >= cutoff:
            out.append(job)
    return out

# === re ===
SPACE_RE = re.compile(r"\s+")

def norm(s):
    if not s:
        return ""
    return SPACE_RE.sub(" ", str(s)).strip().lower()

GENDER_TAG_RE = re.compile(
    r"""\(\s*
        (?:m|w|d|f|x|gn|div|divers|all\s+genders|alle\s+geschlechter)
        (?:\s*[/\-|]\s*
            (?:m|w|d|f|x|gn|div|divers)
        )*
        \s*\)
    """,
    re.I | re.X
)

def strip_gender_suffix_display(s: str) -> str:
    s = "" if s is None else s
    s = s.replace("–", "-").replace("—", "-")
    s = GENDER_TAG_RE.sub("", s)
    s = SPACE_RE.sub(" ", s).strip()
    return s

def norm_title(s: str) -> str:
    s = "" if s is None else s
    s = s.replace("–", "-").replace("—", "-")
    s = GENDER_TAG_RE.sub("", s)               
    s = SPACE_RE.sub(" ", s).strip().lower()   
    return s


def deduplicate_records(dataset):
    seen = set()
    unique = []
    for job in dataset:
        key = (norm_title(job.get("title")), norm(job.get("companyName")), norm(job.get("jobUrl")))
        if key not in seen:
            unique.append(job)
            seen.add(key)
    return unique

# === language ===
DE_TOKENS = {"und","der","die","das","mit","für","bei","im","auf","kein","oder","sowie","kenntnisse"}
EN_TOKENS = {"and","the","with","for","in","on","without","or","also","skills"}

def detect_lang(text):
    if not text:
        return "unknown"
    txt = f" {text.lower()} "
    de = sum(txt.count(f" {t} ") for t in DE_TOKENS)
    en = sum(txt.count(f" {t} ") for t in EN_TOKENS)
    # 
    if de >= en * 2 and de >= 3:
        return "de"
    if en >= de * 2 and en >= 3:
        return "en"
    if de >= 2 and en >= 2:
        return "bilingual"
    if de >= 2:
        return "de"
    if en >= 2:
        return "en"
    return "unknown"


# === Clusters ===
MARKETPLACE_WORDS = {
    "marketplace","marktplatz","amazon","seller central","ebay","zalando","otto","kaufland","temu","tiktok shop",
    "listing","a+ content","product detail page","pdp","feed-management","plentymarkets","pim","shopware"
}
ONLINE_MARKETING_WORDS = {
    "online marketing","performance","seo","sea","sem","google ads","search ads 360","campaign","crm",
    "email","newsletter","analytics","matomo","content","cms","conversion","roas"
}
ONLINE_SALES_WORDS = {
    "vertrieb","sales","auftragsbearbeitung","order","kaufmännisch","lager","fulfillment","retouren",
    "inventory","warenwirtschaft","logistik","customer service","kundenservice","support","ticket"
}

MARKETPLACE_WORDS.update({"sellercentral", "account health", "buy box"})
ONLINE_MARKETING_WORDS.update({"cpc", "cpm", "ctr", "performance marketing", "meta ads"})
ONLINE_SALES_WORDS.update({"auftrag", "rechnung", "mahnen", "bestellung"})


def categorize_direction(job):
    text = f"{job.get('title','')} {job.get('description','')}".lower()
    m  = any(w in text for w in MARKETPLACE_WORDS)
    om = any(w in text for w in ONLINE_MARKETING_WORDS)
    osales = any(w in text for w in ONLINE_SALES_WORDS)
    flags = [m, om, osales]
    if flags.count(True) == 1:
        return "marketplaces" if m else ("online_marketing" if om else "online_sales")
    if flags.count(True) == 0:
        return "unclear"
    return "mixed"

# title e-commerce (title)
ECOM_TITLE_KEYWORDS = {
    "e-commerce", "ecommerce", "online shop", "onlineshop",
    "marketplace", "marktplatz", "amazon", "shopify", "shopware",
    "online marketing", "digital marketing", "performance marketing",
    "seo", "sem", "sea", "crm", "sales (online", "vertrieb (online"
}

# === utils ===
def to_percent(counts_dict):
    total = sum(counts_dict.values()) or 1
    return {k: round(v*100.0/total, 2) for k, v in counts_dict.items()}

def top_n(counter_like, n=15):
    if isinstance(counter_like, dict):
        counter_like = Counter(counter_like)
    return counter_like.most_common(n)
