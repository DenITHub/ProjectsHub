from utils import load_all_json, filter_recent, deduplicate_records, write_json, OUTPUT_DIR

if __name__ == "__main__":
    raw = load_all_json()
    recent = filter_recent(raw, months=6)
    unique = deduplicate_records(recent)

    write_json(f"{OUTPUT_DIR}/clean_data.json", unique)
    print(f"Сырых записей: {len(raw)}")
    print(f"После фильтра по дате: {len(recent)}")
    print(f"Уникальных (после дедупликации): {len(unique)}")

