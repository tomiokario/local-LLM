[CmdletBinding()]
param(
    [string]$Model = "ollama_chat/batiai/qwen3.6-35b:iq3",
    [string]$ProjectPath = (Join-Path (Split-Path -Parent $PSScriptRoot) "work")
)

$ErrorActionPreference = "Stop"

$AiderCommand = Get-Command aider -ErrorAction SilentlyContinue
if (-not $AiderCommand) {
    $AiderExe = Join-Path $env:USERPROFILE ".local\bin\aider.exe"
    if (Test-Path $AiderExe) {
        $AiderCommand = Get-Command $AiderExe -ErrorAction SilentlyContinue
    }
}

if (-not $AiderCommand) {
    throw "aider command was not found. Run scripts/setup.ps1 -InstallAider first, then restart PowerShell."
}

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

Set-Location $ProjectPath
& $AiderCommand.Source --model $Model @args
