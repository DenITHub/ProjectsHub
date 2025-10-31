#from collections import Counter, defaultdict
#from utils import read_json_file, write_json, OUTPUT_DIR, categorize_direction, to_percent

#if __name__ == "__main__":
#    data = read_json_file(f"{OUTPUT_DIR}/clean_data.json")

#    # Частоты названий
#    title_counts = Counter([(item.get("title") or "").strip() for item in data if item.get("title")])
#    write_json(f"{OUTPUT_DIR}/title_clusters.json", title_counts.most_common())

#    # Направления
#    dir_counts = Counter([categorize_direction(job) for job in data])
#    write_json(f"{OUTPUT_DIR}/direction_counts.json", dict(dir_counts))
#    write_json(f"{OUTPUT_DIR}/direction_shares.json", to_percent(dict(dir_counts)))

#    # Топ названий по направлениям
#    by_dir = defaultdict(Counter)
#    for job in data:
#        d = categorize_direction(job)
#        title = (job.get("title") or "").strip()
#        if title:
#            by_dir[d][title] += 1
#    top_by_dir = {d: cnt.most_common(10) for d, cnt in by_dir.items()}
#    write_json(f"{OUTPUT_DIR}/title_clusters_by_direction.json", top_by_dir)

#    print(f"Всего уникальных названий: {len(title_counts)}")
#    print("Распределение по направлениям:", dict(dir_counts))


#from utils import read_json_file, write_json, OUTPUT_DIR, categorize_direction, to_percent, strip_gender_suffix_display
#from collections import Counter, defaultdict

#if __name__ == "__main__":
#    data = read_json_file(f"{OUTPUT_DIR}/clean_data.json")

#    # Считаем кластеры по ОЧИЩЕННОМУ заголовку (для вывода)
#    titles_clean = [
#        strip_gender_suffix_display(item.get("title"))
#        for item in data
#        if item.get("title")
#    ]
#    title_counts = Counter([t for t in titles_clean if t])
#    write_json(f"{OUTPUT_DIR}/title_clusters.json", title_counts.most_common())

#    # Направления — без изменений
#    dir_counts = Counter([categorize_direction(job) for job in data])
#    write_json(f"{OUTPUT_DIR}/direction_counts.json", dict(dir_counts))
#    write_json(f"{OUTPUT_DIR}/direction_shares.json", to_percent(dict(dir_counts)))

#    # Топ названий по направлениям — тоже используем очищенный тайтл
#    by_dir = defaultdict(Counter)
#    for job in data:
#        d = categorize_direction(job)
#        title_disp = strip_gender_suffix_display(job.get("title"))
#        if title_disp:
#            by_dir[d][title_disp] += 1
#    top_by_dir = {d: cnt.most_common(10) for d, cnt in by_dir.items()}
#    write_json(f"{OUTPUT_DIR}/title_clusters_by_direction.json", top_by_dir)

#    print(f"Всего уникальных названий: {len(title_counts)}")
#    print("Распределение по направлениям:", dict(dir_counts))

from collections import Counter, defaultdict
from utils import (
    read_json_file, write_json, OUTPUT_DIR,
    categorize_direction, to_percent, strip_gender_suffix_display,
    ECOM_TITLE_KEYWORDS
)

def is_ecom_relevant_title(title: str) -> bool:
    """Явная релевантность e-commerce именно по TITLE (без описания)."""
    if not title:
        return False
    t = title.lower()
    return any(k in t for k in ECOM_TITLE_KEYWORDS)

if __name__ == "__main__":
    data = read_json_file(f"{OUTPUT_DIR}/clean_data.json")

    # 1) Кластеры по всем названиям (для совместимости со старым отчётом)
    titles_all = [strip_gender_suffix_display(item.get("title")) for item in data if item.get("title")]
    title_counts_all = Counter([t for t in titles_all if t])

    write_json(f"{OUTPUT_DIR}/title_clusters.json", title_counts_all.most_common())

    # 2) Кластеры по e-commerce-релевантным TИTLE
    titles_ecom = [t for t in titles_all if t and is_ecom_relevant_title(t)]
    title_counts_ecom = Counter(titles_ecom)

    write_json(f"{OUTPUT_DIR}/title_clusters_ecom.json", title_counts_ecom.most_common())

    # 3) Направления — без изменений
    dir_counts = Counter([categorize_direction(job) for job in data])
    write_json(f"{OUTPUT_DIR}/direction_counts.json", dict(dir_counts))
    write_json(f"{OUTPUT_DIR}/direction_shares.json", to_percent(dict(dir_counts)))

    # 4) Топ названий по направлениям (ALL и ECOM) — используем очищенный title
    by_dir_all = defaultdict(Counter)
    by_dir_ecom = defaultdict(Counter)

    for job in data:
        d = categorize_direction(job)
        title_disp = strip_gender_suffix_display(job.get("title"))
        if not title_disp:
            continue
        by_dir_all[d][title_disp] += 1
        if is_ecom_relevant_title(title_disp):
            by_dir_ecom[d][title_disp] += 1

    top_by_dir_all = {d: cnt.most_common(10) for d, cnt in by_dir_all.items()}
    top_by_dir_ecom = {d: cnt.most_common(10) for d, cnt in by_dir_ecom.items()}

    write_json(f"{OUTPUT_DIR}/title_clusters_by_direction.json", top_by_dir_all)
    write_json(f"{OUTPUT_DIR}/title_clusters_by_direction_ecom.json", top_by_dir_ecom)

    print(f"Всего уникальных названий (ALL): {len(title_counts_all)}")
    print(f"Уникальных e-commerce названий (ECOM): {len(title_counts_ecom)}")
    print("Распределение по направлениям:", dict(dir_counts))
