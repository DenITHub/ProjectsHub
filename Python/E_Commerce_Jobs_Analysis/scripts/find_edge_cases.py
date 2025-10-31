import os, json, re
from utils import DATA_DIR, OUTPUT_DIR

# "сильные" e-com сигналы (title/description)
STRONG = [
    "e-commerce", "ecommerce", "online shop", "onlineshop", "webshop",
    "shopify", "shopware", "amazon", "seller central", "marketplace",
    "crm", "seo", "sea", "sem", "performance marketing", "fulfillment"
]
# "слабые/общие" слова (не считаем как сигнал в одиночку)
WEAK = ["online", "digital", "bestellung", "bestell", "order"]

def norm(s): return (s or "").lower()

def has_strong(text): return any(k in text for k in STRONG)
def has_only_weak(text): 
    return any(k in text for k in WEAK) and not has_strong(text)

def main():
    results = []
    targets = {
        "teamassistenz voll-/teilzeit (m/w/d)",
        "cost control, project & administrative assistant (m/w/d)",
        "sachbearbeiter backoffice (m/w/d) bonn",
    }
    for fname in os.listdir(DATA_DIR):
        if not fname.endswith(".json"): 
            continue
        data = json.load(open(os.path.join(DATA_DIR, fname), encoding="utf-8"))
        for job in data:
            title = norm(job.get("title"))
            desc  = norm(job.get("description"))
            if title in targets:
                hit = {
                    "file": fname,
                    "title": job.get("title"),
                    "company": job.get("companyName"),
                    "location": job.get("location"),
                    "url": job.get("jobUrl"),
                    "strong_signals": [k for k in STRONG if k in desc],
                    "weak_signals": [k for k in WEAK if k in desc],
                    "keep_if_strict": has_strong(desc),  # True только если есть сильные сигналы
                    "snippet": (job.get("description") or "").replace("\n"," ")[:220] + "..."
                }
                results.append(hit)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, "examples_strict_check.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Saved: outputs/examples_strict_check.json ({len(results)} items)")

if __name__ == "__main__":
    main()
