#!/usr/bin/env node

/**
 * Test script for face recognition display
 * Creates a test status file to check if the display is working
 */

const fs = require('fs');
const path = require('path');

const STATUS_FILE = "/tmp/magicmirror_face_status.json";

function createTestStatusFile() {
    console.log("🧪 Testing Face Recognition Display");
    console.log("==================================");
    
    // Create test status file
    const testStatus = {
        distance: 15.5,
        person: "Andii",
        active: true,
        status: "recognized",
        timestamp: new Date().toISOString()
    };
    
    try {
        // Write test status file
        fs.writeFileSync(STATUS_FILE, JSON.stringify(testStatus, null, 2));
        console.log("✅ Test status file created:", testStatus);
        
        // Wait a moment
        setTimeout(() => {
            console.log("📝 Testing different states...");
            
            // Test 1: Person recognized
            console.log("1. Testing person recognized state...");
            const recognizedStatus = {
                distance: 12.3,
                person: "Andii",
                active: true,
                status: "recognized",
                timestamp: new Date().toISOString()
            };
            fs.writeFileSync(STATUS_FILE, JSON.stringify(recognizedStatus, null, 2));
            
            setTimeout(() => {
                // Test 2: Detecting face
                console.log("2. Testing face detection state...");
                const detectingStatus = {
                    distance: 18.7,
                    person: null,
                    active: true,
                    status: "detecting",
                    timestamp: new Date().toISOString()
                };
                fs.writeFileSync(STATUS_FILE, JSON.stringify(detectingStatus, null, 2));
                
                setTimeout(() => {
                    // Test 3: Waiting for proximity
                    console.log("3. Testing waiting state...");
                    const waitingStatus = {
                        distance: 45.2,
                        person: null,
                        active: false,
                        status: "waiting",
                        timestamp: new Date().toISOString()
                    };
                    fs.writeFileSync(STATUS_FILE, JSON.stringify(waitingStatus, null, 2));
                    
                    setTimeout(() => {
                        console.log("✅ Test completed!");
                        console.log("Check your MagicMirror display for the following messages:");
                        console.log("1. 'Тавтай морил Анди!' (when person recognized)");
                        console.log("2. 'Царай уншиж байна...' (when detecting face)");
                        console.log("3. 'Ойртож зогсоорой' (when waiting for proximity)");
                    }, 3000);
                }, 3000);
            }, 3000);
        }, 1000);
        
    } catch (error) {
        console.error("❌ Error creating test status file:", error.message);
        console.log("🔧 Make sure you have write permissions to /tmp/");
    }
}

// Run the test
createTestStatusFile();
