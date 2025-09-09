#!/usr/bin/env node
/**
 * Test script to simulate the data flow between modules
 */

console.log('🧪 Testing Data Flow Between Modules');
console.log('=' * 50);

// Simulate the API data
const apiData = {
    "message": "Future events and lists (today and beyond)",
    "date": "2025-09-09",
    "users": [{
        "name": "Andii",
        "events": [
            {
                "_id": "68bfff568ea84e6d9cde98b2",
                "title": "Bagsh uulzalt",
                "description": "Diplom sedev songolt\n10am",
                "color": "#8b5cf6",
                "allDay": true,
                "startDate": "2025-09-09T16:00:00.000Z"
            },
            {
                "_id": "68ba8c5d8ea84e6d9cde97be",
                "title": "hi",
                "description": "",
                "color": "#3b82f6",
                "allDay": true,
                "startDate": "2025-09-10T16:00:00.000Z"
            }
        ],
        "lists": [{
            "_id": "68ba8cb48ea84e6d9cde97db",
            "title": "Work must finish",
            "description": "",
            "listDate": "2025-09-09T00:00:00.000Z",
            "items": [
                {
                    "_id": "68ba8cc08ea84e6d9cde97e1",
                    "title": "Finish osh.gov.mn",
                    "description": "",
                    "completed": false
                },
                {
                    "_id": "68ba8ccb8ea84e6d9cde97e9",
                    "title": "Add Media Cosmos.tech.mn",
                    "description": "",
                    "completed": false
                }
            ]
        }]
    }],
    "summary": {
        "totalUsers": 1,
        "totalEvents": 2,
        "totalLists": 1
    }
};

// Simulate face recognition
const recognizedUser = "Andii";
console.log(`1. Face recognized as: ${recognizedUser}`);

// Simulate personalapi module
console.log('\n2. Personal API Module:');
const user = apiData.users.find(u => 
    u.name.toLowerCase() === recognizedUser.toLowerCase()
);

if (user) {
    console.log(`✅ User found: ${user.name}`);
    console.log(`📊 Events: ${user.events.length}, Lists: ${user.lists.length}`);
    
    // Simulate loadUserData function
    const events = user.events || [];
    const lists = user.lists || [];
    
    console.log(`   Events: ${events.map(e => e.title).join(', ')}`);
    console.log(`   Lists: ${lists.map(l => l.title).join(', ')}`);
    
    // Simulate sending USER_DATA_LOADED notification
    const userDataPayload = {
        user: recognizedUser,
        events: events,
        lists: lists
    };
    
    console.log('\n3. Sending USER_DATA_LOADED notification...');
    console.log('   Payload:', JSON.stringify(userDataPayload, null, 2));
    
    // Simulate personalcalendar module
    console.log('\n4. Personal Calendar Module:');
    if (userDataPayload.user === recognizedUser) {
        const calendarEvents = userDataPayload.events || [];
        console.log(`   ✅ Loaded ${calendarEvents.length} events for ${recognizedUser}`);
        calendarEvents.forEach(event => {
            const date = new Date(event.startDate);
            const isAllDay = event.allDay ? ' (All Day)' : '';
            console.log(`   📅 ${event.title} - ${date.toLocaleDateString()}${isAllDay}`);
        });
    } else {
        console.log('   ❌ User mismatch');
    }
    
    // Simulate personaltodo module
    console.log('\n5. Personal Todo Module:');
    if (userDataPayload.user === recognizedUser) {
        const todoItems = [];
        if (userDataPayload.lists) {
            userDataPayload.lists.forEach(list => {
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
        console.log(`   ✅ Loaded ${todoItems.length} items for ${recognizedUser}`);
        todoItems.forEach(item => {
            const status = item.completed ? '✅' : '☐';
            console.log(`   ${status} ${item.title} (${item.listTitle})`);
        });
    } else {
        console.log('   ❌ User mismatch');
    }
    
} else {
    console.log(`❌ User ${recognizedUser} not found in API data`);
}

console.log('\n✅ Data flow test completed!');
console.log('🎯 If this looks correct, the issue might be in the module communication or timing.');
