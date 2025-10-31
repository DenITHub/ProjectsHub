from datetime import datetime
from utils import read_json_file, OUTPUT_DIR

if __name__ == "__main__":
    data = read_json_file(f"{OUTPUT_DIR}/clean_data.json")

    dates = []
    for job in data:
        date_str = job.get("publishedAt") or job.get("date")
        if date_str:
            try:
                dates.append(datetime.strptime(date_str[:10], "%Y-%m-%d"))
            except Exception:
                pass

    if dates:
        print(f"🔹 Всего вакансий с датой: {len(dates)}")
        print(f"📅 Период выборки: {min(dates).date()} → {max(dates).date()}")
    else:
        print("⚠️ Даты не найдены в данных.")
