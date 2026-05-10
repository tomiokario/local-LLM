[CmdletBinding()]
param()

$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
$OllamaExe = Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama.exe"
$AiderExe = Join-Path $env:USERPROFILE ".local\bin\aider.exe"

Write-Host "Root: $Root"
Write-Host "OLLAMA_MODELS(process): $env:OLLAMA_MODELS"
Write-Host "OLLAMA_MODELS(user): $([Environment]::GetEnvironmentVariable("OLLAMA_MODELS", "User"))"
Write-Host ""

Write-Host "Directories:"
foreach ($Path in @("ollama", "lmstudio", "work", "notes")) {
    $FullPath = Join-Path $Root $Path
    if (Test-Path $FullPath) {
        $ItemCount = (Get-ChildItem -Force $FullPath | Measure-Object).Count
        Write-Host "  OK  $FullPath ($ItemCount items)"
    } else {
        Write-Host "  NG  $FullPath"
    }
}

Write-Host ""
Write-Host "GPU:"
if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
} else {
    Write-Host "  nvidia-smi not found"
}

Write-Host ""
Write-Host "Ollama:"
$OllamaCommand = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $OllamaCommand -and (Test-Path $OllamaExe)) {
    $OllamaCommand = Get-Command $OllamaExe -ErrorAction SilentlyContinue
}
if ($OllamaCommand) {
    & $OllamaCommand.Source --version
    & $OllamaCommand.Source list
} else {
    Write-Host "  ollama command not found"
}

Write-Host ""
Write-Host "aider:"
$AiderCommand = Get-Command aider -ErrorAction SilentlyContinue
if (-not $AiderCommand -and (Test-Path $AiderExe)) {
    $AiderCommand = Get-Command $AiderExe -ErrorAction SilentlyContinue
}
if ($AiderCommand) {
    & $AiderCommand.Source --version
} else {
    Write-Host "  aider command not found"
}
