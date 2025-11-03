# === Load OpenAI key ===
$env:OPENAI_API_KEY = (Get-Content -Raw "$env:USERPROFILE\.continue\secrets.json" | ConvertFrom-Json).OPENAI_API_KEY

# === Start Continue CLI ===
cn --config "D:/ProjectsHub/.continue/config.yaml" --verbose
