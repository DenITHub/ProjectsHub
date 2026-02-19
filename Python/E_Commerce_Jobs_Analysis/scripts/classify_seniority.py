# scripts/classify_seniority.py
import os, json, re
from collections import Counter, defaultdict
from utils import DATA_DIR, OUTPUT_DIR, load_all_json, filter_recent, deduplicate_records, categorize_direction

LEVEL_PATTERNS = {
    "senior":  [
        r"\bsenior\b", r"\bexpert\b", r"\bprincipal\b",
        r"\bteam\s*lead\b", r"\blead\b", r"\b(head|leiter)(in)?\b"
    ],
    "junior":  [
        r"\bjunior\b", r"\btrainee\b", r"\bwerkstudent(in)?\b", r"\bpraktikant(in)?\b",
        r"\bentry[-\s]*level\b", r"\bassistant\b", r"\bassistenz\b"
    ],
    "mid":     [
        r"\b(specialist|professional)\b", r"\bberater(in)?\b", r"\bmanager(in)?\b",
        r"\bmit\s+erfahrung\b"
    ]
}

def detect_level(text: str) -> str:
    if not text:
        return "unspecified"
    t = text.lower()

    # Senior/Lead 
    for pat in LEVEL_PATTERNS["senior"]:
        if re.search(pat, t, flags=re.I):
            return "senior"
    # Junior
    for pat in LEVEL_PATTERNS["junior"]:
        if re.search(pat, t, flags=re.I):
            return "junior"
    # Mid
    for pat in LEVEL_PATTERNS["mid"]:
        if re.search(pat, t, flags=re.I):
            return "mid"
    return "unspecified"

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    raw = load_all_json(DATA_DIR)
    recent = filter_recent(raw, months=6)
    jobs = deduplicate_records(recent)

    overall = Counter()
    by_dir = defaultdict(Counter)

    for j in jobs:
        text = f"{j.get('title','')} \n {j.get('description','')}"
        lvl = detect_level(text)
        overall[lvl] += 1

        direction = categorize_direction(text)
        by_dir[direction][lvl] += 1

    # 
    with open(os.path.join(OUTPUT_DIR, "seniority_stats.json"), "w", encoding="utf-8") as f:
        json.dump(dict(overall), f, ensure_ascii=False, indent=2)

    with open(os.path.join(OUTPUT_DIR, "seniority_by_direction.json"), "w", encoding="utf-8") as f:
        json.dump({d: dict(c) for d, c in by_dir.items()}, f, ensure_ascii=False, indent=2)

    # 
    try:
        import matplotlib.pyplot as plt

        # 
        labels = list(overall.keys())
        values = [overall[k] for k in labels]
        plt.figure(figsize=(6, 4))
        plt.bar(labels, values)
        plt.title("Seniority Distribution (All)")
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, "seniority_overall.png"))
        plt.close()

        # 
        dirs = list(by_dir.keys())
        lvls = ["junior", "mid", "senior", "unspecified"]
        data = [[by_dir[d][lv] for lv in lvls] for d in dirs]
        # 
        import numpy as np
        x = np.arange(len(dirs))
        w = 0.2
        plt.figure(figsize=(10, 5))
        for i, lv in enumerate(lvls):
            plt.bar(x + (i-1.5)*w, [by_dir[d][lv] for d in dirs], width=w, label=lv.title())
        plt.xticks(x, dirs, rotation=15)
        plt.title("Seniority by Direction")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, "seniority_by_direction.png"))
        plt.close()

    except Exception as e:
        print(f"[WARN] Plot skipped: {e}")

    print("Seniority stats saved: outputs/seniority_stats.json, outputs/seniority_by_direction.json")

if __name__ == "__main__":
    main()
