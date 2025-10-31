import csv, json, os
from utils import OUTPUT_DIR

def dump_dict_csv(d, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["key","count"])
        for k, v in d.items():
            w.writerow([k, v])

if __name__ == "__main__":
    skills = json.load(open(f"{OUTPUT_DIR}/skills_count.json", encoding="utf-8"))
    titles = json.load(open(f"{OUTPUT_DIR}/title_clusters.json", encoding="utf-8"))

    dump_dict_csv(skills, f"{OUTPUT_DIR}/skills_count.csv")
    with open(f"{OUTPUT_DIR}/title_clusters.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["title","count"])
        for t, c in titles:
            w.writerow([t, c])
    print("CSV сохранены в outputs/")
