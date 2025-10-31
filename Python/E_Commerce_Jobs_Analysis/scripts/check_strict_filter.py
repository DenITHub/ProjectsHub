import os, json
from utils import DATA_DIR, OUTPUT_DIR

# === FILTERS ===

# --- MARKETPLACES ---
STRONG_MARKETPLACE = [
    "marketplace", "amazon", "seller central", "vendor central",
    "ebay", "zalando", "otto", "kaufland", "temu", "tiktok shop",
    "product feed", "a+ content", "product detail page", "pdp",
    "listing", "asin", "buy box", "plentymarkets", "pim", "feed management",
    "content upload", "catalog management", "product data", "repricing",
    "shopware", "shopify", "woocommerce", "magento", "erp system",
    "account health", "brand registry"
]
WEAK_MARKETPLACE = [
    "artikelpflege", "produktdatenpflege", "marktplatz", "content",
    "produkte", "sortiment", "preis", "angebot", "verkaufsplattform", "feed"
]

# --- ONLINE SALES ---
STRONG_SALES = [
    "order management", "auftragsbearbeitung", "sales", "vertrieb", "verkauf",
    "customer service", "kundenservice", "crm", "b2b", "b2c", "fulfillment",
    "retouren", "logistik", "versand", "lager", "inventory",
    "warenwirtschaftssystem", "rechnung", "fakturierung", "support ticket",
    "sap", "erp", "jira", "zendesk", "helpdesk", "crm system"
]
WEAK_SALES = [
    "kundenkontakt", "bestellung", "bestell", "support", "kundenbetreuung",
    "lieferung", "service", "assistenz", "büro", "office", "auftrag"
]

# --- ONLINE MARKETING ---
STRONG_MARKETING = [
    "online marketing", "digital marketing", "performance marketing",
    "seo", "sea", "sem", "google ads", "adwords", "meta ads", "facebook ads",
    "campaign management", "campaign", "crm marketing", "email marketing",
    "newsletter", "content marketing", "copywriting", "cms", "wordpress",
    "analytics", "google analytics", "matomo", "conversion", "roas", "cpc",
    "ctr", "display ads", "retargeting", "remarketing", "tracking",
    "tag manager", "ga4"
]
WEAK_MARKETING = [
    "marketing", "advertising", "kommunikation", "media", "design",
    "grafik", "content", "brand", "strategie", "social media", "kampagne"
]

# --- fallback (unclear) ---
STRONG_GENERAL = STRONG_MARKETPLACE + STRONG_SALES + STRONG_MARKETING
WEAK_GENERAL = WEAK_MARKETPLACE + WEAK_SALES + WEAK_MARKETING


def categorize_direction(text: str):
    text = text.lower()
    m  = any(w in text for w in STRONG_MARKETPLACE)
    om = any(w in text for w in STRONG_MARKETING)
    osales = any(w in text for w in STRONG_SALES)
    flags = [m, om, osales]
    if flags.count(True) == 1:
        return "marketplaces" if m else ("online_marketing" if om else "online_sales")
    if flags.count(True) == 0:
        return "unclear"
    return "mixed"


def norm(s): return (s or "").lower()

def has_strong(text, strong_list): return any(k in text for k in strong_list)
def has_any(text, strong_list, weak_list): return any(k in text for k in (strong_list + weak_list))


def main():
    total = strong = weak_only = none = 0
    examples_none = []
    by_dir = {
        "marketplaces": {"total": 0, "strong": 0, "weak": 0, "none": 0},
        "online_sales": {"total": 0, "strong": 0, "weak": 0, "none": 0},
        "online_marketing": {"total": 0, "strong": 0, "weak": 0, "none": 0},
        "unclear": {"total": 0, "strong": 0, "weak": 0, "none": 0},
        "mixed": {"total": 0, "strong": 0, "weak": 0, "none": 0}
    }

    for fname in os.listdir(DATA_DIR):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(DATA_DIR, fname)
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[WARN] Ошибка чтения {fname}: {e}")
            continue

        for job in data:
            title = norm(job.get("title"))
            desc  = norm(job.get("description"))
            text  = f"{title} {desc}"
            total += 1

            
            direction = categorize_direction(text)
            by_dir[direction]["total"] += 1

            
            if direction == "marketplaces":
                strong_list, weak_list = STRONG_MARKETPLACE, WEAK_MARKETPLACE
            elif direction == "online_sales":
                strong_list, weak_list = STRONG_SALES, WEAK_SALES
            elif direction == "online_marketing":
                strong_list, weak_list = STRONG_MARKETING, WEAK_MARKETING
            else:
                strong_list, weak_list = STRONG_GENERAL, WEAK_GENERAL

            
            if has_strong(text, strong_list):
                strong += 1
                by_dir[direction]["strong"] += 1
            elif has_any(text, strong_list, weak_list):
                weak_only += 1
                by_dir[direction]["weak"] += 1
            else:
                none += 1
                by_dir[direction]["none"] += 1
                if len(examples_none) < 15:
                    examples_none.append({
                        "file": fname,
                        "title": job.get("title"),
                        "company": job.get("companyName"),
                        "url": job.get("jobUrl"),
                        "direction": direction
                    })

    pct_none = round((none / total * 100), 2) if total else 0
    pct_strong = round((strong / total * 100), 2) if total else 0

    summary = {
        "total_vacancies": total,
        "with_strong_signals": strong,
        "with_only_weak_signals": weak_only,
        "without_signals": none,
        "percent_without_signals": pct_none,
        "percent_with_signals": pct_strong,
        "by_direction": by_dir,
        "examples_without_signals": examples_none
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "strict_filter_summary.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    
    print(f"\nChecked {total} vacancies (multi-direction filter)")
    print(f" - With strong e-commerce signals: {strong}")
    print(f" - With only weak signals: {weak_only}")
    print(f" - Without any signals: {none} ({pct_none}%)")

    print("\n=== Breakdown by Direction ===")
    for d, stats in by_dir.items():
        if stats["total"] == 0:
            continue
        pct = round(stats["none"] / stats["total"] * 100, 2)
        print(f"{d:18} → total {stats['total']}, none {stats['none']} ({pct}%)")

    print(f"\n📄 Saved summary: {out_path}")

if __name__ == "__main__":
    main()
