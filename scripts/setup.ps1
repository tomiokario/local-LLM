[CmdletBinding()]
param(
    [switch]$InstallOllama,
    [switch]$InstallAider,
    [switch]$PullMinimal
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$OllamaModels = Join-Path $Root "ollama"
$LmStudioModels = Join-Path $Root "lmstudio"
$WorkDir = Join-Path $Root "work"
$NotesDir = Join-Path $Root "notes"
$OllamaBin = Join-Path $env:LOCALAPPDATA "Programs\Ollama"
$AiderBin = Join-Path $env:USERPROFILE ".local\bin"

function Add-UserPath {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        return
    }

    $CurrentUserPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $Parts = @()
    if ($CurrentUserPath) {
        $Parts = $CurrentUserPath -split ";" | Where-Object { $_ }
    }

    if ($Parts -notcontains $Path) {
        $NewUserPath = (@($Parts) + $Path) -join ";"
        [Environment]::SetEnvironmentVariable("Path", $NewUserPath, "User")
        Write-Host "Added to user PATH: $Path"
    }

    if (($env:Path -split ";") -notcontains $Path) {
        $env:Path = "$Path;$env:Path"
    }
}

foreach ($Path in @($OllamaModels, $LmStudioModels, $WorkDir, $NotesDir)) {
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
}

[Environment]::SetEnvironmentVariable("OLLAMA_MODELS", $OllamaModels, "User")
$env:OLLAMA_MODELS = $OllamaModels

Write-Host "OLLAMA_MODELS = $OllamaModels"
Write-Host "Directories are ready under $Root"

if ($InstallOllama) {
    if (Get-Command ollama -ErrorAction SilentlyContinue) {
        Write-Host "Ollama is already available."
    } else {
        Write-Host "Installing Ollama from the official installer script..."
        powershell -ExecutionPolicy Bypass -NoProfile -Command "irm https://ollama.com/install.ps1 | iex"
    }
}

if ($InstallAider) {
    if (Get-Command aider -ErrorAction SilentlyContinue) {
        Write-Host "aider is already available."
    } else {
        Write-Host "Installing aider from the official installer script..."
        powershell -ExecutionPolicy Bypass -NoProfile -Command "irm https://aider.chat/install.ps1 | iex"
    }
}

Add-UserPath $OllamaBin
Add-UserPath $AiderBin

if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    Write-Host ""
    Write-Host "GPU:"
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
} else {
    Write-Warning "nvidia-smi was not found. Check the NVIDIA driver installation."
}

if ($PullMinimal) {
    & (Join-Path $PSScriptRoot "pull-minimal.ps1")
}

Write-Host ""
Write-Host "Done. Restart PowerShell, Ollama, and LM Studio so the user environment variable is picked up."
