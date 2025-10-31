#  💡 Python Projects — Data Analytics & Applications

This section contains two independent Python-based projects:  
1. **App_Sakila_Python** — a console application for querying the Sakila MySQL database.  
2. **CRM_Data_Analysis_Python** — a data analysis project focused on CRM optimization.

---

## 📂 Project 1: App_Sakila_Python

### 🎯 Goal
A console application designed for interactive movie search in the **Sakila MySQL** database.  
Includes integrated **SQLite logging** of all search queries.

### ⚙️ Structure
| File | Description |
|------|--------------|
| `config.py` | contains MySQL connection parameters, keeping credentials separate from the main code |
| `db_mysql.py` | executes SQL queries: search by keyword, genre, and release year |
| `db_sqlite.py` | logs all user search queries into a local SQLite database |
| `display.py` | manages formatted console output and menu rendering |
| `main.py` | contains the core application logic and command-line interface |
| `search_log.db` | local SQLite database for logging queries |

### 🧰 Stack
- Python 3.x  
- MySQL Connector  
- SQLite  
- PrettyTable (for console formatting)

---

## 📂 Project 2: CRM_Data_Analysis_Python

### 🎯 Goal
Analysis of CRM data from an online programming school to identify growth opportunities and improve key metrics such as CPA, ROI, and Retention.

### ⚙️ Structure
CRM_Data_Analysis_Python/
├── dashboard/ # visualization exports (PNG, HTML)
├── data/ # raw data
├── data_cleaned/ # processed datasets
├── reports/ # analytics reports
├── scripts/ # ETL & analysis scripts
│ └── main.py
└── README.md

---

## 📂 Project 3: E_Commerce_Jobs_Analysis (Germany, LinkedIn)

**Task**  
1) Analyze e-commerce specialist job vacancies in Germany over the last 3–6 months.  
2) Three directions: **marketplaces**, **online sales**, **online marketing**.  
3) Extract **hard skills**, **language(s)** (DE/EN/both), **soft skills** (minimal).  
4) Build **clusters of job titles** (frequencies, shares, formulations).

**Data**  
LinkedIn scraper collected job titles and descriptions (JSON files located in `./data`).  
Note: see the list of files in the task description.

**Approach (MVP priority)**  
- First — reliable cleaning: period filtering, deduplication, sanity-check.  
- Then — counting hard skills using a dictionary (`./skills/*.json`).  
- Reports and charts in `./outputs`.

## Structure

E_cd D:\ProjectsHub\Python
git add .gitignore requirements.txt README.md
git commit -m "Finalize unified Python project structure and configs"
git push
Commerce_Jobs_Analysis/
├─ data/                          # raw JSON (LinkedIn dumps)
├─ outputs/                       # results: cleaned data, charts, report.md
├─ scripts/
│  ├─ analyze_clusters.py         # job title clusters (and filtering irrelevant ones)
│  ├─ analyze_skills_by_direction.py
│  ├─ check_period.py
│  ├─ deduplicate.py
│  ├─ export_csv.py
│  ├─ extract_skills.py
│  ├─ generate_report.py
│  ├─ language_analysis.py
│  ├─ load_and_inspect.py
│  └─ utils.py                    # paths, loading, dedup, language, directions
├─ skills/
│  ├─ skills_dict.json            # hard skills (categorized dictionary)
│  ├─ skills.json                 # list of hard skills for search
│  └─ tools.json                  # tools/platforms for search
├─ .gitignore
├─ requirements.txt
└─ README.md

---

## 📂 Projects Overview

| Project | Description | Folder |
|----------|--------------|--------|
| 🎬 App_Sakila_Python | Console app for MySQL Sakila DB querying and logging | [`App_Sakila_Python`](./App_Sakila_Python) |
| 📊 CRM_Data_Analysis_Python | CRM optimization & data analysis dashboard | [`CRM_Data_Analysis_Python`](./CRM_Data_Analysis_Python) |
| 🛒 E_Commerce_Jobs_Analysis | Analysis of LinkedIn e-commerce job postings in Germany | [`E_Commerce_Jobs_Analysis`](./E_Commerce_Jobs_Analysis) |
