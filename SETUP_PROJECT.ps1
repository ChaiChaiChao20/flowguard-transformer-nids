$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv/Scripts/python.exe')) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3.12 -m venv .venv
    } else {
        & python -m venv .venv
    }
    if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.12, then run setup again.' }
}
& ./.venv/Scripts/python.exe -m pip install -r requirements-extensions.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed. Read the error above before retrying.' }
Write-Host 'Setup complete. Double-click OPEN_PROJECT.cmd to start FlowGuard.'
