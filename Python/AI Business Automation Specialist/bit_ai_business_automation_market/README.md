Analysis Pipeline & Documentation
Pipeline: Full Step-by-Step Process

---

# 1. Role Formalization (Role Profile)

What we do:
Describe what an AI Business Automation Specialist is in a machine-readable format.

Where it is stored:
File: data/reference/role_profile_ai_business_automation.json

Typical fields:
- role_name
- summary
- core_tasks (list of key tasks and responsibilities)

How it is used:
The script report_official_berufe_similarity.py reads the JSON and uses
get_embedding(...) to convert the text into a vector role_vec (the role profile embedding).

If the JSON is missing or empty, the script uses a fallback text via _fallback_role_text().

---

# 2. Official Occupation Catalog (DE/AT/CH)

What we do:
Build a unified catalog of official occupations for three countries.

Source file:
data/processed/catalog_official_berufe.csv
(delimiter: ;)

Typical columns:
- country — country (DE, AT, CH)
- source — source (BERUFENET, AMS, BVZ, etc.)
- official_title — official occupation title
- kldb_code — KldB code (DE only, if available)
- notes — additional descriptions / context

Loading:
Function load_official_catalog() in report_official_berufe_similarity.py:
- trims whitespace
- normalizes string formats
- ensures a minimal required set of columns exists

---

# 3. Embeddings and Similarity (Core Analysis)

Main idea:
Compare the role profile embedding with embeddings of each official occupation title.

Where the logic lives:
src/classification/role_matcher.py
- get_embedding(text: str) -> np.ndarray — calls the OpenAI Embeddings API
- cosine_sim(a: np.ndarray, b: np.ndarray) -> float — cosine similarity

How it is used in the reporting script:
- load_role_profile_vector():
  reads the JSON role profile,
  creates an embedding,
  returns role_vec.
- compute_similarity(df: pd.DataFrame, role_vec: np.ndarray) -> pd.DataFrame:
  concatenates official_title + notes (if present),
  calls get_embedding(text) for each row,
  computes cosine similarity between role_vec and the occupation embedding,
  adds a similarity column to the dataframe.

Result:
DataFrame df_sim where each occupation has a numeric similarity score to the role.

---

# 4. Saving the “Scored” Catalog

Goal:
Persist similarity results into a separate CSV for downstream analysis and visualization.

File:
data/processed/catalog_official_berufe_scored.csv

Writer:
generate_similarity_report() in report_official_berufe_similarity.py:
df_sim.to_csv(CATALOG_SCORED_CSV, index=False)

---

# 5. Top-10 Visualizations by Country

Goal:
Show which occupations in each country are closest to the role.

Function:
plot_top10_by_country(df_sim, country, output_path)

What it does:
- filters df_sim by country
- takes top 10 by similarity
- plots a horizontal bar chart:
  X — similarity
  Y — occupation titles

Output files:
- docs/img/top10_official_berufe_de.png
- docs/img/top10_official_berufe_at.png
- docs/img/top10_official_berufe_ch.png

---

# 6. Global Top-10 (DACH Aggregate)

Goal:
Show which occupations overall (across DACH) match the role most strongly and most often.

Function:
plot_top10_global(df_sim, IMG_DIR / "top10_official_berufe_similarity.png")

Logic:
groupby("official_title")["similarity"].max()
— take the maximum similarity per title if it appears in multiple countries.

Sort by similarity, take top 10, plot a horizontal bar chart.

Output file:
docs/img/top10_official_berufe_similarity.png

---

# 7. Country Heatmap (DE/AT/CH)

Goal:
Provide an intuitive visualization across the three countries at once.

Function:
plot_heatmap(df_sim, IMG_DIR / "heatmap_official_berufe_de_at_ch.png")

How it works:
For each country (DE, AT, CH), take its top 10 occupations by similarity.
Build three independent vertical heatmap “strips”:

- DE → colormap Blues
- AT → Reds
- CH → Greens

In each strip:
- Y-axis — its own top-10 occupation list
- each cell — numeric value 0.xx

On the right: a shared colorbar labeled “Cosine Similarity”.

Output file:
docs/img/heatmap_official_berufe_de_at_ch.png

---

# 8. Mapping: Official Occupations → BIT Role Level (Optional Layer)

Goal:
Manual / semi-manual mapping of selected occupations to BIT role levels.

Reference file:
data/reference/official_berufe_bit_mapping.csv

Loading:
load_bit_mapping():
- string cleaning
- required columns validation (country, source, official_title, bit_role_level, bit_role_label, comment, ...)

Then:
In generate_similarity_report():
df_sim is merged with the mapping on (country, source, official_title).
Rows with bit_role_level filled are kept.
The result is rendered into a Markdown table.

---

# 9. Markdown Report Generation: 05_similarity_official_berufe.md

Core function:
generate_similarity_report() -> str

Step-by-step:
- load role profile → role_vec
- load official catalog → df
- compute similarity → df_sim
- save catalog_official_berufe_scored.csv

Build and save charts:
- top10_official_berufe_de.png
- top10_official_berufe_at.png
- top10_official_berufe_ch.png
- top10_official_berufe_similarity.png
- heatmap_official_berufe_de_at_ch.png

Write Markdown report docs/05_similarity_official_berufe.md:
- Top-10 tables by country
- heatmap link
- “Mapping: Official Occupations → BIT Role Level” table (if mapping exists)
- market titles block from docs/market_titles_mapping.md (if file exists)

Returns the report text as a string (can be used further for PDF/Marp generation).

---

# 10. Final Presentation Report: 06_final_report_BIT_ru.md (Marp)

Goal:
Create a presentation for product team / stakeholders.

File:
docs/06_final_report_BIT_ru.md (Marp format)

Data sources:
- narrative conclusions — written manually based on 05_similarity_official_berufe.md
- images — from docs/img/:
  - img/top10_official_berufe_de.png
  - img/top10_official_berufe_at.png
  - img/top10_official_berufe_ch.png
  - img/top10_official_berufe_similarity.png
  - img/heatmap_official_berufe_de_at_ch.png (optional slide)

Build PDF:
cd docs
marp 06_final_report_BIT_ru.md --allow-local-files --pdf

---

# 11. Key Files and Responsibilities (Short List for README)

- src/config.py — base paths: DATA_DIR, DOCS_DIR, IMG_DIR
- src/classification/role_matcher.py — embeddings and cosine similarity

- src/reports/report_official_berufe_similarity.py — main analysis + reporting pipeline:
  loads the catalog,
  computes similarity,
  saves catalog_official_berufe_scored.csv,
  generates all charts,
  writes docs/05_similarity_official_berufe.md

- data/reference/role_profile_ai_business_automation.json — machine-readable role profile
- data/processed/catalog_official_berufe.csv — unified official occupations catalog (DE/AT/CH)
- data/processed/catalog_official_berufe_scored.csv — same catalog + similarity column
- data/reference/official_berufe_bit_mapping.csv — manual mapping → BIT role levels
- docs/05_similarity_official_berufe.md — technical similarity report
- docs/06_final_report_BIT_ru.md — presentation report (Marp → PDF)
- docs/img/*.png — all generated visualizations

---

# 12. Glossary (Key Terms and Abbreviations)

- BIT — Beam Institute of Technology
- AI Business Automation Specialist — a role combining business analysis, processes, integrations, and AI automation tools
- DE / AT / CH — Germany (Deutschland), Austria, Switzerland (Confoederatio Helvetica)
- KMU — Klein- und Mittelunternehmen (SMEs)
- KldB — Klassifikation der Berufe (German occupation classification, Destatis)
- BERUFENET — occupation database by Bundesagentur für Arbeit (DE)
- AMS — Arbeitsmarktservice Österreich
- BVZ / berufsberatung.ch — Swiss occupation reference sources
- Embedding — vector representation of text (model: text-embedding-3-small)
- Cosine Similarity — similarity metric between vectors (roughly 0 to 1; higher means closer)
- Similarity Score — numeric similarity between the role profile and an occupation description
- Market Titles (job titles) — real market vacancy titles mapped to official occupations or clusters
- CRM — Customer Relationship Management systems (HubSpot, Salesforce, Pipedrive)
- ERP — Enterprise Resource Planning (SAP, Odoo, Microsoft Dynamics)
- SaaS — Software as a Service (Notion, Slack, Zendesk)
- Workflow Automation (n8n / Make / PA) — low-code/no-code automation tools:
  - n8n — open-source workflow automation
  - Make (ex-Integromat) — visual SaaS automations
  - Power Automate — Microsoft ecosystem automation
- AI Agents — automated programs using LLM/AI to perform tasks (message handling, customer replies, rule-based decisions)

---

Minimal “correct” pipeline for Hard/Soft/Tools → Matrix → BIT blocks → Charts:

A) Extract (raw → job_skills_extracted.csv)
- src/classification/skill_extractor.py — single source of extraction logic
- src/classification/skills_dictionary.py — single taxonomy/dictionary
- src/classification/extract_skills_from_raw.py — batch extractor → data/processed/job_skills_extracted.csv

B) Matrix (job_skills_extracted → competency_matrix_*.csv)
- src/reporting/competency_matrix.py — single matrix generator:
  → competency_matrix_long.csv
  → competency_matrix_pivot_country_role.csv
  → competency_top_by_country_role.csv

C) BIT blocks (competency_matrix_pivot_country_role → bit_blocks/*.csv)
Add a new script: src/reporting/bit_blocks.py (or src/reporting/competency_bit_blocks.py)
→ generates bit_blocks_* files (as exported previously)

D) Charts
- src/visualization/plot_competency_bars.py — bar charts (working version)

Heatmap module: either remove it or unify naming
(currently plot_competency_matrix cannot be imported as a module — likely missing file/import in src/visualization/)