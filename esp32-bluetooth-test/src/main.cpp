/*
 * ESP32-S3 BLE Test Program
 * 
 * This program tests Bluetooth Low Energy functionality on ESP32-S3.
 * It performs two tests:
 * 1. BLE Advertising - Makes the device visible to other BLE scanners
 * 2. BLE Scanning - Scans for nearby BLE devices
 * 
 * Upload this sketch and open Serial Monitor at 115200 baud.
 */

#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>

// Device name that will appear in BLE scans
#define DEVICE_NAME "ESP32-S3-TEST"

BLEScan* pBLEScan;
bool bluetoothWorking = false;

// Callback class for BLE scan results
class MyAdvertisedDeviceCallbacks: public BLEAdvertisedDeviceCallbacks {
    void onResult(BLEAdvertisedDevice advertisedDevice) {
      Serial.printf("  Found: %s (RSSI: %d)\n", 
                    advertisedDevice.toString().c_str(),
                    advertisedDevice.getRSSI());
    }
};

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n=================================");
  Serial.println("ESP32-S3 Bluetooth BLE Test");
  Serial.println("=================================\n");
  
  // Test 1: Initialize BLE
  Serial.println("TEST 1: Initializing BLE...");
  try {
    BLEDevice::init(DEVICE_NAME);
    Serial.println("✓ BLE initialized successfully");
    bluetoothWorking = true;
  } catch (...) {
    Serial.println("✗ FAILED: Could not initialize BLE");
    Serial.println("  Hardware may be damaged or disabled");
    return;
  }
  
  // Test 2: Start BLE Advertising
  Serial.println("\nTEST 2: Starting BLE Advertising...");
  try {
    BLEServer *pServer = BLEDevice::createServer();
    BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->addServiceUUID("4fafc201-1fb5-459e-8fcc-c5c9c331914b");
    pAdvertising->setScanResponse(true);
    pAdvertising->setMinPreferred(0x06);  // iPhone connection tuning
    pAdvertising->setMinPreferred(0x12);
    BLEDevice::startAdvertising();
    
    Serial.println("✓ BLE Advertising started");
    Serial.printf("  Device name: %s\n", DEVICE_NAME);
    Serial.println("  Other devices can now discover this ESP32-S3");
  } catch (...) {
    Serial.println("✗ FAILED: Could not start advertising");
    bluetoothWorking = false;
    return;
  }
  
  // Test 3: Setup BLE Scanner
  Serial.println("\nTEST 3: Setting up BLE Scanner...");
  try {
    pBLEScan = BLEDevice::getScan();
    pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
    pBLEScan->setActiveScan(true);  // Active scan uses more power but gets more info
    pBLEScan->setInterval(100);
    pBLEScan->setWindow(99);  // Less or equal to setInterval value
    
    Serial.println("✓ BLE Scanner configured");
  } catch (...) {
    Serial.println("✗ FAILED: Could not setup scanner");
    bluetoothWorking = false;
    return;
  }
  
  Serial.println("\n=================================");
  if (bluetoothWorking) {
    Serial.println("✓ BLUETOOTH IS WORKING!");
    Serial.println("=================================");
    Serial.println("\nScanning for nearby BLE devices...");
    Serial.println("(Press RESET to scan again)\n");
  } else {
    Serial.println("✗ BLUETOOTH TEST FAILED");
    Serial.println("=================================");
    Serial.println("\nCheck:");
    Serial.println("- Board selection (should be ESP32-S3)");
    Serial.println("- USB cable and port");
    Serial.println("- Bluetooth not disabled in menuconfig");
    Serial.println("- Hardware may be damaged");
  }
}

void loop() {
  if (!bluetoothWorking) {
    delay(10000);
    return;
  }
  
  // Scan for BLE devices every 5 seconds
  Serial.println("--- Scanning for 5 seconds ---");
  BLEScanResults foundDevices = pBLEScan->start(5, false);
  
  int deviceCount = foundDevices.getCount();
  Serial.printf("\nScan complete. Found %d device(s)\n\n", deviceCount);
  
  if (deviceCount == 0) {
    Serial.println("No BLE devices found nearby.");
    Serial.println("Try scanning with your phone's BLE scanner app");
    Serial.printf("to see if it can detect '%s'\n\n", DEVICE_NAME);
  }
  
  pBLEScan->clearResults();   // Free memory
  delay(5000);  // Wait 5 seconds before next scan
}
