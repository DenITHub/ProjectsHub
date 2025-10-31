from collections import Counter
from utils import (
    OUTPUT_DIR,
    SKILLS_DIR,
    read_json_file,
    write_json,
    categorize_direction
)

def count_terms_by_direction(data, terms):
    # Возвращает Counter по направлениям
    dir_terms = {
        "marketplaces": Counter(),
        "online_sales": Counter(),
        "online_marketing": Counter(),
        "mixed": Counter(),
        "unclear": Counter()
    }
    for job in data:
        d = categorize_direction(job)
        text = f"{job.get('title','')} {job.get('description','')}".lower()
        for t in terms:
            if t.lower() in text:
                dir_terms[d][t] += 1
    return dir_terms

def top10_with_percent(counter):
    total = sum(counter.values()) or 1
    items = counter.most_common(10)
    return [(s, c, round(c*100/total, 1)) for s, c in items]

if __name__ == "__main__":
    data = read_json_file(f"{OUTPUT_DIR}/clean_data.json")

    tools_list  = read_json_file(f"{SKILLS_DIR}/tools.json")
    skills_list = read_json_file(f"{SKILLS_DIR}/skills.json")

    tools_by_dir  = count_terms_by_direction(data, tools_list)
    skills_by_dir = count_terms_by_direction(data, skills_list)

    tools_top = { d: top10_with_percent(cnt) for d, cnt in tools_by_dir.items() if cnt }
    skills_top = { d: top10_with_percent(cnt) for d, cnt in skills_by_dir.items() if cnt }

    write_json(f"{OUTPUT_DIR}/tools_by_direction.json", tools_top)
    write_json(f"{OUTPUT_DIR}/skills_by_direction.json", skills_top)

    print("\n=== TOOLS by direction (top-10) ===")
    for d, items in tools_top.items():
        print(f"\n{d.upper()}")
        for s, c, p in items:
            print(f"{s}: {c} ({p}%)")

    print("\n=== SKILLS by direction (top-10) ===")
    for d, items in skills_top.items():
        print(f"\n{d.upper()}")
        for s, c, p in items:
            print(f"{s}: {c} ({p}%)")

    print("\nФайлы сохранены:",
          "outputs/tools_by_direction.json, outputs/skills_by_direction.json")


