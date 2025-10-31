from collections import Counter
from utils import read_json_file, write_json, OUTPUT_DIR, detect_lang

if __name__ == "__main__":
    data = read_json_file(f"{OUTPUT_DIR}/clean_data.json")

    langs_per_job = []
    counts = Counter()
    for job in data:
        txt = f"{job.get('title','')}\n{job.get('description','')}"
        lang = detect_lang(txt)
        counts[lang] += 1
        langs_per_job.append({
            "title": job.get("title"),
            "company": job.get("companyName"),
            "jobUrl": job.get("jobUrl"),
            "lang": lang
        })

    write_json(f"{OUTPUT_DIR}/language_per_job.json", langs_per_job)
    write_json(f"{OUTPUT_DIR}/language_stats.json", dict(counts))

    print("Языковая статистика:", dict(counts))
