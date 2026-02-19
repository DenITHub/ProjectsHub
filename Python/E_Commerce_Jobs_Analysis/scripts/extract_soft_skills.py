# scripts/7_extract_soft_skills.py
import os, json, re
from collections import Counter
from utils import DATA_DIR, OUTPUT_DIR, load_all_json, filter_recent, deduplicate_records

SKILLS_PATH = os.path.join(os.path.dirname(DATA_DIR), "skills", "soft_skills_dict.json")

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def word_boundary(pattern: str) -> str:
    
    return r"(?:^|[^A-Za-zÄÖÜäöüß0-9])" + re.escape(pattern) + r"(?:$|[^A-Za-zÄÖÜäöüß0-9])"

def find_soft_skills(text: str, soft_dict: dict) -> list:
    if not text:
        return []
    t = text.lower()
    found = set()
    for key, variants in soft_dict.items():
        for v in variants:
            if re.search(word_boundary(v.lower()), t, flags=re.I):
                found.add(key)
                break
    return sorted(found)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 
    soft_dict = load_json(SKILLS_PATH)

    # 
    raw = load_all_json(DATA_DIR)
    recent = filter_recent(raw, months=6)
    jobs = deduplicate_records(recent)

    # 
    enriched = []
    bag = []
    for j in jobs:
        text = f"{j.get('title','')} \n {j.get('description','')}"
        softs = find_soft_skills(text, soft_dict)
        if softs:
            j["soft_skills"] = softs
            bag.extend(softs)
        enriched.append(j)

    # 
    counts = Counter(bag)
    counts_sorted = dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

    with open(os.path.join(OUTPUT_DIR, "soft_skills_count.json"), "w", encoding="utf-8") as f:
        json.dump(counts_sorted, f, ensure_ascii=False, indent=2)

    # 
    with open(os.path.join(OUTPUT_DIR, "dataset_with_soft_skills.json"), "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

    # 
    try:
        import matplotlib.pyplot as plt
        top = list(counts.most_common(15))
        if top:
            labels = [k for k, _ in top][::-1]
            values = [v for _, v in top][::-1]
            plt.figure(figsize=(10, 5))
            plt.barh(labels, values)
            plt.title("Top-15 Soft Skills (E-Commerce DE)")
            plt.tight_layout()
            plt.savefig(os.path.join(OUTPUT_DIR, "soft_skills_top15.png"))
            plt.close()
    except Exception as e:
        print(f"[WARN] Plot skipped: {e}")

    print(f"Soft skills extracted. Unique={len(counts)}, saved to outputs/soft_skills_count.json")

if __name__ == "__main__":
    main()
