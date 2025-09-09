#!/usr/bin/env node
/**
 * Debug script to test MagicMirror module communication
 * This will help identify where the data flow is breaking
 */

const https = require('https');

const API_URL = 'https://calendar-app-production-6d2d.up.railway.app/api/magic-mirror/future-data';

console.log('🔍 Debug MagicMirror Data Flow');
console.log('='.repeat(50));

// Test 1: API Connection
console.log('1. Testing API Connection...');
https.get(API_URL, (res) => {
    let data = '';
    
    res.on('data', (chunk) => {
        data += chunk;
    });
    
    res.on('end', () => {
        try {
            const apiData = JSON.parse(data);
            console.log('✅ API Connection: SUCCESS');
            console.log(`   Users: ${apiData.users.length}`);
            console.log(`   Events: ${apiData.summary.totalEvents}`);
            console.log(`   Lists: ${apiData.summary.totalLists}`);
            
            // Test 2: User Data Extraction
            console.log('\n2. Testing User Data Extraction...');
            const user = apiData.users.find(u => u.name.toLowerCase() === 'andii');
            
            if (user) {
                console.log('✅ User Found: Andii');
                console.log(`   Events: ${user.events.length}`);
                console.log(`   Lists: ${user.lists.length}`);
                
                // Test 3: Event Processing
                console.log('\n3. Testing Event Processing...');
                if (user.events.length > 0) {
                    console.log('✅ Events Processing: SUCCESS');
                    user.events.forEach((event, index) => {
                        console.log(`   Event ${index + 1}: ${event.title}`);
                        console.log(`     - All Day: ${event.allDay}`);
                        console.log(`     - Date: ${event.startDate}`);
                        console.log(`     - Color: ${event.color}`);
                    });
                } else {
                    console.log('❌ Events Processing: FAILED - No events found');
                }
                
                // Test 4: Todo Processing
                console.log('\n4. Testing Todo Processing...');
                if (user.lists.length > 0) {
                    console.log('✅ Todo Processing: SUCCESS');
                    user.lists.forEach((list, index) => {
                        console.log(`   List ${index + 1}: ${list.title}`);
                        if (list.items && list.items.length > 0) {
                            list.items.forEach((item, itemIndex) => {
                                console.log(`     Item ${itemIndex + 1}: ${item.title} (${item.completed ? 'completed' : 'pending'})`);
                            });
                        } else {
                            console.log('     ❌ No items in list');
                        }
                    });
                } else {
                    console.log('❌ Todo Processing: FAILED - No lists found');
                }
                
                // Test 5: Data Structure Validation
                console.log('\n5. Testing Data Structure Validation...');
                const events = user.events || [];
                const lists = user.lists || [];
                
                console.log(`   Events array length: ${events.length}`);
                console.log(`   Lists array length: ${lists.length}`);
                
                if (events.length > 0) {
                    console.log('   ✅ Events structure is valid');
                } else {
                    console.log('   ❌ Events structure is invalid or empty');
                }
                
                if (lists.length > 0) {
                    console.log('   ✅ Lists structure is valid');
                } else {
                    console.log('   ❌ Lists structure is invalid or empty');
                }
                
                // Test 6: Module Data Format
                console.log('\n6. Testing Module Data Format...');
                const moduleData = {
                    user: 'Andii',
                    events: events,
                    lists: lists
                };
                
                console.log('   Module data structure:');
                console.log(`     - User: ${moduleData.user}`);
                console.log(`     - Events: ${moduleData.events.length} items`);
                console.log(`     - Lists: ${moduleData.lists.length} items`);
                
                // Test 7: Todo Items Flattening
                console.log('\n7. Testing Todo Items Flattening...');
                const todoItems = [];
                if (lists.length > 0) {
                    lists.forEach(list => {
                        if (list.items) {
                            list.items.forEach(item => {
                                todoItems.push({
                                    title: item.title,
                                    completed: item.completed,
                                    listTitle: list.title
                                });
                            });
                        }
                    });
                }
                
                console.log(`   Flattened todo items: ${todoItems.length}`);
                if (todoItems.length > 0) {
                    console.log('   ✅ Todo flattening: SUCCESS');
                    todoItems.forEach((item, index) => {
                        console.log(`     ${index + 1}. ${item.title} (${item.listTitle})`);
                    });
                } else {
                    console.log('   ❌ Todo flattening: FAILED - No items');
                }
                
                console.log('\n✅ All tests completed!');
                console.log('🎯 If all tests pass, the issue is in module communication timing.');
                
            } else {
                console.log('❌ User Found: FAILED - Andii not found');
                console.log('   Available users:', apiData.users.map(u => u.name));
            }
            
        } catch (error) {
            console.error('❌ API Data Parsing: FAILED', error.message);
        }
    });
    
}).on('error', (error) => {
    console.error('❌ API Connection: FAILED', error.message);
});
