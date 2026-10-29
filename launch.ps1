$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw 'The project environment is not set up. Run SETUP_PROJECT.ps1 once, then launch again.'
}
& $python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8502
if ($LASTEXITCODE -ne 0) { throw 'Streamlit exited with an error. Read the message above.' }

