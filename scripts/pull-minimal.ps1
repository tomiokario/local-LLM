[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$OllamaCommand = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $OllamaCommand) {
    $OllamaExe = Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama.exe"
    if (Test-Path $OllamaExe) {
        $OllamaCommand = Get-Command $OllamaExe -ErrorAction SilentlyContinue
    }
}

if (-not $OllamaCommand) {
    throw "ollama command was not found. Run scripts/setup.ps1 -InstallOllama first, then restart PowerShell."
}

$Models = @(
    "batiai/gemma4-26b:iq4",
    "batiai/qwen3.6-35b:iq3"
)

foreach ($Model in $Models) {
    Write-Host "Pulling $Model"
    & $OllamaCommand.Source pull $Model
}

Write-Host ""
Write-Host "Installed models:"
& $OllamaCommand.Source list
