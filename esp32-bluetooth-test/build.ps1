# Build ESP32-S3 BLE Test
# Just run: .\build.ps1

$pio = "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe"

Write-Host "Building ESP32-S3 BLE Test..." -ForegroundColor Cyan
& $pio run

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nBuild successful!" -ForegroundColor Green
} else {
    Write-Host "`nBuild failed!" -ForegroundColor Red
}
