#!/usr/bin/env node

/**
 * Debug script for Personal API integration
 * This helps troubleshoot why personal data isn't showing
 */

const fs = require('fs');

console.log("🔍 Personal API Debug Tool");
console.log("=========================");
console.log("");

// Check status file
const STATUS_FILE = "C:\\tmp\\magicmirror_face_status.json";
console.log("1. Checking face recognition status file...");
if (fs.existsSync(STATUS_FILE)) {
    try {
        const statusData = JSON.parse(fs.readFileSync(STATUS_FILE, 'utf8'));
        console.log("✅ Status file found:");
        console.log(`   Person: ${statusData.person || 'None'}`);
        console.log(`   Active: ${statusData.active}`);
        console.log(`   Distance: ${statusData.distance}cm`);
        console.log(`   Status: ${statusData.status}`);
    } catch (error) {
        console.log("❌ Error reading status file:", error.message);
    }
} else {
    console.log("❌ Status file not found");
    console.log("   This means face recognition is not running");
}

console.log("");

// Test API connectivity
console.log("2. Testing API connectivity...");
const API_URL = "https://calendar-app-production-6d2d.up.railway.app/api/magic-mirror/future-data";

fetch(API_URL)
    .then(response => {
        if (response.ok) {
            console.log("✅ API is accessible");
            return response.json();
        } else {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
    })
    .then(data => {
        console.log("📊 API Response:");
        console.log(`   Users: ${data.users.length}`);
        console.log(`   Events: ${data.summary.totalEvents}`);
        console.log(`   Lists: ${data.summary.totalLists}`);
        console.log("");
        console.log("👥 Available users:");
        data.users.forEach((user, index) => {
            console.log(`   ${index + 1}. ${user.name} (${user.events.length} events, ${user.lists.length} lists)`);
        });
    })
    .catch(error => {
        console.log("❌ API error:", error.message);
    });

console.log("");

// Check MagicMirror config
console.log("3. Checking MagicMirror configuration...");
if (fs.existsSync("config/config.js")) {
    const configContent = fs.readFileSync("config/config.js", 'utf8');
    if (configContent.includes("personalapi")) {
        console.log("✅ Personal API module found in config");
    } else {
        console.log("❌ Personal API module not found in config");
        console.log("   Add the module to config/config.js");
    }
} else {
    console.log("❌ config/config.js not found");
}

console.log("");

// Check module files
console.log("4. Checking module files...");
const moduleFiles = [
    "modules/personalapi/personalapi.js",
    "modules/personalapi/personalapi.css",
    "modules/personalapi/node_helper.js"
];

moduleFiles.forEach(file => {
    if (fs.existsSync(file)) {
        console.log(`✅ ${file} exists`);
    } else {
        console.log(`❌ ${file} missing`);
    }
});

console.log("");

// Create test status file
console.log("5. Creating test status file...");
const testStatus = {
    distance: 15,
    person: "Andii",
    active: true,
    status: "recognized",
    timestamp: new Date().toISOString()
};

try {
    fs.writeFileSync(STATUS_FILE, JSON.stringify(testStatus, null, 2));
    console.log("✅ Test status file created");
    console.log("   This will simulate face recognition for testing");
} catch (error) {
    console.log("❌ Error creating test status file:", error.message);
}

console.log("");
console.log("🎯 Next steps:");
console.log("1. If face recognition is not running, start it:");
console.log("   python3 face_recognition_system.py");
console.log("");
console.log("2. If API is not accessible, check your internet connection");
console.log("");
console.log("3. If module is not in config, add it to config/config.js");
console.log("");
console.log("4. Restart MagicMirror² to test:");
console.log("   npm start");
console.log("");
console.log("5. Check browser console for Personal API messages");
console.log("");
console.log("6. The test status file will simulate 'Andii' being recognized");
