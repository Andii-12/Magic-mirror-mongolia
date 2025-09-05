#!/usr/bin/env node

// Simple test for personalapi module
const fs = require('fs');

console.log("🧪 Testing Personal API Module");
console.log("=============================");

// Test 1: Check if status file exists and is valid JSON
console.log("\n1. Testing status file...");
const statusFile = "/tmp/magicmirror_face_status.json";

if (fs.existsSync(statusFile)) {
    try {
        const data = JSON.parse(fs.readFileSync(statusFile, 'utf8'));
        console.log("✅ Status file exists and is valid JSON");
        console.log("   Data:", JSON.stringify(data, null, 2));
    } catch (error) {
        console.log("❌ Status file exists but invalid JSON:", error.message);
    }
} else {
    console.log("❌ Status file does not exist");
}

// Test 2: Test API connection
console.log("\n2. Testing API connection...");
const apiUrl = "https://calendar-app-production-6d2d.up.railway.app/api/magic-mirror/future-data";

fetch(apiUrl)
    .then(response => {
        if (response.ok) {
            console.log("✅ API is accessible");
            return response.json();
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    })
    .then(data => {
        console.log("✅ API returned data");
        console.log("   Users:", Object.keys(data.users || {}));
        console.log("   Sample data:", JSON.stringify(data, null, 2).substring(0, 200) + "...");
    })
    .catch(error => {
        console.log("❌ API error:", error.message);
    });

// Test 3: Check if personalapi module exists
console.log("\n3. Testing personalapi module...");
const modulePath = "./modules/personalapi/personalapi.js";
if (fs.existsSync(modulePath)) {
    console.log("✅ personalapi module exists");
} else {
    console.log("❌ personalapi module not found");
}

console.log("\n🏁 Test complete!");
