#!/usr/bin/env node

/**
 * Test script for Mongolian Holidays API
 * Tests the Nager.Date API for Mongolian holidays
 */

const fetch = require('node-fetch');

async function testMongolianHolidays() {
    console.log('🇲🇳 Testing Mongolian Holidays API...');
    console.log('=====================================');
    
    const currentYear = new Date().getFullYear();
    const apiUrl = `https://date.nager.at/api/v3/PublicHolidays/${currentYear}/MN`;
    
    try {
        console.log(`📡 Fetching holidays for ${currentYear}...`);
        console.log(`🔗 API URL: ${apiUrl}`);
        
        const response = await fetch(apiUrl);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const holidays = await response.json();
        
        console.log(`✅ Successfully fetched ${holidays.length} holidays for ${currentYear}`);
        console.log('');
        
        // Display holidays
        console.log('📅 Mongolian Holidays:');
        console.log('---------------------');
        
        holidays.forEach((holiday, index) => {
            const date = new Date(holiday.date);
            const formattedDate = date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                weekday: 'long'
            });
            
            console.log(`${index + 1}. ${holiday.localName}`);
            console.log(`   English: ${holiday.name}`);
            console.log(`   Date: ${formattedDate}`);
            console.log(`   Type: ${holiday.types ? holiday.types.join(', ') : 'Public'}`);
            console.log('');
        });
        
        // Test next year as well
        const nextYear = currentYear + 1;
        const nextYearUrl = `https://date.nager.at/api/v3/PublicHolidays/${nextYear}/MN`;
        
        console.log(`📡 Testing ${nextYear} holidays...`);
        const nextYearResponse = await fetch(nextYearUrl);
        
        if (nextYearResponse.ok) {
            const nextYearHolidays = await nextYearResponse.json();
            console.log(`✅ ${nextYear} holidays also available (${nextYearHolidays.length} holidays)`);
        } else {
            console.log(`⚠️  ${nextYear} holidays not yet available`);
        }
        
        console.log('');
        console.log('🎉 API test completed successfully!');
        console.log('💡 The new mongolianholidays module should work correctly.');
        
    } catch (error) {
        console.error('❌ Error testing API:', error.message);
        console.log('');
        console.log('🔧 Troubleshooting:');
        console.log('   - Check your internet connection');
        console.log('   - Verify the API URL is accessible');
        console.log('   - Check if the API service is running');
        process.exit(1);
    }
}

// Run the test
testMongolianHolidays();
