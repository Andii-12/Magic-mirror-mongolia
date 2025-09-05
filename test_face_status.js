#!/usr/bin/env node

/**
 * Test script to check face recognition status file
 * This helps debug why Personal API module isn't showing data
 */

const fs = require('fs');
const path = require('path');

const STATUS_FILE = "/tmp/magicmirror_face_status.json";

console.log("🧪 Testing Face Recognition Status File");
console.log("=====================================");
console.log("");

// Check if status file exists
console.log(`📁 Checking status file: ${STATUS_FILE}`);
if (fs.existsSync(STATUS_FILE)) {
    console.log("✅ Status file exists");
    
    try {
        const data = JSON.parse(fs.readFileSync(STATUS_FILE, 'utf8'));
        console.log("📊 Status file content:");
        console.log(JSON.stringify(data, null, 2));
        
        if (data.person) {
            console.log(`👤 Recognized person: ${data.person}`);
            console.log(`🟢 Active: ${data.active}`);
            console.log(`📏 Distance: ${data.distance}cm`);
        } else {
            console.log("⚠️  No person recognized");
        }
    } catch (error) {
        console.error("❌ Error reading status file:", error.message);
    }
} else {
    console.log("❌ Status file does not exist");
    console.log("");
    console.log("🔧 This means face recognition system is not running or not creating the status file.");
    console.log("   To fix this:");
    console.log("   1. Start face recognition: python3 face_recognition_system.py");
    console.log("   2. Make sure the status file path is correct");
    console.log("   3. Check face recognition logs for errors");
}

console.log("");

// Test creating a mock status file for testing
console.log("🧪 Creating mock status file for testing...");
const mockStatus = {
    distance: 15,
    person: "Andii",
    active: true,
    status: "recognized",
    timestamp: new Date().toISOString()
};

try {
    fs.writeFileSync(STATUS_FILE, JSON.stringify(mockStatus, null, 2));
    console.log("✅ Mock status file created");
    console.log("📊 Mock data:");
    console.log(JSON.stringify(mockStatus, null, 2));
    console.log("");
    console.log("🔄 Now restart MagicMirror² to test with mock data:");
    console.log("   npm start");
} catch (error) {
    console.error("❌ Error creating mock status file:", error.message);
    console.log("   You may need to run: sudo chmod 666 /tmp/");
}

console.log("");
console.log("🔍 Debugging steps:");
console.log("1. Check if face recognition is running: ps aux | grep face_recognition");
console.log("2. Check MagicMirror logs for Personal API messages");
console.log("3. Verify the status file path in config");
console.log("4. Test with mock data (created above)");
