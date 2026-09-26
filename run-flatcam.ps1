$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$pythonExe = Join-Path $PSScriptRoot '.venv\Scripts\pythonw.exe'
if (-not (Test-Path -LiteralPath $pythonExe)) {
    throw 'Create .venv and install requirements.txt first. See README.md.'
}
$env:QT_API = 'pyqt6'
Start-Process -FilePath $pythonExe -ArgumentList @('FlatCAM.py') -WorkingDirectory $PSScriptRoot
