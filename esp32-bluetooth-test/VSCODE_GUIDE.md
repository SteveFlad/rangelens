# Quick Start Guide - Running ESP32 Test in VS Code

## Step-by-Step Instructions

### 1️⃣ Connect Hardware
- Plug ESP32-S3 into computer via USB cable
- Wait for Windows to recognize the device

### 2️⃣ Build the Code
Look at the **bottom toolbar** in VS Code (blue/purple bar)

Click the **✓** (checkmark) icon - this builds/compiles the code
- Or press `Ctrl+Alt+B`

Wait for "SUCCESS" message in the terminal

### 3️⃣ Upload to ESP32
Click the **→** (right arrow) icon in the bottom toolbar
- Or press `Ctrl+Alt+U`

Wait for upload to complete (shows progress percentage)

### 4️⃣ View Results
Click the **🔌** (plug) icon in the bottom toolbar to open Serial Monitor
- Or press `Ctrl+Alt+S`

You should immediately see:
```
=================================
ESP32-S3 Bluetooth BLE Test
=================================

TEST 1: Initializing BLE...
✓ BLE initialized successfully
...
```

## PlatformIO Toolbar Buttons

Located at the **very bottom** of VS Code window (left side of blue bar):

| Icon | Name | Shortcut | Purpose |
|------|------|----------|---------|
| 🏠 | PlatformIO Home | | Open PlatformIO home screen |
| ✓ | Build | Ctrl+Alt+B | Compile the code |
| → | Upload | Ctrl+Alt+U | Upload to ESP32 |
| 🗑️ | Clean | | Delete build files |
| 🔌 | Serial Monitor | Ctrl+Alt+S | View serial output |

## Troubleshooting

### "Can't see the toolbar buttons"
- Look at the very bottom of VS Code (blue/purple status bar)
- If not visible, open Command Palette (Ctrl+Shift+P) and type "PlatformIO"

### "Upload failed" or "Device not found"
1. Check USB cable is connected
2. Try pressing the BOOT button on ESP32-S3 during upload
3. In platformio.ini, add your COM port:
   ```ini
   upload_port = COM3  ; Change COM3 to your actual port
   ```

### "How do I find my COM port?"
- Click the Serial Monitor icon (🔌)
- PlatformIO will show available ports
- Usually COM3, COM4, COM5, etc. on Windows

### Serial Monitor shows gibberish
- Check that `monitor_speed = 115200` is in platformio.ini (it is)
- Close and reopen Serial Monitor
- Press the RESET button on ESP32-S3

## Expected Output

### ✅ Success (Bluetooth Working):
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
```

### ❌ Failure (Bluetooth Not Working):
```
TEST 1: Initializing BLE...
✗ FAILED: Could not initialize BLE
  Hardware may be damaged or disabled
```

## Next Steps

**If test passes**: Your ESP32-S3 Bluetooth is working correctly!

**If test fails**: 
1. Try a different ESP32-S3 board
2. Check board settings in platformio.ini
3. Hardware may be damaged
