import re
from collections import defaultdict
from utils import read_json_file, write_json, OUTPUT_DIR, SKILLS_DIR

def compile_patterns(terms):
    patterns = {}
    for t in terms:
        # точный поиск по словам/фразам (без ложных частичных совпадений)
        patterns[t] = re.compile(rf"\b{re.escape(t.lower())}\b")
    return patterns

if __name__ == "__main__":
    data = read_json_file(f"{OUTPUT_DIR}/clean_data.json")

    # Загружаем отдельно инструменты и навыки
    tools_list = read_json_file(f"{SKILLS_DIR}/tools.json")
    skills_list = read_json_file(f"{SKILLS_DIR}/skills.json")

    tools_re = compile_patterns(tools_list)
    skills_re = compile_patterns(skills_list)

    tools_counter = defaultdict(int)
    skills_counter = defaultdict(int)

    job_tools = []
    job_skills = []

    for job in data:
        text = f"{job.get('title','')}\n{job.get('description','')}".lower()

        found_tools = []
        for tool, pat in tools_re.items():
            if pat.search(text):
                tools_counter[tool] += 1
                found_tools.append(tool)

        found_skills = []
        for skill, pat in skills_re.items():
            if pat.search(text):
                skills_counter[skill] += 1
                found_skills.append(skill)

        job_tools.append({
            "title": job.get("title"),
            "company": job.get("companyName"),
            "jobUrl": job.get("jobUrl"),
            "tools": sorted(found_tools)
        })
        job_skills.append({
            "title": job.get("title"),
            "company": job.get("companyName"),
            "jobUrl": job.get("jobUrl"),
            "skills": sorted(found_skills)
        })

    # сохраняем отдельно
    write_json(f"{OUTPUT_DIR}/tools_count.json",
               dict(sorted(tools_counter.items(), key=lambda x: (-x[1], x[0]))))
    write_json(f"{OUTPUT_DIR}/skills_count.json",
               dict(sorted(skills_counter.items(), key=lambda x: (-x[1], x[0]))))
    write_json(f"{OUTPUT_DIR}/job_tools.json", job_tools)
    write_json(f"{OUTPUT_DIR}/job_skills.json", job_skills)

    print(f"Вакансий обработано: {len(data)}")
    print(f"Инструменты (уникальные с упоминаниями): {len([k for k,v in tools_counter.items() if v>0])}")
    print(f"Навыки (уникальные с упоминаниями): {len([k for k,v in skills_counter.items() if v>0])}")
