param(
    [switch]$Review,
    [switch]$SkipSetup,
    [string]$PythonExecutable
)
$ErrorActionPreference = 'Stop'
$projectPath = $PSScriptRoot
$backendPath = Join-Path $projectPath 'backend'
$frontendPath = Join-Path $projectPath 'frontend'
$pythonPath = if ($PythonExecutable) { $PythonExecutable } else { Join-Path $backendPath '.venv\Scripts\python.exe' }
if (!(Test-Path -LiteralPath $pythonPath)) {
    if ($PythonExecutable -or $SkipSetup) { throw 'The selected Python environment does not exist. Run setup first.' }
    python -m venv (Join-Path $backendPath '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Python environment creation failed.' }
}
if (!$SkipSetup) {
    $installTarget = if ($Review) { "${projectPath}[review]" } else { $projectPath }
    & $pythonPath -m pip install $installTarget
    if ($LASTEXITCODE -ne 0) { throw 'CareerCast package installation failed.' }
    & $pythonPath -c "import spacy; spacy.load('en_core_web_sm')" 2>$null
    if ($LASTEXITCODE -ne 0) {
        & $pythonPath -m spacy download en_core_web_sm
        if ($LASTEXITCODE -ne 0) { throw 'spaCy model installation failed.' }
    }
    Push-Location $frontendPath
    try {
        npm ci
        if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency installation failed.' }
    } finally { Pop-Location }
}
$backendProcess = $null
$reviewProcess = $null
Push-Location $frontendPath
try {
    $backendProcess = Start-Process -FilePath $pythonPath -ArgumentList '-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000' -WorkingDirectory $backendPath -WindowStyle Hidden -PassThru
    $ready = $false
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        if ($backendProcess.HasExited) { throw 'The API could not start. Check dependencies and port 8000.' }
        try {
            $response = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/health' -UseBasicParsing -TimeoutSec 2
            if ($response.StatusCode -eq 200) { $ready = $true; break }
        } catch { }
        Start-Sleep -Milliseconds 500
    }
    if (!$ready) { throw 'The API did not become ready. Check the backend environment.' }
    if ($Review) {
        $reviewProcess = Start-Process -FilePath $pythonPath -ArgumentList '-m','streamlit','run','review_app.py','--server.address','127.0.0.1','--server.port','8501','--server.headless','true' -WorkingDirectory $backendPath -WindowStyle Hidden -PassThru
        Write-Host 'Review app: http://127.0.0.1:8501'
    }
    Write-Host 'CareerCast: http://127.0.0.1:5173 | API: http://127.0.0.1:8000/docs'
    Write-Host 'Keep this terminal open. Ctrl+C stops services created by this launcher.'
    npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
    if ($LASTEXITCODE -ne 0) { throw 'Frontend startup failed. Check port 5173.' }
} finally {
    if ($reviewProcess -and !$reviewProcess.HasExited) { Stop-Process -Id $reviewProcess.Id }
    if ($backendProcess -and !$backendProcess.HasExited) { Stop-Process -Id $backendProcess.Id }
    Pop-Location
}
