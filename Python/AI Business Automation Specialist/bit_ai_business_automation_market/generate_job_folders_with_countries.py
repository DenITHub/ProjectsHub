import os
from pathlib import Path

# Базовая папка
BASE_DIR = Path("data") / "raw"

# Страны для структуры
COUNTRIES = ["DE", "AT", "CH"]

# Описание структуры по ролям
STRUCTURE = {
    "business_transformation_analyst": [
        "01_business_transformation_analyst.json",
        "02_business_transformation_manager.json",
        "03_business_transformation_consultant.json",
        "04_digital_transformation_analyst.json",
        "05_digital_transformation_consultant.json",
        "06_transformation_analyst.json",
        "07_transformation_consultant.json",
        "08_business_process_analyst.json",
        "09_business_process_consultant.json",
        "10_prozessmanager_digitalisierung.json",
        "11_prozessmanager_business_transformation.json",
        "12_prozessmanager_mw_d.json",
        "13_prozess_analyst.json"
    ],
    "ai_governance_analyst": [
        "01_ai_governance_analyst.json",
        "02_ai_governance_specialist.json",
        "03_ai_governance_consultant.json",
        "04_ai_risk_analyst.json",
        "05_ai_risk_specialist.json",
        "06_ai_compliance_analyst.json",
        "07_ai_compliance_specialist.json",
        "08_responsible_ai_analyst.json",
        "09_responsible_ai_specialist.json",
        "10_ki_governance.json",
        "11_ki_compliance.json",
        "12_ki_risk_management.json",
        "13_data_governance_analyst.json",
        "14_data_risk_analyst.json"
    ],
    "ai_automation_specialist": [
        "01_ai_automation_specialist.json",
        "02_ai_automation_consultant.json",
        "03_artificial_intelligence_automation.json",
        "04_intelligent_automation_specialist.json",
        "05_intelligent_automation_consultant.json",
        "06_intelligent_automation_engineer.json",
        "07_rpa_specialist.json",
        "08_rpa_developer.json",
        "09_rpa_consultant.json",
        "10_process_automation_specialist.json",
        "11_process_automation_consultant.json",
        "12_prozessautomatisierung.json",
        "13_prozessmanager_automatisierung.json",
        "14_prozessmanager_rpa.json",
        "15_automation_engineer_ai.json"
    ],
    "prompt_engineer": [
        "01_prompt_engineer.json",
        "02_prompt_engineering.json",
        "03_prompt_specialist.json",
        "04_prompt_designer.json",
        "05_ai_prompt_engineer.json",
        "06_ai_prompt_specialist.json",
        "07_generative_ai_engineer.json",
        "08_generative_ai_specialist.json",
        "09_llm_prompting.json",
        "10_ki_prompt_engineer.json",
        "11_ki_prompt_spezialist.json"
    ],
    "junior_automation_specialist": [
        "01_junior_automation_specialist.json",
        "02_junior_automation_engineer.json",
        "03_junior_rpa_specialist.json",
        "04_junior_rpa_developer.json",
        "05_junior_rpa_consultant.json",
        "06_junior_process_automation.json",
        "07_junior_prozessmanager_automatisierung.json",
        "08_automation_assistant.json",
        "09_automation_trainee.json"
    ],
    "digital_process_analyst": [
        "01_digital_process_analyst.json",
        "02_digital_process_consultant.json",
        "03_business_process_analyst.json",
        "04_business_process_consultant.json",
        "05_process_mining_analyst.json",
        "06_process_mining_specialist.json",
        "07_process_analyst_digitalisierung.json",
        "08_prozessanalyst.json",
        "09_prozess_analyst.json",
        "10_process_improvement_analyst.json"
    ],
    "ai_project_manager": [
        "01_ai_project_manager.json",
        "02_artificial_intelligence_project_manager.json",
        "03_data_ai_project_manager.json",
        "04_ai_projektmanager.json",
        "05_projektmanager_ki.json",
        "06_projektleiter_ki.json",
        "07_digital_project_manager_ai.json",
        "08_it_project_manager_ai.json",
        "09_ai_program_manager.json"
    ],
    "ai_product_manager": [
        "01_ai_product_manager.json",
        "02_artificial_intelligence_product_manager.json",
        "03_product_manager_ai.json",
        "04_product_owner_ai.json",
        "05_ai_produktmanager.json",
        "06_produktmanager_ki.json",
        "07_product_manager_machine_learning.json",
        "08_product_owner_machine_learning.json",
        "09_generative_ai_product_manager.json"
    ]
}


def main():
    for country in COUNTRIES:
        country_dir = BASE_DIR / country
        country_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created country folder: {country_dir}")

        for role_folder, file_list in STRUCTURE.items():
            role_path = country_dir / role_folder
            role_path.mkdir(parents=True, exist_ok=True)
            print(f"  📂 Created role folder: {role_path}")

            for filename in file_list:
                file_path = role_path / filename
                if not file_path.exists():
                    file_path.write_text("", encoding="utf-8")
                    print(f"    ✔ Created file: {file_path}")
                else:
                    print(f"    ⏩ Skipped (exists): {file_path}")


if __name__ == "__main__":
    main()
