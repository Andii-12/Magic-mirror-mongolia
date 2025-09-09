#!/usr/bin/env node
/**
 * Debug script to test personal data flow
 * This simulates the data flow between modules
 */

const https = require('https');

const API_URL = 'https://calendar-app-production-6d2d.up.railway.app/api/magic-mirror/future-data';

console.log('🔍 Debug Personal Data Flow');
console.log('=' * 50);

// Simulate the data flow
function simulateDataFlow() {
    console.log('1. Fetching data from API...');
    
    https.get(API_URL, (res) => {
        let data = '';
        
        res.on('data', (chunk) => {
            data += chunk;
        });
        
        res.on('end', () => {
            try {
                const apiData = JSON.parse(data);
                console.log('✅ API data received successfully');
                
                // Simulate face recognition
                const recognizedUser = 'Andii';
                console.log(`\n2. Face recognized as: ${recognizedUser}`);
                
                // Find user data
                const user = apiData.users.find(u => 
                    u.name.toLowerCase() === recognizedUser.toLowerCase()
                );
                
                if (user) {
                    console.log(`✅ User found: ${user.name}`);
                    console.log(`📊 Events: ${user.events.length}, Lists: ${user.lists.length}`);
                    
                    // Simulate personalapi module
                    console.log('\n3. Personal API Module:');
                    console.log(`   Events: ${user.events.map(e => e.title).join(', ')}`);
                    console.log(`   Lists: ${user.lists.map(l => l.title).join(', ')}`);
                    
                    // Simulate personalcalendar module
                    console.log('\n4. Personal Calendar Module:');
                    if (user.events.length > 0) {
                        user.events.forEach(event => {
                            const date = new Date(event.startDate);
                            const isAllDay = event.allDay ? ' (All Day)' : '';
                            console.log(`   📅 ${event.title} - ${date.toLocaleDateString()}${isAllDay}`);
                        });
                    } else {
                        console.log('   ❌ No events found');
                    }
                    
                    // Simulate personaltodo module
                    console.log('\n5. Personal Todo Module:');
                    if (user.lists.length > 0) {
                        user.lists.forEach(list => {
                            console.log(`   📋 ${list.title}:`);
                            if (list.items) {
                                list.items.forEach(item => {
                                    const status = item.completed ? '✅' : '☐';
                                    console.log(`      ${status} ${item.title}`);
                                });
                            }
                        });
                    } else {
                        console.log('   ❌ No todo lists found');
                    }
                    
                } else {
                    console.log(`❌ User ${recognizedUser} not found in API data`);
                    console.log('Available users:', apiData.users.map(u => u.name));
                }
                
                console.log('\n✅ Data flow simulation completed!');
                console.log('🎯 If this looks correct, the issue might be in the module communication.');
                
            } catch (error) {
                console.error('❌ Error parsing API response:', error.message);
            }
        });
        
    }).on('error', (error) => {
        console.error('❌ Error fetching API data:', error.message);
    });
}

simulateDataFlow();
