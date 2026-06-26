$venvPython = "D:\ASSH\fbcommerce\.venv\Scripts\python.exe"
$backendDir = "D:\ASSH\fbcommerce\backend"

Write-Host "Starting fbtiktokcommerce Telegram bot..." -ForegroundColor Green
Start-Process -NoNewWindow -FilePath $venvPython -ArgumentList "-m bot.main" -WorkingDirectory $backendDir
Write-Host "Bot started!" -ForegroundColor Cyan
