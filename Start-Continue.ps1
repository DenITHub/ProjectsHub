# Start-Continue.ps1 — Safe autostart for Continue CLI
# Tested on PowerShell 7+, UTF-8 without BOM

chcp 65001 | Out-Null

function Write-Color {
    param (
        [string]$Text,
        [ConsoleColor]$Color = "Gray"
    )
    $oldColor = $Host.UI.RawUI.ForegroundColor
    $Host.UI.RawUI.ForegroundColor = $Color
    Write-Host $Text
    $Host.UI.RawUI.ForegroundColor = $oldColor
}

# === Load API key ===
$secretsPath = "$env:USERPROFILE\.continue\secrets.json"
if (Test-Path $secretsPath) {
    $apiKey = (Get-Content -Raw $secretsPath | ConvertFrom-Json).OPENAI_API_KEY
    if ($apiKey -and $apiKey.StartsWith("sk-")) {
        Write-Color "OK: API key loaded successfully." Green
        $env:OPENAI_API_KEY = $apiKey
    } else {
        Write-Color "Warning: secrets.json found but key missing or invalid." Yellow
        exit 1
    }
} else {
    Write-Color "Error: secrets.json not found at $secretsPath" Red
    exit 1
}

# === Check CLI ===
if (-not (Get-Command cn -ErrorAction SilentlyContinue)) {
    Write-Color "Error: CLI command 'cn' not found. Install with: npm i -g @continuedev/cli" Red
    exit 1
}

# === Check CLI version ===
$cliVersion = (cn --version) 2>$null
if ($cliVersion -ne "1.5.8") {
    Write-Color "Warning: Installed CLI version is $cliVersion (recommended v1.5.8)." Yellow
} else {
    Write-Color "Continue CLI v$cliVersion is OK." Cyan
}

# === Clean logs older than 7 days ===
$logDir = "$env:USERPROFILE\.continue\logs"
if (Test-Path $logDir) {
    Get-ChildItem -Path $logDir -File | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } | Remove-Item -Force
    Write-Color "Old logs cleaned." DarkGray
}

# === Start CLI ===
Write-Color "Starting Continue CLI..." Cyan
Start-Sleep -Seconds 1

$projectPath = "D:\ProjectsHub"
$configPath  = "$projectPath\.continue\config.yaml"

if (-not (Test-Path $configPath)) {
    Write-Color "Error: config.yaml not found at $configPath" Red
    exit 1
}

Set-Location $projectPath
cn --config $configPath --verbose
