#!/usr/bin/env node
/**
 * Test script to verify today's tasks functionality
 */

const moment = require('moment');

// Mock the getTodayTasks function logic
function getTodayTasks() {
    // Sample data from user_profiles.json
    const lists = [{
        title: "Personal Tasks",
        listDate: "2024-12-19", // Today's date
        items: [
            {
                title: "Цаг агаарыг шалгах",
                completed: false,
                date: "2024-12-19"
            },
            {
                title: "Мэдээ унших",
                completed: true,
                date: "2024-12-19"
            },
            {
                title: "Цагийн хуваарийг шалгах",
                completed: false,
                date: "2024-12-19"
            },
            {
                title: "Хоол хийх",
                completed: false,
                date: "2024-12-19"
            },
            {
                title: "Гэрээ цэвэрлэх",
                completed: false,
                date: "2024-12-19"
            },
            {
                title: "Ном унших",
                completed: false,
                date: "2024-12-19"
            }
        ]
    }];

    const today = moment().startOf('day');
    const todayTasks = [];

    // Process all lists to find today's tasks
    lists.forEach(list => {
        if (list.items && list.items.length > 0) {
            list.items.forEach(item => {
                // Check if task is for today based on list date or item date
                let taskDate = null;
                
                // Try to get date from list
                if (list.listDate) {
                    taskDate = moment(list.listDate).startOf('day');
                }
                // Try to get date from item
                else if (item.date) {
                    taskDate = moment(item.date).startOf('day');
                }
                // If no specific date, assume it's for today
                else {
                    taskDate = today;
                }

                // Add task if it's for today
                if (taskDate.isSame(today, 'day')) {
                    todayTasks.push({
                        title: item.title,
                        completed: item.completed || false,
                        date: taskDate.format('YYYY-MM-DD')
                    });
                }
            });
        }
    });

    // Sort tasks: incomplete first, then completed
    todayTasks.sort((a, b) => {
        if (a.completed === b.completed) return 0;
        return a.completed ? 1 : -1;
    });

    return todayTasks;
}

function testTodayTasks() {
    console.log("🧪 Testing Today's Tasks Functionality");
    console.log("=" * 50);
    console.log(`📅 Today's date: ${moment().format('YYYY-MM-DD')}`);
    
    const todayTasks = getTodayTasks();
    
    console.log(`\n📋 Found ${todayTasks.length} tasks for today:`);
    
    if (todayTasks.length === 0) {
        console.log("   ✅ Should show: 'Өнөөдөр хийх зүйлс байхгүй байна'");
    } else {
        console.log("   📝 Today's tasks (max 5 shown):");
        todayTasks.slice(0, 5).forEach((task, index) => {
            const status = task.completed ? '✅' : '⏳';
            console.log(`   ${index + 1}. ${status} ${task.title}`);
        });
        
        if (todayTasks.length > 5) {
            console.log(`   ... болон ${todayTasks.length - 5} даалгавар илүү`);
        }
    }
    
    console.log("\n✅ Test completed!");
}

testTodayTasks();
