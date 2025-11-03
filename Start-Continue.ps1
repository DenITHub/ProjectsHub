chcp 65001 | Out-Null
Write-Host "Checking environment..."

$secretsPath = "$env:USERPROFILE\.continue\secrets.json"
if (Test-Path $secretsPath) {
    $key = (Get-Content -Raw $secretsPath | ConvertFrom-Json).OPENAI_API_KEY
    if ($key -and $key.StartsWith("sk-")) {
        $env:OPENAI_API_KEY = $key
        Write-Host "✅ API key loaded successfully."
    } else {
        Write-Host "⚠️  Invalid or missing API key." -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "❌ secrets.json not found." -ForegroundColor Red
    exit 1
}

if (-not (Get-Command cn -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Continue CLI not found. Run: npm i -g @continuedev/cli" -ForegroundColor Red
    exit 1
}

Write-Host "🚀 Starting Continue CLI..."
Start-Sleep -Seconds 1

cn --config "D:\ProjectsHub\.continue\config.yaml" --verbose
