# 🧠 Python Projects — Data Analytics & Applications

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