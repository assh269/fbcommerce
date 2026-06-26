$frontendDir = "D:\ASSH\fbcommerce\frontend"

Write-Host "Starting fbtiktokcommerce frontend..." -ForegroundColor Green
Start-Process -NoNewWindow -FilePath "npm" -ArgumentList "run dev" -WorkingDirectory $frontendDir
Write-Host "Frontend starting on http://localhost:5173" -ForegroundColor Cyan
