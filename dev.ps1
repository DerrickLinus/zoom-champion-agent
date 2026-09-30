param([int]$ApiPort=8000,[int]$WebPort=5173)
$root=Split-Path -Parent $MyInvocation.MyCommand.Path
Start-Process powershell -ArgumentList "-NoExit","-Command","Set-Location '$root\backend'; uvicorn app.main:app --reload --port $ApiPort"
Set-Location $root
npm run dev -- --port $WebPort
