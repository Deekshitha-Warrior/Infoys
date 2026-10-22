$ErrorActionPreference = 'Stop'
$projectPath = $PSScriptRoot
$backendPath = Join-Path $projectPath 'backend'
$frontendPath = Join-Path $projectPath 'frontend'
$pythonPath = Join-Path $backendPath '.venv\Scripts\python.exe'
if (!(Test-Path -LiteralPath $pythonPath)) {
    python -m venv (Join-Path $backendPath '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Python environment creation failed.' }
}
& $pythonPath -m pip install -r (Join-Path $backendPath 'requirements.txt')
if ($LASTEXITCODE -ne 0) { throw 'Backend dependency installation failed.' }
& $pythonPath -m spacy download en_core_web_sm
if ($LASTEXITCODE -ne 0) { throw 'spaCy model installation failed.' }
Push-Location $frontendPath
try {
    npm ci
    if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency installation failed.' }
    $backendProcess = Start-Process -FilePath $pythonPath -ArgumentList '-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000' -WorkingDirectory $backendPath -WindowStyle Hidden -PassThru
    Write-Host 'CareerCast is starting. Use the local URL printed below. Ctrl+C stops the app.'
    npm run dev -- --host 127.0.0.1
} finally {
    if ($backendProcess -and !$backendProcess.HasExited) { Stop-Process -Id $backendProcess.Id }
    Pop-Location
}
