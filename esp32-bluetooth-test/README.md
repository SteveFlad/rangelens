# ESP32-S3 Bluetooth BLE Test

This Arduino sketch tests Bluetooth Low Energy (BLE) functionality on ESP32-S3 boards.

## What This Test Does

1. **Initializes BLE** - Checks if the Bluetooth hardware responds
2. **Starts Advertising** - Makes the ESP32-S3 visible as "ESP32-S3-TEST"
3. **Scans for Devices** - Looks for other BLE devices nearby
4. **Reports Results** - Shows success/failure for each test

## Requirements

### Hardware
- ESP32-S3 development board
- USB cable
- Computer with VS Code

### Software
- VS Code with PlatformIO IDE extension installed
- No additional libraries needed (BLE is built-in)

## How to Run in VS Code

### 1. Open Project in PlatformIO

This project is already configured for PlatformIO. Simply open this folder in VS Code.

### 2. Build the Project

Click the **Build** button (✓ checkmark) in the PlatformIO toolbar at the bottom of VS Code, or:
- Press `Ctrl+Alt+B`
- Or open Command Palette (Ctrl+Shift+P) and run "PlatformIO: Build"

### 3. Upload to ESP32-S3

1. Connect your ESP32-S3 to your computer via USB
2. Click the **Upload** button (→ arrow) in the PlatformIO toolbar, or:
   - Press `Ctrl+Alt+U`
   - Or open Command Palette and run "PlatformIO: Upload"

### 4. Open Serial Monitor

Click the **Serial Monitor** button (🔌 plug icon) in the PlatformIO toolbar, or:
- Press `Ctrl+Alt+S`
- Or open Command Palette and run "PlatformIO: Serial Monitor"

The serial monitor will open at 115200 baud automatically and show the test results.

## Expected Output

### If Bluetooth is Working:
```
=================================
ESP32-S3 Bluetooth BLE Test
=================================

TEST 1: Initializing BLE...
✓ BLE initialized successfully

TEST 2: Starting BLE Advertising...
✓ BLE Advertising started
  Device name: ESP32-S3-TEST
  Other devices can now discover this ESP32-S3

TEST 3: Setting up BLE Scanner...
✓ BLE Scanner configured

=================================
✓ BLUETOOTH IS WORKING!
=================================

Scanning for nearby BLE devices...
--- Scanning for 5 seconds ---
  Found: Device Name (RSSI: -45)
  Found: Another Device (RSSI: -67)

Scan complete. Found 2 device(s)
```

### If Bluetooth is NOT Working:
```
TEST 1: Initializing BLE...
✗ FAILED: Could not initialize BLE
  Hardware may be damaged or disabled
```

## Troubleshooting

### Bluetooth initialization fails
1. **Check board selection**: Ensure ESP32-S3 is selected, not ESP32 or ESP32-S2
2. **Check partition scheme**: Try "Huge APP (3MB No OTA/1MB SPIFFS)"
3. **Verify Bluetooth is enabled**: Some ESP32-S3 builds have BLE disabled
4. **Try different USB port**: Some USB hubs don't provide enough power

### No devices found in scan
- This is normal if there are no BLE devices nearby
- Use a BLE scanner app on your phone (e.g., "nRF Connect") to verify the ESP32-S3 is advertising

### Upload fails
1. Hold the BOOT button while clicking Upload
2. Release BOOT button after "Connecting..." appears
3. Try a different USB cable (data cable, not charge-only)

### Hardware might be damaged if:
- Multiple ESP32-S3 boards all fail the same test
- The board was exposed to water or static electricity
- BLE worked before but suddenly stopped
- WiFi works but Bluetooth doesn't (separate antennas)

## Testing with Phone Apps

To verify the ESP32-S3 is advertising:

### iOS
- Install "nRF Connect" or "LightBlue" from App Store
- Open app and look for "ESP32-S3-TEST" in the device list

### Android
- Install "nRF Connect" from Google Play
- Open app and scan for "ESP32-S3-TEST"

## Next Steps

If this test passes:
- Bluetooth hardware is working correctly
- You can proceed with your BLE project
- The issue may be in your application code, not hardware

If this test fails:
- Try a different ESP32-S3 board to rule out hardware damage
- Check if Bluetooth is disabled in your board's configuration
- Contact your board supplier if under warranty
