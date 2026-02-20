# AI Business Automation Specialist

## Project Structure

AI BUSINESS AUTOMATION SPECIALIST/

├── .vscode/
│   └── settings.json                  # VS Code environment settings
│
└── bit_ai_business_automation_market/
    ├── pyproject.toml                 # Python project metadata
    ├── requirements.txt               # Project dependencies
    ├── README.md                      # Local project documentation
    │
    ├── data/
    │   ├── database/
    │   │   └── bit_ai.db              # SQLite database
    │   │
    │   ├── processed/
    │   │   ├── catalog_official_berufe.csv
    │   │   ├── catalog_official_berufe_scored.csv
    │   │   ├── job_ads_labeled.parquet
    │   │   └── profiles_labeled.parquet
    │   │
    │   ├── raw/
    │   │   └── catalogs/
    │   │       ├── at_berufe_manual.csv
    │   │       ├── ch_berufe_manual.csv
    │   │       └── de_berufe_manual.csv
    │   │
    │   └── reference/
    │       ├── official_berufe_bit_mapping.csv
    │       ├── official_resources_list_de_at_ch.json
    │       ├── role_profile_ai_business_automation.json
    │       └── title_dictionary_de_at_ch.csv
    │
    ├── docs/
    ├── notebooks/
    ├── src/
    └── tools/

## Setup

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

Core Modules

src/config.py – project paths and configuration

src/classification/role_matcher.py – embeddings & cosine similarity

src/reporting/report_official_berufe_similarity.py – main analysis pipeline