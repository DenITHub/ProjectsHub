#import os
#import json
#import matplotlib.pyplot as plt
#from utils import OUTPUT_DIR

#def load(path, default=None):
#    try:
#        with open(path, encoding="utf-8") as f:
#            return json.load(f)
#    except Exception:
#        return default

#if __name__ == "__main__":
#    # Skills
#    skills = load(f"{OUTPUT_DIR}/skills_count.json", {})
#    items = list(skills.items())
#    items.sort(key=lambda x: x[1], reverse=True)
#    top = items[:15] if items else []
#    if top:
#        labels, values = zip(*top)
#        plt.figure(figsize=(12, 6))
#        plt.barh(list(labels)[::-1], list(values)[::-1])
#        plt.title("Top 15 Hard Skills in E-Commerce Vacancies (DE)")
#        plt.tight_layout()
#        plt.savefig(f"{OUTPUT_DIR}/skills_top15.png")
#        plt.close()

#    # Titles
#    titles = load(f"{OUTPUT_DIR}/title_clusters.json", [])
#    top_t = titles[:10] if titles else []
#    if top_t:
#        labels_t = [t[0] for t in top_t]
#        values_t = [t[1] for t in top_t]
#        plt.figure(figsize=(12, 6))
#        plt.barh(list(labels_t)[::-1], list(values_t)[::-1])
#        plt.title("Top 10 Job Titles")
#        plt.tight_layout()
#        plt.savefig(f"{OUTPUT_DIR}/titles_top10.png")
#        plt.close()

#    # Languages
#    lang_stats = load(f"{OUTPUT_DIR}/language_stats.json", {})
#    if lang_stats:
#        labels_l = list(lang_stats.keys())
#        values_l = list(lang_stats.values())
#        plt.figure(figsize=(6, 6))
#        plt.pie(values_l, labels=labels_l, autopct="%1.1f%%")
#        plt.title("Distribution of Vacancy Description Languages")
#        plt.tight_layout()
#        plt.savefig(f"{OUTPUT_DIR}/languages_pie.png")
#        plt.close()

#    print("Графики сохранены в outputs/")

#    # === Бар-чарты по направлениям ===
#    skills_by_dir_path = f"{OUTPUT_DIR}/skills_by_direction.json"
#    if os.path.exists(skills_by_dir_path):
#        with open(skills_by_dir_path, encoding="utf-8") as f:
#            skills_by_dir = json.load(f)
#        for d in ["marketplaces", "online_sales", "online_marketing"]:
#            if d in skills_by_dir and skills_by_dir[d]:
#                items = skills_by_dir[d]
#                labels = [s for s, _, _ in items]
#                values = [v for _, v, _ in items]
#                plt.figure(figsize=(10, 5))
#                plt.barh(labels[::-1], values[::-1])
#                plt.title(f"Top Hard Skills – {d.replace('_', ' ').title()}")
#                plt.tight_layout()
#                plt.savefig(f"{OUTPUT_DIR}/skills_{d}.png")
#                plt.close()

#    # === Топ-15 Tools (инструменты) ===
#    tools_path = f"{OUTPUT_DIR}/tools_count.json"
#    if os.path.exists(tools_path):
#        with open(tools_path, encoding="utf-8") as f:
#            tools_count = json.load(f)
#        items = list(tools_count.items())
#        items.sort(key=lambda x: x[1], reverse=True)
#        top = items[:15] if items else []
#        if top:
#            labels, values = zip(*top)
#            plt.figure(figsize=(12, 6))
#            plt.barh(list(labels)[::-1], list(values)[::-1])
#            plt.title("Top 15 Tools (E-Commerce Vacancies)")
#            plt.tight_layout()
#            plt.savefig(f"{OUTPUT_DIR}/tools_top15.png")
#            plt.close()

#    # === Бар-чарты по направлениям для TOOLS и SKILLS ===
#    def plot_dir_bars(json_name, prefix):
#        path = f"{OUTPUT_DIR}/{json_name}"
#        if not os.path.exists(path):
#            return
#        with open(path, encoding="utf-8") as f:
#            data = json.load(f)
#        for d in ["marketplaces", "online_sales", "online_marketing"]:
#            if d in data and data[d]:
#                items = data[d]
#                labels = [s for s, _, _ in items]
#                values = [v for _, v, _ in items]
#                plt.figure(figsize=(10, 5))
#                plt.barh(labels[::-1], values[::-1])
#                plt.title(f"Top {prefix} – {d.replace('_',' ').title()}")
#                plt.tight_layout()
#                plt.savefig(f"{OUTPUT_DIR}/{prefix.lower()}_{d}.png")
#                plt.close()

#    plot_dir_bars("tools_by_direction.json", "Tools")
#    plot_dir_bars("skills_by_direction.json", "Skills")

#    # === Top-20 e-commerce-релевантных названий вакансий ===
#    titles_ecom_path = f"{OUTPUT_DIR}/title_clusters_ecom.json"
#    if os.path.exists(titles_ecom_path):
#        with open(titles_ecom_path, encoding="utf-8") as f:
#            titles_ecom = json.load(f)  # список пар [title, count]
#        top_e = titles_ecom[:20] if titles_ecom else []
#        if top_e:
#            labels_e = [t[0] for t in top_e]
#            values_e = [t[1] for t in top_e]
#            plt.figure(figsize=(12, 7))
#            plt.barh(labels_e[::-1], values_e[::-1])
#            plt.title("Top 20 Titles (E-Commerce-Relevant Only)")
#            plt.tight_layout()
#            plt.savefig(f"{OUTPUT_DIR}/titles_ecom_top20.png")
#            plt.close()

#    # === (Опционально) Топ-10 e-commerce-релевантных названий по направлениям ===
#    titles_ecom_by_dir_path = f"{OUTPUT_DIR}/title_clusters_by_direction_ecom.json"
#    if os.path.exists(titles_ecom_by_dir_path):
#        with open(titles_ecom_by_dir_path, encoding="utf-8") as f:
#            titles_ecom_by_dir = json.load(f)  # {dir: [[title, count], ...]}
#        for d in ["marketplaces", "online_marketing", "online_sales"]:
#            if d in titles_ecom_by_dir and titles_ecom_by_dir[d]:
#                items = titles_ecom_by_dir[d][:10]
#                labels_d = [t[0] for t in items]
#                values_d = [t[1] for t in items]
#                plt.figure(figsize=(10, 5))
#                plt.barh(labels_d[::-1], values_d[::-1])
#                plt.title(f"Top E-Commerce Job Titles – {d.replace('_',' ').title()}")
#                plt.tight_layout()
#                plt.savefig(f"{OUTPUT_DIR}/titles_ecom_{d}.png")
#                plt.close()


#    # === (Опционально) Топ-10 e-commerce-релевантных названий по направлениям ===
#    titles_ecom_by_dir_path = f"{OUTPUT_DIR}/title_clusters_by_direction_ecom.json"
#    if os.path.exists(titles_ecom_by_dir_path):
#        with open(titles_ecom_by_dir_path, encoding="utf-8") as f:
#            titles_ecom_by_dir = json.load(f)  # {direction: [[title, count], ...]}
        
#        # Определим порядок и подписи направлений
#        directions_order = ["marketplaces", "online_marketing", "online_sales"]
#        pretty_names = {
#            "marketplaces": "Marketplaces",
#            "online_marketing": "Online Marketing",
#            "online_sales": "Online Sales"
#        }

#        #for d in directions_order:
#        #    if d in titles_ecom_by_dir and titles_ecom_by_dir[d]:
#        #        items = titles_ecom_by_dir[d][:10]
#        #        labels_d = [t[0] for t in items]
#        #        values_d = [t[1] for t in items]

#        #        plt.figure(figsize=(10, 5))
#        #        plt.barh(labels_d[::-1], values_d[::-1])
#        #        plt.title(f"Top E-Commerce Job Titles – {pretty_names[d]}", loc="left", x=0.0)
#        #        plt.savefig(f"{OUTPUT_DIR}/titles_ecom_{d}.png")
#        #        plt.close()


#for d in directions_order:
#    if d in titles_ecom_by_dir and titles_ecom_by_dir[d]:
#        items = titles_ecom_by_dir[d][:10]
#        labels_d = [t[0] for t in items]
#        values_d = [t[1] for t in items]

#        # ВАЖНО: работаем через fig, ax — это не сдвинет оси/ярлыки
#        fig, ax = plt.subplots(figsize=(10, 5))
#        ax.barh(labels_d[::-1], values_d[::-1])

#        # смещаем только заголовок влево, без bold
#        ax.set_title(
#            f"Top E-Commerce Job Titles – {pretty_names[d]}",
#            loc="left",          # выравнивание слева
#            pad=12,              # небольшой отступ сверху
#            fontweight="normal"  # точно не жирный
#            # можно добавить y=1.02, если хочется чуть выше
#        )

#        # оставляем немного места под title, чтобы tight_layout не «перецентровал» его
#        fig.tight_layout(rect=[0, 0, 1, 0.95])

#        fig.savefig(f"{OUTPUT_DIR}/titles_ecom_{d}.png")
#        plt.close(fig)

# scripts/visualize.py  — ЧИСТАЯ ВЕРСИЯ
import os
import json
import matplotlib.pyplot as plt
from utils import OUTPUT_DIR

def load(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

if __name__ == "__main__":
    # === Top-15 Hard Skills ===
    skills = load(f"{OUTPUT_DIR}/skills_count.json", {})
    items = sorted(list(skills.items()), key=lambda x: x[1], reverse=True)[:15]
    if items:
        labels, values = zip(*items)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.barh(list(labels)[::-1], list(values)[::-1])
        ax.set_title("Top 15 Hard Skills in E-Commerce Vacancies (DE)", loc="left", pad=12, fontweight="normal")
        fig.tight_layout(rect=[0, 0, 1, 0.95])
        fig.savefig(f"{OUTPUT_DIR}/skills_top15.png")
        plt.close(fig)

    # === Top-10 Job Titles (all) ===
    titles_all = load(f"{OUTPUT_DIR}/title_clusters.json", [])
    top_t = titles_all[:10] if titles_all else []
    if top_t:
        labels_t = [t[0] for t in top_t]
        values_t = [t[1] for t in top_t]
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.barh(list(labels_t)[::-1], list(values_t)[::-1])
        ax.set_title("Top 10 Job Titles", loc="left", pad=12, fontweight="normal")
        fig.tight_layout(rect=[0, 0, 1, 0.95])
        fig.savefig(f"{OUTPUT_DIR}/titles_top10.png")
        plt.close(fig)

    # === Languages pie ===
    lang_stats = load(f"{OUTPUT_DIR}/language_stats.json", {})
    if lang_stats:
        labels_l = list(lang_stats.keys())
        values_l = list(lang_stats.values())
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(values_l, labels=labels_l, autopct="%1.1f%%")
        ax.set_title("Distribution of Vacancy Description Languages", loc="left", pad=12, fontweight="normal")
        fig.tight_layout(rect=[0, 0, 1, 0.95])
        fig.savefig(f"{OUTPUT_DIR}/languages_pie.png")
        plt.close(fig)

    # === Skills by direction ===
    skills_by_dir = load(f"{OUTPUT_DIR}/skills_by_direction.json", {})
    for d in ["marketplaces", "online_sales", "online_marketing"]:
        if d in skills_by_dir and skills_by_dir[d]:
            items = skills_by_dir[d]
            labels = [s for s, _, _ in items]
            values = [v for _, v, _ in items]
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.barh(labels[::-1], values[::-1])
            ax.set_title(f"Top Hard Skills – {d.replace('_',' ').title()}",
                         loc="left", pad=12, fontweight="normal")
            fig.tight_layout(rect=[0, 0, 1, 0.95])
            fig.savefig(f"{OUTPUT_DIR}/skills_{d}.png")
            plt.close(fig)

    # === Top-15 Tools ===
    tools_count = load(f"{OUTPUT_DIR}/tools_count.json", {})
    items = sorted(list(tools_count.items()), key=lambda x: x[1], reverse=True)[:15]
    if items:
        labels, values = zip(*items)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.barh(list(labels)[::-1], list(values)[::-1])
        ax.set_title("Top 15 Tools (E-Commerce Vacancies)", loc="left", pad=12, fontweight="normal")
        fig.tight_layout(rect=[0, 0, 1, 0.95])
        fig.savefig(f"{OUTPUT_DIR}/tools_top15.png")
        plt.close(fig)

    # === Tools/Skills by direction helper ===
    def plot_dir_bars(json_name, prefix):
        data = load(f"{OUTPUT_DIR}/{json_name}", {})
        for d in ["marketplaces", "online_sales", "online_marketing"]:
            if d in data and data[d]:
                items = data[d]
                labels = [s for s, _, _ in items]
                values = [v for _, v, _ in items]
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.barh(labels[::-1], values[::-1])
                ax.set_title(f"Top {prefix} – {d.replace('_',' ').title()}",
                             loc="left", pad=12, fontweight="normal")
                fig.tight_layout(rect=[0, 0, 1, 0.95])
                fig.savefig(f"{OUTPUT_DIR}/{prefix.lower()}_{d}.png")
                plt.close(fig)

    plot_dir_bars("tools_by_direction.json", "Tools")
    plot_dir_bars("skills_by_direction.json", "Skills")

    # === Top-20 e-commerce-relevant titles (overall) ===
    titles_ecom = load(f"{OUTPUT_DIR}/title_clusters_ecom.json", [])
    top_e = titles_ecom[:20] if titles_ecom else []
    if top_e:
        labels_e = [t[0] for t in top_e]
        values_e = [t[1] for t in top_e]
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.barh(labels_e[::-1], values_e[::-1])
        ax.set_title("Top 20 Titles (E-Commerce-Relevant Only)", loc="left", pad=12, fontweight="normal")
        fig.tight_layout(rect=[0, 0, 1, 0.95])
        fig.savefig(f"{OUTPUT_DIR}/titles_ecom_top20.png")
        plt.close(fig)

    # === Top-10 e-commerce-relevant titles by direction (LEFT-aligned title) ===
    titles_ecom_by_dir = load(f"{OUTPUT_DIR}/title_clusters_by_direction_ecom.json", {})
    directions_order = ["marketplaces", "online_marketing", "online_sales"]
    pretty_names = {
        "marketplaces": "Marketplaces",
        "online_marketing": "Online Marketing",
        "online_sales": "Online Sales",
    }
    for d in directions_order:
        if d in titles_ecom_by_dir and titles_ecom_by_dir[d]:
            items = titles_ecom_by_dir[d][:10]
            labels_d = [t[0] for t in items]
            values_d = [t[1] for t in items]
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.barh(labels_d[::-1], values_d[::-1])
            ax.set_title(f"Top E-Commerce Job Titles – {pretty_names[d]}",
                         loc="left", pad=12, fontweight="normal")
            fig.tight_layout(rect=[0, 0, 1, 0.95])
            fig.savefig(f"{OUTPUT_DIR}/titles_ecom_{d}.png")
            plt.close(fig)
            
    # === Dataset Quality pie (relevant vs no signals) ===
summary = load(f"{OUTPUT_DIR}/strict_filter_summary.json", {})
if summary:
    strong = summary.get("with_strong_signals", 0)
    weak_only = summary.get("with_only_weak_signals", 0)
    none = summary.get("without_signals", 0)
    relevant = strong + weak_only

    labels_q = ["With e-commerce signals", "No signals"]
    values_q = [relevant, none]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(values_q, labels=labels_q, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    ax.set_title("Dataset Quality (Signals vs No Signals)", loc="left", pad=12, fontweight="normal")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(f"{OUTPUT_DIR}/quality_split_pie.png")
    plt.close(fig)


    print("Графики сохранены в outputs/")
