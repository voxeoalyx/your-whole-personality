param([int]$Port = 8765)
$ErrorActionPreference = 'Stop'
$localPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (Test-Path -LiteralPath $localPython) {
    & $localPython (Join-Path $PSScriptRoot 'server.py') --port $Port
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 (Join-Path $PSScriptRoot 'server.py') --port $Port
} else {
    $pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($pythonCommand -and $pythonCommand.Source -notmatch 'WindowsApps') {
        & $pythonCommand.Source (Join-Path $PSScriptRoot 'server.py') --port $Port
    } else {
        throw 'Python 3.10+ is required. Install Python, then run: python server.py'
    }
}
exit $LASTEXITCODE
