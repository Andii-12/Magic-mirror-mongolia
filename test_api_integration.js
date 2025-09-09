#!/usr/bin/env node
/**
 * Test script to verify API integration
 * This tests the API endpoint and data format
 */

const https = require('https');

const API_URL = 'https://calendar-app-production-6d2d.up.railway.app/api/magic-mirror/future-data';

console.log('🧪 Testing API Integration');
console.log('=' * 50);

https.get(API_URL, (res) => {
    let data = '';
    
    res.on('data', (chunk) => {
        data += chunk;
    });
    
    res.on('end', () => {
        try {
            const apiData = JSON.parse(data);
            console.log('✅ API Response received successfully');
            console.log(`📊 Summary: ${apiData.summary.totalUsers} users, ${apiData.summary.totalEvents} events, ${apiData.summary.totalLists} lists`);
            
            console.log('\n👤 Users found:');
            apiData.users.forEach(user => {
                console.log(`  - ${user.name}: ${user.events.length} events, ${user.lists.length} lists`);
                
                if (user.events.length > 0) {
                    console.log('    📅 Events:');
                    user.events.forEach(event => {
                        console.log(`      • ${event.title} (${event.startDate})`);
                    });
                }
                
                if (user.lists.length > 0) {
                    console.log('    📋 Todo Lists:');
                    user.lists.forEach(list => {
                        console.log(`      • ${list.title}: ${list.items.length} items`);
                        list.items.forEach(item => {
                            console.log(`        - ${item.title} (${item.completed ? 'completed' : 'pending'})`);
                        });
                    });
                }
            });
            
            console.log('\n✅ API integration test completed successfully!');
            console.log('🎯 The personal data modules should now show this real data when a face is recognized.');
            
        } catch (error) {
            console.error('❌ Error parsing API response:', error.message);
        }
    });
    
}).on('error', (error) => {
    console.error('❌ Error fetching API data:', error.message);
});
