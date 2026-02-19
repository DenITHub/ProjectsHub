# scripts/generate_report.py
import os
import json
from urllib.parse import urlparse
from utils import OUTPUT_DIR

# ---------- helpers ----------
def load_or(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def short_url(u: str) -> str:
    if not u:
        return ""
    base = u.split("?")[0]
    try:
        p = urlparse(base)
        parts = [pp for pp in p.path.split("/") if pp]
        tail = "/".join(parts[-2:]) if len(parts) >= 2 else (parts[-1] if parts else "")
        return f"{p.netloc}/{tail}"
    except Exception:
        return base

def ensure_scheme(u: str) -> str:
    if not u:
        return ""
    return u if u.startswith("http") else ("https://" + u.lstrip("/"))

# ---------- load data ----------
skills          = load_or(f"{OUTPUT_DIR}/skills_count.json", {})
tools           = load_or(f"{OUTPUT_DIR}/tools_count.json", {})
titles          = load_or(f"{OUTPUT_DIR}/title_clusters.json", [])
langs           = load_or(f"{OUTPUT_DIR}/language_stats.json", {})
skills_by_dir   = load_or(f"{OUTPUT_DIR}/skills_by_direction.json", {})
tools_by_dir    = load_or(f"{OUTPUT_DIR}/tools_by_direction.json", {})
titles_ecom     = load_or(f"{OUTPUT_DIR}/title_clusters_ecom.json", [])
titles_ecom_dir = load_or(f"{OUTPUT_DIR}/title_clusters_by_direction_ecom.json", {})
period_info     = load_or(f"{OUTPUT_DIR}/period_info.json", {})                 # {min_date,max_date,count_after}
strict_summary  = load_or(f"{OUTPUT_DIR}/strict_filter_summary.json", {})       # QC summary
soft_counts     = load_or(f"{OUTPUT_DIR}/soft_skills_count.json", {})
seniority_total = load_or(f"{OUTPUT_DIR}/seniority_stats.json", {})
seniority_bydir = load_or(f"{OUTPUT_DIR}/seniority_by_direction.json", {})

min_date   = period_info.get("min_date", "")
max_date   = period_info.get("max_date", "")
clean_count = period_info.get("count_after", 0)

# Для QC
total    = strict_summary.get("total_vacancies", 0)
none_cnt = strict_summary.get("without_signals", 0)
pct_none = strict_summary.get("percent_without_signals", 0.0)
strong   = strict_summary.get("with_strong_signals", 0)
weak     = strict_summary.get("with_only_weak_signals", 0)
examples = strict_summary.get("examples_without_signals", [])
by_dir   = strict_summary.get("by_direction", {})

# ---------- build report ----------
report_path = os.path.join(OUTPUT_DIR, "final_report_marp.md")
parts = []

# ===== Front matter =====
parts.append("""---
marp: true
theme: gaia
paginate: true
class: lead
header: 'ICH · E-Commerce Jobs (Germany) · LinkedIn'
footer: '© ICH · E-Commerce Labor Market Analysis · 2025'
style: |
  section { font-size: 26px; line-height: 1.4; }
  h1, h2, h3 { letter-spacing: 0.2px; }
  :root { --ich-accent:#0b6cff; --ich-dark:#0f172a; }
  section.lead h1 { color: var(--ich-accent); font-weight: 800; }
  .brand{ display:flex; align-items:center; gap:16px;}
  .muted{ color:#64748b; font-size:22px;}
  section.small-text{ font-size:20px; line-height:1.3; }
---

# E-Commerce Jobs (Germany)
## LinkedIn Market Scan & Skills Analysis
<span class="muted">Internship · ICH · 2025</span>
""")

if min_date and max_date:
    parts.append(f"\n**Период выборки:** {min_date} → {max_date}  ")
if clean_count:
    parts.append(f"**Всего вакансий (после очистки):** **{clean_count}**")

# ===== Goal =====
parts.append(f"""
---

## Цель и охват

**Цель:** выявить востребованные *Hard Skills* и *Tools* для E-Commerce специалистов в Германии и отличия по направлениям.

**Охват:**
- Источник: LinkedIn, 19 JSON
- Период: *по полю `publishedAt` (последние 6 месяцев)*
- После фильтра и дедупликации: **{clean_count} вакансии**
- Языки вакансий: DE/EN/Bilingual (эвристика по стоп-словам)
""")

# ===== Methodology =====
parts.append("""
---

## Методология (кратко)

1. Очистка и дедупликация (ключ: *title + company + jobUrl*, нормализация `m/w/d`)
2. Классификация направлений:
   - **Marketplaces** · **Online Sales** · **Online Marketing**
3. Извлечение терминов (разделено на **Tools** и **Skills**)
4. Подсчёт частот и разрез по направлениям
5. Визуализации и автогенерация отчёта (`report.md`)
""")

# ===== languages =====
parts.append("""
---

## Распределение языков

![width:400px](./languages_pie.png)

*Языки вакансий по описанию: DE / EN / Bilingual / Unknown.*
""")

# ===== Skills top15 =====
parts.append("""
---

## Топ-15 Hard Skills (навыки)

![width:600px](./skills_top15.png)

**Наблюдения:** KPI/Excel/SEO/SEA/CRM стабильно в топе.
""")

# ===== Tools top15 =====
parts.append("""
---

## Топ-15 Tools (инструменты)

![width:600px](./tools_top15.png)

**Наблюдения:** Excel/MS Office, Google Ads/Analytics, API, CMS/CRM.
""")

# ===== Skills Clusters =====
parts.append("""
---

## Skills по направлениям

### Online Marketing
![width:600px](./skills_online_marketing.png)

**Фокус:** SEO · SEA · SEM · Analytics · Performance.

---

### Online Sales
![width:600px](./skills_online_sales.png)

**Фокус:** Excel · CRM · KPI · Auftragsbearbeitung · Inventory.

---

### Marketplaces
![width:600px](./skills_marketplaces.png)

**Фокус:** Amazon/Shopify/Shopware/PIM (нишевый сегмент).
""")

# ===== Tools Clusters =====
parts.append("""
---

## Tools по направлениям

### Online Marketing
![width:600px](./tools_online_marketing.png)

---

### Online Sales
![width:600px](./tools_online_sales.png)

---

### Marketplaces
![width:600px](./tools_marketplaces.png)
""")

# ===== Clusters Title =====
parts.append("""
---

## Кластеры названий (только e-commerce релевантные)

![width:600px](./titles_ecom_top20.png)

*Чёткий фокус на Online/E-Commerce/Digital-позиции.*
""")

# ===== Quality Check 1=====
parts.append("""
---

## Проверка качества — Strict Filter Validation
""")
if os.path.exists(os.path.join(OUTPUT_DIR, "quality_split_pie.png")):
    parts.append("![width:280px](./quality_split_pie.png)\n")
parts.append(
    f"**Всего вакансий:** {total}  \n"
    f"- Сильные сигналы: **{strong}**  \n"
    f"- Слабые сигналы: **{weak}**  \n"
    f"- Без сигналов: **{none_cnt}** (**{pct_none:.2f}%**)\n\n"
)
parts.append("<small>Проверка по полной выгрузке (2176). Анализ по очищенным данным (1930).</small>\n")
if examples:
    parts.append("\n**Примеры без e-commerce сигналов:**")
    for ex in examples[:2]:
        t = (ex.get('title') or '').strip()
        c = (ex.get('company') or '').strip()
        parts.append(f"- {t} — {c}")

# ===== Quality Check 2=====
parts.append("""
---

## Вакансии без сигналов по направлениям

<small>Процент вакансий без e-commerce сигналов:</small>
""")
pretty = {
    "marketplaces": "Marketplaces",
    "online_marketing": "Online Marketing",
    "online_sales": "Online Sales",
    "mixed": "Mixed",
    "unclear": "Unclear",
}
order_dirs = ["marketplaces", "online_marketing", "online_sales", "mixed", "unclear"]
for d in order_dirs:
    st  = by_dir.get(d, {})
    tot = st.get("total", 0) or 0
    n0  = st.get("none", 0) or 0
    pct = (n0 * 100.0 / tot) if tot else 0.0
    parts.append(f"- **{pretty[d]}:** {n0}/{tot} → **{pct:.2f}%**")

# ===== Soft Skills =====
parts.append("""
---

## Soft Skills Overview — Top 10
""")

if os.path.exists(os.path.join(OUTPUT_DIR, "soft_skills_top15.png")):
    parts.append("![width:500px](./soft_skills_top15.png)\n")

if soft_counts:
    parts.append("<small>")   
    for name, cnt in list(soft_counts.items())[:10]:
        parts.append(f"- **{name.title()}** — {cnt}")
    parts.append("</small>")  

parts.append(
    "\n<small>Частые: коммуникация, организация, ответственность, командная работа.</small>\n"
)


# ===== Seniority =====
parts.append("""
---

## Seniority Levels Overview
""")

parts.append('<div style="display: flex; justify-content: center; gap: 24px;">')

if os.path.exists(os.path.join(OUTPUT_DIR, "seniority_overall.png")):
    parts.append('<img src="./seniority_overall.png" width="500px">')
if os.path.exists(os.path.join(OUTPUT_DIR, "seniority_by_direction.png")):
    parts.append('<img src="./seniority_by_direction.png" width="620px">')

parts.append("</div>\n")  


if seniority_total:
    total_s = sum(seniority_total.values())
    parts.append("<small>")
    for lvl, cnt in seniority_total.items():
        pct = (cnt / total_s * 100) if total_s else 0
        parts.append(f"- **{lvl.title()}** — {cnt} ({pct:.1f}%)")
    parts.append("</small>")

parts.append(
    "\n<small>Преобладает уровень **Mid**; Senior чаще встречаются в Marketing и Marketplaces.</small>\n"
)

# ---------- write file ----------
content = "\n".join(parts)
with open(report_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Готово: {report_path}")
