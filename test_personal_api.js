#!/usr/bin/env node

/**
 * Test script for Personal API integration
 * Tests the API endpoint and displays the data structure
 */

// Using built-in fetch (Node.js 18+)

const API_URL = "https://calendar-app-production-6d2d.up.railway.app/api/magic-mirror/future-data";

async function testPersonalAPI() {
    console.log("🧪 Testing Personal API Integration");
    console.log("=====================================");
    console.log(`📡 API URL: ${API_URL}`);
    console.log("");

    try {
        console.log("⏳ Fetching data...");
        const response = await fetch(API_URL);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        console.log("✅ API Response received successfully!");
        console.log("");
        
        // Display summary
        console.log("📊 Summary:");
        console.log(`   - Total Users: ${data.summary.totalUsers}`);
        console.log(`   - Total Events: ${data.summary.totalEvents}`);
        console.log(`   - Total Lists: ${data.summary.totalLists}`);
        console.log(`   - Date: ${data.date}`);
        console.log("");
        
        // Display users and their data
        console.log("👥 Users and their data:");
        data.users.forEach((user, index) => {
            console.log(`\n${index + 1}. ${user.name}:`);
            console.log(`   📅 Events (${user.events.length}):`);
            user.events.forEach((event, eventIndex) => {
                console.log(`      ${eventIndex + 1}. ${event.title}`);
                console.log(`         - Date: ${event.startDate}`);
                console.log(`         - All Day: ${event.allDay}`);
                console.log(`         - Color: ${event.color}`);
                if (event.description) {
                    console.log(`         - Description: ${event.description}`);
                }
            });
            
            console.log(`   📋 Todo Lists (${user.lists.length}):`);
            user.lists.forEach((list, listIndex) => {
                console.log(`      ${listIndex + 1}. ${list.title}`);
                console.log(`         - Date: ${list.listDate}`);
                if (list.description) {
                    console.log(`         - Description: ${list.description}`);
                }
                console.log(`         - Items (${list.items.length}):`);
                list.items.forEach((item, itemIndex) => {
                    const status = item.completed ? "✅" : "☐";
                    console.log(`            ${itemIndex + 1}. ${status} ${item.title}`);
                    if (item.description) {
                        console.log(`               - ${item.description}`);
                    }
                });
            });
        });
        
        console.log("\n🎉 Test completed successfully!");
        console.log("\n💡 Integration notes:");
        console.log("   - The module will match user names from face recognition");
        console.log("   - Only data for the recognized user will be displayed");
        console.log("   - Events and todos will be shown in the middle_center position");
        console.log("   - Data updates every 5 minutes");
        
    } catch (error) {
        console.error("❌ Test failed:");
        console.error(`   Error: ${error.message}`);
        console.error("");
        console.error("🔧 Troubleshooting:");
        console.error("   - Check if the API URL is correct");
        console.error("   - Verify internet connection");
        console.error("   - Check if the API server is running");
        process.exit(1);
    }
}

// Run the test
testPersonalAPI();
