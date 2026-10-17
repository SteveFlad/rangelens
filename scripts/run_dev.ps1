param(
  [switch]$Mock = $true
)

$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $projectRoot '.venv\Scripts\python.exe'

if (-not (Test-Path $pythonExe)) {
    Write-Error "Project virtual environment not found at '$pythonExe'. Run: python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt"
    exit 1
}

Set-Location $projectRoot
& $pythonExe -m app.main $(if ($Mock) { '--mock' })
