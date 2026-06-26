$venvPython = "D:\ASSH\fbcommerce\.venv\Scripts\python.exe"
$backendDir = "D:\ASSH\fbcommerce\backend"

Write-Host "Starting fbtiktokcommerce backend..." -ForegroundColor Green
Start-Process -NoNewWindow -FilePath $venvPython -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -WorkingDirectory $backendDir
Write-Host "Backend starting on http://localhost:8000" -ForegroundColor Cyan
