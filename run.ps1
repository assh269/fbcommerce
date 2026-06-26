$venvPython = "D:\ASSH\fbcommerce\.venv\Scripts\python.exe"
$backendDir = "D:\ASSH\fbcommerce\backend"
$frontendDir = "D:\ASSH\fbcommerce\frontend"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  fbtiktokcommerce - Starting Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Kill any existing on our ports
netstat -ano | Select-String ":8001 " | ForEach-Object { ($_ -split '\s+')[-1] } | Where-Object { $_ -match '\d+' } | ForEach-Object { taskkill /F /PID $_ 2>$null }
netstat -ano | Select-String ":5173 " | ForEach-Object { ($_ -split '\s+')[-1] } | Where-Object { $_ -match '\d+' } | ForEach-Object { taskkill /F /PID $_ 2>$null }

Start-Sleep -Seconds 1

# Start backend
Write-Host "[1/3] Starting Backend (port 8001)..." -ForegroundColor Green
$p1 = Start-Process -NoNewWindow -FilePath $venvPython -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload" -WorkingDirectory $backendDir -PassThru
Start-Sleep -Seconds 4

# Start frontend
Write-Host "[2/3] Starting Frontend (port 5173)..." -ForegroundColor Green
$p2 = Start-Process -NoNewWindow -FilePath "npm" -ArgumentList "run dev" -WorkingDirectory $frontendDir -PassThru

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Services Running:" -ForegroundColor Cyan
Write-Host "  Backend API:  http://localhost:8001" -ForegroundColor White
Write-Host "  Frontend:     http://localhost:5173" -ForegroundColor White
Write-Host "  Health Check: http://localhost:8001/health" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the Telegram bot, run: .\start_bot.ps1" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop services." -ForegroundColor Yellow

# Keep running
while ($true) {
    Start-Sleep -Seconds 10
    if ($p1.HasExited) { Write-Host "WARNING: Backend process exited!" -ForegroundColor Red }
    if ($p2.HasExited) { Write-Host "WARNING: Frontend process exited!" -ForegroundColor Red }
}
