# Open Serial Monitor
# Just run: .\monitor.ps1
# Press Ctrl+C to exit

$pio = "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe"

Write-Host "Opening serial monitor at 115200 baud..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to exit" -ForegroundColor Yellow
Write-Host ""

& $pio device monitor -b 115200
