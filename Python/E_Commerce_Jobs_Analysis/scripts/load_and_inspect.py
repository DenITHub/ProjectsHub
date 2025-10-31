from pprint import pprint
from utils import list_data_files, load_all_json

if __name__ == "__main__":
    files = list_data_files()
    print(f"Файлов в data/: {len(files)}")
    for fn in files:
        print(" -", fn)

    data = load_all_json()
    print(f"\nВсего записей (сырых): {len(data)}")
    if data:
        print("\nПример записи:")
        pprint({k: data[0].get(k) for k in ["title","companyName","location","publishedAt","jobUrl"]})
