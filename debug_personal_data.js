#!/usr/bin/env node

/**
 * Debug script to check personal data loading issues
 * Run this to diagnose why personal calendar and todo are showing undefined/no events
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 MagicMirror Personal Data Debug Tool');
console.log('=====================================\n');

// Check if face recognition status file exists
const statusFile = '/tmp/magicmirror_face_status.json';
console.log('1. Checking face recognition status...');
if (fs.existsSync(statusFile)) {
    try {
        const statusData = JSON.parse(fs.readFileSync(statusFile, 'utf8'));
        console.log('✅ Face status file found:');
        console.log(`   Person: ${statusData.person || 'null'}`);
        console.log(`   Active: ${statusData.active}`);
        console.log(`   Distance: ${statusData.distance}cm`);
        console.log(`   Status: ${statusData.status}`);
        console.log(`   Timestamp: ${statusData.timestamp}\n`);
    } catch (error) {
        console.log('❌ Error reading face status file:', error.message, '\n');
    }
} else {
    console.log('❌ Face status file not found at:', statusFile, '\n');
}

// Check user profiles
console.log('2. Checking user profiles...');
const profilesFile = 'user_profiles.json';
if (fs.existsSync(profilesFile)) {
    try {
        const profilesData = JSON.parse(fs.readFileSync(profilesFile, 'utf8'));
        console.log('✅ User profiles found:');
        console.log('   Available users:', Object.keys(profilesData.users));
        console.log('   Default user:', profilesData.default.name);
        
        // Check if current user from face recognition matches any profile
        if (fs.existsSync(statusFile)) {
            try {
                const statusData = JSON.parse(fs.readFileSync(statusFile, 'utf8'));
                if (statusData.person) {
                    const userExists = profilesData.users[statusData.person];
                    if (userExists) {
                        console.log(`   ✅ Face recognition user "${statusData.person}" found in profiles`);
                    } else {
                        console.log(`   ❌ Face recognition user "${statusData.person}" NOT found in profiles`);
                        console.log('   💡 This is likely the cause of the issue!');
                    }
                }
            } catch (error) {
                console.log('   Error checking user match:', error.message);
            }
        }
        console.log('');
    } catch (error) {
        console.log('❌ Error reading user profiles:', error.message, '\n');
    }
} else {
    console.log('❌ User profiles file not found at:', profilesFile, '\n');
}

// Check if Images directory exists (for face recognition training)
console.log('3. Checking face recognition training data...');
const imagesDir = 'Images';
if (fs.existsSync(imagesDir)) {
    const faceFolders = fs.readdirSync(imagesDir).filter(item => 
        fs.statSync(path.join(imagesDir, item)).isDirectory()
    );
    console.log('✅ Face recognition training data found:');
    console.log('   Trained faces:', faceFolders);
    console.log('');
} else {
    console.log('❌ Images directory not found. Face recognition may not work.\n');
}

// Check trainer.yml
console.log('4. Checking face recognition model...');
const trainerPaths = ['trainer.yml', 'python_code/trainer.yml'];
let trainerFound = false;
for (const trainerPath of trainerPaths) {
    if (fs.existsSync(trainerPath)) {
        console.log(`✅ Trainer model found at: ${trainerPath}`);
        trainerFound = true;
        break;
    }
}
if (!trainerFound) {
    console.log('❌ No trainer.yml found. Face recognition will not work.');
}
console.log('');

// Recommendations
console.log('🔧 RECOMMENDATIONS:');
console.log('===================');

if (fs.existsSync(statusFile)) {
    try {
        const statusData = JSON.parse(fs.readFileSync(statusFile, 'utf8'));
        if (statusData.person && fs.existsSync(profilesFile)) {
            const profilesData = JSON.parse(fs.readFileSync(profilesFile, 'utf8'));
            if (!profilesData.users[statusData.person]) {
                console.log('1. ❌ USER NAME MISMATCH:');
                console.log(`   Face recognition detected: "${statusData.person}"`);
                console.log(`   Available in profiles: ${Object.keys(profilesData.users).join(', ')}`);
                console.log('   💡 Fix: Either rename the face recognition folder or update user_profiles.json');
                console.log('');
            }
        }
    } catch (error) {
        console.log('Error in recommendations:', error.message);
    }
}

console.log('2. 🔄 RESTART SEQUENCE:');
console.log('   a) Stop face recognition: Ctrl+C in the terminal running face_recognition_system.py');
console.log('   b) Restart MagicMirror: pm2 restart magicmirror');
console.log('   c) Start face recognition: python3 face_recognition_system.py');
console.log('');

console.log('3. 📝 CHECK LOGS:');
console.log('   - Face recognition logs: Check terminal output');
console.log('   - MagicMirror logs: pm2 logs magicmirror');
console.log('   - Browser console: F12 in browser');
console.log('');

console.log('Debug complete! 🎯');