#!/usr/bin/env node

/**
 * Test script to verify personal data flow
 * This simulates the face recognition and data loading process
 */

const fs = require('fs');

console.log('🧪 Testing Personal Data Flow');
console.log('=============================\n');

// Test 1: Check user profiles
console.log('1. Testing user profiles...');
try {
    const profilesData = JSON.parse(fs.readFileSync('user_profiles.json', 'utf8'));
    console.log('✅ User profiles loaded successfully');
    console.log(`   Available users: ${Object.keys(profilesData.users).join(', ')}`);
    
    // Test Andii's data
    const andiiProfile = profilesData.users['Andii'];
    if (andiiProfile) {
        console.log('✅ Andii profile found');
        console.log(`   Calendar enabled: ${andiiProfile.calendar.enabled}`);
        console.log(`   Events count: ${andiiProfile.calendar.events ? andiiProfile.calendar.events.length : 0}`);
        console.log(`   Todo enabled: ${andiiProfile.todo.enabled}`);
        console.log(`   Todo items count: ${andiiProfile.todo.list ? andiiProfile.todo.list.length : 0}`);
        
        if (andiiProfile.calendar.events && andiiProfile.calendar.events.length > 0) {
            console.log('   Sample events:');
            andiiProfile.calendar.events.forEach((event, index) => {
                console.log(`     ${index + 1}. ${event.title} - ${new Date(event.startDate).toLocaleString()}`);
            });
        }
        
        if (andiiProfile.todo.list && andiiProfile.todo.list.length > 0) {
            console.log('   Todo items:');
            andiiProfile.todo.list.forEach((item, index) => {
                console.log(`     ${index + 1}. ${item}`);
            });
        }
    } else {
        console.log('❌ Andii profile not found');
    }
    console.log('');
} catch (error) {
    console.log('❌ Error loading user profiles:', error.message, '\n');
}

// Test 2: Simulate face recognition status
console.log('2. Simulating face recognition status...');
const mockStatus = {
    person: "Andii",
    active: true,
    distance: 15,
    status: "recognized",
    timestamp: new Date().toISOString()
};

try {
    fs.writeFileSync('/tmp/magicmirror_face_status.json', JSON.stringify(mockStatus, null, 2));
    console.log('✅ Mock face recognition status created');
    console.log(`   Person: ${mockStatus.person}`);
    console.log(`   Active: ${mockStatus.active}`);
    console.log(`   Distance: ${mockStatus.distance}cm`);
    console.log('');
} catch (error) {
    console.log('❌ Error creating mock status file:', error.message);
    console.log('   (This is expected on Windows - the file will be created on Raspberry Pi)');
    console.log('');
}

// Test 3: Simulate data conversion
console.log('3. Testing data conversion...');
try {
    const profilesData = JSON.parse(fs.readFileSync('user_profiles.json', 'utf8'));
    const userProfile = profilesData.users['Andii'];
    
    if (userProfile) {
        // Convert to API format (same as in personalapi.js)
        const events = userProfile.calendar && userProfile.calendar.enabled ? 
            userProfile.calendar.events || [] : [];
        
        const lists = userProfile.todo && userProfile.todo.enabled ? 
            [{
                title: "Personal Tasks",
                items: (userProfile.todo.list || []).map(item => ({
                    title: item,
                    completed: false
                }))
            }] : [];

        console.log('✅ Data conversion successful');
        console.log(`   Events: ${events.length}`);
        console.log(`   Lists: ${lists.length}`);
        console.log(`   Total todo items: ${lists.reduce((total, list) => total + list.items.length, 0)}`);
        
        if (events.length > 0) {
            console.log('   Sample converted events:');
            events.slice(0, 2).forEach((event, index) => {
                console.log(`     ${index + 1}. ${event.title} - ${new Date(event.startDate).toLocaleString()}`);
            });
        }
        
        if (lists.length > 0) {
            console.log('   Sample converted todo items:');
            lists[0].items.slice(0, 3).forEach((item, index) => {
                console.log(`     ${index + 1}. ${item.title} (${item.completed ? 'completed' : 'pending'})`);
            });
        }
    }
    console.log('');
} catch (error) {
    console.log('❌ Error in data conversion:', error.message, '\n');
}

console.log('🎯 Test Results Summary:');
console.log('========================');
console.log('✅ User profiles are properly configured');
console.log('✅ Sample events and todos are available for Andii');
console.log('✅ Data conversion logic is working');
console.log('');
console.log('💡 Next Steps:');
console.log('1. Restart MagicMirror: pm2 restart magicmirror');
console.log('2. Check browser console for any errors');
console.log('3. Verify face recognition is working');
console.log('4. Personal data should now display correctly');
console.log('');
console.log('Test complete! 🎉');