#!/usr/bin/env node

/**
 * Test script to verify API integration
 * This tests the actual API endpoint and data processing
 */

const https = require('https');

console.log('🧪 Testing API Integration');
console.log('==========================\n');

// Test the actual API endpoint
const apiUrl = 'https://calendar-app-production-6d2d.up.railway.app/api/magic-mirror/future-data';

console.log('1. Testing API endpoint...');
console.log(`   URL: ${apiUrl}\n`);

https.get(apiUrl, (res) => {
    let data = '';
    
    res.on('data', (chunk) => {
        data += chunk;
    });
    
    res.on('end', () => {
        try {
            const apiData = JSON.parse(data);
            console.log('✅ API Response received successfully');
            console.log(`   Message: ${apiData.message}`);
            console.log(`   Date: ${apiData.date}`);
            console.log(`   Total Users: ${apiData.summary.totalUsers}`);
            console.log(`   Total Events: ${apiData.summary.totalEvents}`);
            console.log(`   Total Lists: ${apiData.summary.totalLists}\n`);
            
            // Check Andii's data
            const andiiUser = apiData.users.find(user => user.name === 'Andii');
            if (andiiUser) {
                console.log('✅ Andii user data found in API response');
                console.log(`   Events: ${andiiUser.events.length}`);
                console.log(`   Lists: ${andiiUser.lists.length}\n`);
                
                console.log('📅 Sample Events:');
                andiiUser.events.forEach((event, index) => {
                    console.log(`   ${index + 1}. ${event.title}`);
                    console.log(`      Date: ${new Date(event.startDate).toLocaleString()}`);
                    console.log(`      All Day: ${event.allDay}`);
                    console.log(`      Color: ${event.color}`);
                    if (event.description) {
                        console.log(`      Description: ${event.description}`);
                    }
                    console.log('');
                });
                
                console.log('📋 Sample Todo Lists:');
                andiiUser.lists.forEach((list, index) => {
                    console.log(`   ${index + 1}. ${list.title}`);
                    console.log(`      Date: ${new Date(list.listDate).toLocaleString()}`);
                    console.log(`      Items: ${list.items.length}`);
                    list.items.forEach((item, itemIndex) => {
                        console.log(`         ${itemIndex + 1}. ${item.title} (${item.completed ? 'completed' : 'pending'})`);
                    });
                    console.log('');
                });
                
                // Test data conversion (same as in personalapi.js)
                console.log('🔄 Testing data conversion...');
                const convertedEvents = andiiUser.events || [];
                const convertedLists = andiiUser.lists || [];
                
                console.log(`   Converted Events: ${convertedEvents.length}`);
                console.log(`   Converted Lists: ${convertedLists.length}`);
                
                // Flatten todo items (same as in personaltodo.js)
                const flattenedTodos = [];
                convertedLists.forEach(list => {
                    if (list.items) {
                        list.items.forEach(item => {
                            flattenedTodos.push({
                                title: item.title,
                                completed: item.completed,
                                listTitle: list.title
                            });
                        });
                    }
                });
                
                console.log(`   Flattened Todo Items: ${flattenedTodos.length}`);
                console.log('   Sample converted todos:');
                flattenedTodos.slice(0, 3).forEach((item, index) => {
                    console.log(`     ${index + 1}. ${item.title} (${item.completed ? 'completed' : 'pending'}) from ${item.listTitle}`);
                });
                
            } else {
                console.log('❌ Andii user not found in API response');
                console.log('   Available users:', apiData.users.map(u => u.name));
            }
            
        } catch (error) {
            console.log('❌ Error parsing API response:', error.message);
            console.log('   Raw response:', data);
        }
    });
    
}).on('error', (error) => {
    console.log('❌ Error fetching API data:', error.message);
});

console.log('2. Expected MagicMirror behavior:');
console.log('   - Personal API should fetch this data');
console.log('   - When Andii is recognized, data should be loaded');
console.log('   - Events should show: "Bagsh uulzalt", "hi", "Game"');
console.log('   - Todos should show: "Finish osh.gov.mn", "Add Media Cosmos.tech.mn"');
console.log('');
console.log('3. If data is not showing:');
console.log('   - Check browser console for "Personal API: Loaded X events" messages');
console.log('   - Verify face recognition is working');
console.log('   - Check if modules are receiving USER_DATA_LOADED notifications');
console.log('');
console.log('Test complete! 🎯');