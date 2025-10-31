import os
import json
from utils import OUTPUT_DIR

def load_or(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

if __name__ == "__main__":
  skills = load_or(f"{OUTPUT_DIR}/skills_count.json", {})
  tools  = load_or(f"{OUTPUT_DIR}/tools_count.json", {})
  titles = load_or(f"{OUTPUT_DIR}/title_clusters.json", [])
  langs  = load_or(f"{OUTPUT_DIR}/language_stats.json", {})
  dirs_c = load_or(f"{OUTPUT_DIR}/direction_counts.json", {})
  dirs_p = load_or(f"{OUTPUT_DIR}/direction_shares.json", {})
  skills_by_dir = load_or(f"{OUTPUT_DIR}/skills_by_direction.json", {})
  tools_by_dir  = load_or(f"{OUTPUT_DIR}/tools_by_direction.json", {})
  titles_ecom = load_or(f"{OUTPUT_DIR}/title_clusters_ecom.json", [])
  top_titles_by_dir_ecom = load_or(f"{OUTPUT_DIR}/title_clusters_by_direction_ecom.json", {})



  report_path = f"{OUTPUT_DIR}/report.md"
  with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Отчёт: анализ вакансий E-Commerce (LinkedIn, DE)\n\n")

        # === 1) Summary ===
        total_jobs = sum(v for _, v in titles) if titles else 0
        f.write("## 1) Summary\n")
        f.write(f"- Общее число уникальных вакансий (после фильтра и дедупликации): **{total_jobs}**\n")
        if dirs_c:
            parts = [f"{k}: {v} ({dirs_p.get(k,0)}%)" for k,v in dirs_c.items()]
            f.write(f"- Направления: {', '.join(parts)}\n")
        if langs:
            parts = [f"{k}: {v}" for k,v in langs.items()]
            f.write(f"- Языки описаний: {', '.join(parts)}\n")
        f.write("\n")

        # === 2) Top Tools ===
        f.write("## 2) Топ Tools (инструменты)\n")
        tools_items = list(tools.items())
        tools_items.sort(key=lambda x: x[1], reverse=True)
        for s, c in tools_items[:30]:
            f.write(f"- {s}: {c}\n")
        f.write("\n")

        # === 3) Top Hard Skills ===
        f.write("## 3) Топ Hard Skills (навыки)\n")
        skills_items = list(skills.items())
        skills_items.sort(key=lambda x: x[1], reverse=True)
        for s, c in skills_items[:30]:
            f.write(f"- {s}: {c}\n")
        f.write("\n")

        # === 4) Clusters ===
        f.write("## 4) Кластеры названий (Top-20)\n")
        for t, c in titles[:20]:
            f.write(f"- {t}: {c}\n")
        f.write("\n")

        # === 5) Tools/Skills Clusters ===
        f.write("## 5) Tools / Skills по направлениям\n")

        order = ["marketplaces", "online_marketing", "online_sales"]
        pretty = {
            "marketplaces": "Marketplaces",
            "online_marketing": "Online Marketing",
            "online_sales": "Online Sales",
            "mixed": "Mixed",
            "unclear": "Unclear"
        }

        # 5.1 Tools by direction
        if tools_by_dir:
            f.write("### 5.1 Tools по направлениям (топ-10 + %)\n")
            for d in order:
                if d in tools_by_dir and tools_by_dir[d]:
                    f.write(f"#### {pretty.get(d, d)}\n")
                    for term, count, perc in tools_by_dir[d]:
                        f.write(f"- {term}: {count} ({perc}%)\n")
                    f.write("\n")

        # 5.2 Skills by direction
        if skills_by_dir:
            f.write("### 5.2 Hard Skills по направлениям (топ-10 + %)\n")
            for d in order:
                if d in skills_by_dir and skills_by_dir[d]:
                    f.write(f"#### {pretty.get(d, d)}\n")
                    for term, count, perc in skills_by_dir[d]:
                        f.write(f"- {term}: {count} ({perc}%)\n")
                    f.write("\n")

        # === 6) Clusters (e-commerce, Top-20) ===
        if titles_ecom:
            f.write("## 4b) Кластеры названий (только e-commerce-релевантные, Top-20)\n")
            for t, c in titles_ecom[:20]:
                f.write(f"- {t}: {c}\n")
            f.write("\n")

        # (option) 
        if top_titles_by_dir_ecom:
            f.write("### 4c) Топ названий по направлениям (только e-commerce-релевантные)\n")
            order = ["marketplaces", "online_marketing", "online_sales", "mixed", "unclear"]
            pretty = {
                "marketplaces": "Marketplaces",
                "online_marketing": "Online Marketing",
                "online_sales": "Online Sales",
                "mixed": "Mixed",
                "unclear": "Unclear"
            }
            for d in order:
                if d in top_titles_by_dir_ecom and top_titles_by_dir_ecom[d]:
                    f.write(f"#### {pretty.get(d, d)}\n")
                    for t, c in top_titles_by_dir_ecom[d]:
                        f.write(f"- {t}: {c}\n")
                    f.write("\n")

        # img e-commerce
        img_ecom = os.path.join(OUTPUT_DIR, "titles_ecom_top20.png")
        if os.path.exists(img_ecom):
            f.write("![titles_ecom_top20](./titles_ecom_top20.png)\n\n")
            
        # === img Clusters ===
        imgs_ecom_dirs = [
            ("titles_ecom_marketplaces.png", "Marketplaces"),
            ("titles_ecom_online_marketing.png", "Online Marketing"),
            ("titles_ecom_online_sales.png", "Online Sales")
        ]

        for img_name, label in imgs_ecom_dirs:
            path_img = os.path.join(OUTPUT_DIR, img_name)
            if os.path.exists(path_img):
                f.write(f"### {label}\n")
                f.write(f"![{label}](./{img_name})\n\n")

        # === 7) Vizualize ===
        for img in ["skills_top15.png", "titles_top10.png", "languages_pie.png"]:
            path = os.path.join(OUTPUT_DIR, img)
            if os.path.exists(path):
                f.write(f"![{img}](./{img})\n")
                
# === QUALITY CHECK: (with) ===
import os, json
from urllib.parse import urlparse

summary_path = os.path.join(OUTPUT_DIR, "strict_filter_summary.json")
if os.path.exists(summary_path):
    with open(summary_path, encoding="utf-8") as f_sum:
        summary = json.load(f_sum)

    # --- Metrics ---
    total   = summary.get("total_vacancies", 0)
    none    = summary.get("without_signals", 0)
    pct_none = summary.get("percent_without_signals", 0)
    strong  = summary.get("with_strong_signals", 0)
    weak    = summary.get("with_only_weak_signals", 0)
    examples = summary.get("examples_without_signals", [])
    by_dir   = summary.get("by_direction", {})

    # --- Url ---
    def _short_url(u: str) -> str:
        """Сокращённый вид ссылки для текста (без query)."""
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

    def _ensure_scheme(u: str) -> str:
        """Возвращает полный URL с https://, если его нет."""
        if not u:
            return ""
        if u.startswith("http://") or u.startswith("https://"):
            return u
        return "https://" + u.lstrip("/")

    # --- name Clusters ---
    directions_order = ["marketplaces", "online_marketing", "online_sales", "mixed", "unclear"]
    pretty = {
        "marketplaces": "Marketplaces",
        "online_marketing": "Online Marketing",
        "online_sales": "Online Sales",
        "mixed": "Mixed",
        "unclear": "Unclear"
    }

    # --- with ---
    with open(os.path.join(OUTPUT_DIR, "final_report_marp.md"), "a", encoding="utf-8") as f:
        # title
        f.write(
            "\n\n---\n"
            "<!-- class: small-text -->\n"
            "## Проверка качества — Strict Filter Validation\n\n"
            f"**Всего вакансий:** {total}  •  **Сильные сигналы:** {strong}  •  "
            f"**Слабые:** {weak}  •  **Без сигналов:** {none} → **{pct_none:.2f}%**\n\n"
        )

        # pie chart
        quality_img = os.path.join(OUTPUT_DIR, "quality_split_pie.png")
        if os.path.exists(quality_img):
            f.write("![width:220px](./quality_split_pie.png)\n\n")

        
        f.write(
            "<small>Проверка по полной выгрузке (2176). Основной анализ выполнен на очищенной и "
            "дедуплицированной выборке (1930). **16.9%** нерелевантных записей относятся к исходным данным.</small>\n\n"
        )

        
        if examples:
          f.write("<small>**Примеры без e-commerce сигналов:**</small>\n")
          for ex in examples[:3]:
            t, c, u = (ex.get("title","").strip(), ex.get("company","").strip(), ex.get("url","").strip())
            f.write(f"- <small>{t} — {c} · [{_short_url(u)}]({_ensure_scheme(u)})</small>\n")
        f.write(f"\n<small>{none} ({pct_none:.2f}%) вакансий не содержат e-commerce терминов в названии или описании.</small>\n\n")


        
        f.write("\n\n### Доля объявлений без сигналов по направлениям\n\n")
        for d in directions_order:
            st = by_dir.get(d, {})
            tot = st.get("total", 0) or 0
            none_dir = st.get("none", 0) or 0
            pct_dir = (none_dir * 100.0 / tot) if tot else 0.0
            f.write(f"- **{pretty[d]}:** {none_dir}/{tot} → **{pct_dir:.2f}%** без сигналов\n")

        f.write("\n<small>Показатели рассчитаны по словарям/фильтрам сигналов, специфичным для каждого направления.</small>\n")

    print(f"Раздел 'Проверка качества' добавлен в final_report_marp.md ({pct_none:.2f}% без сигналов)")
