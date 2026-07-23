# Build and Upload ESP32-S3 BLE Test
# Just run: .\upload.ps1

$pio = "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe"

Write-Host "Building and uploading to ESP32-S3..." -ForegroundColor Cyan
& $pio run --target upload

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nUpload successful!" -ForegroundColor Green
    Write-Host "To view serial output, run: .\monitor.ps1" -ForegroundColor Yellow
} else {
    Write-Host "`nUpload failed!" -ForegroundColor Red
    Write-Host "Make sure ESP32-S3 is connected via USB" -ForegroundColor Yellow
}
