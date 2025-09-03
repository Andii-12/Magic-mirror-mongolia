#!/usr/bin/env node

/**
 * Script to fetch Mongolian holidays from Calendarific API and generate iCal file
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

const API_URL = 'https://calendarific.com/api/v2/holidays?&api_key=VhaBu1hTpO9OtGRyFbPUxY6vhO2nrqbL&country=MN&year=2025';
const OUTPUT_FILE = path.join(__dirname, '..', 'calendars', 'mongolian-holidays-api.ics');

// Mongolian translations for holiday names
const holidayTranslations = {
    'New Year': 'Шинэ жилийн өдөр',
    'Constitution Day': 'Үндсэн хуулийн өдөр',
    'Valentine\'s Day': 'Валентины өдөр',
    'Tsagaan Sar': 'Шинэ жилийн баяр (Цагаан сар)',
    'Patriots\' Day': 'Эх орончдын өдөр',
    'International Women\'s Day': 'Олон улсын эмэгтэйчүүдийн өдөр',
    'Soldiers\' Day': 'Цэргийн баатар, хамгаалагчдын өдөр',
    'Health Day': 'Эрүүл мэндийн дэлхийн өдөр',
    'Intellectual Property Day': 'Оюуны өмчийн өдөр',
    'Family Day': 'Гэр бүлийн өдөр',
    'Children\'s Day': 'Хүүхдийн дэлхийн өдөр',
    'Great Buddha Day': 'Бурханы их өдөр',
    'Naadam Holiday': 'Наадам',
    'Youth\'s Day': 'Залуучуудын өдөр',
    'Repression Victims\' Day': 'Хэлмэгдүүлэлтийн хохирогчдын өдөр',
    'Elders\' Day': 'Ахмад настны өдөр',
    'Capital City Day': 'Нийслэл хотын өдөр',
    'Genghis Khan Day': 'Чингис хааны өдөр',
    'Republic\'s Day': 'Тусгаар тогтнолын өдөр',
    'Human Rights Day': 'Хүний эрхийн дэлхийн өдөр',
    'Independence Day': 'Тусгаар тогтнолын өдөр'
};

function fetchHolidays() {
    return new Promise((resolve, reject) => {
        https.get(API_URL, (res) => {
            let data = '';
            
            res.on('data', (chunk) => {
                data += chunk;
            });
            
            res.on('end', () => {
                try {
                    const jsonData = JSON.parse(data);
                    resolve(jsonData);
                } catch (error) {
                    reject(error);
                }
            });
        }).on('error', (error) => {
            reject(error);
        });
    });
}

function generateICal(holidays) {
    let ical = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//MagicMirror²//Mongolian Holidays API//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:Mongolian Holidays (API)
X-WR-CALDESC:Official holidays from Calendarific API

`;

    // Add a test event for today
    const today = new Date();
    const todayStr = today.toISOString().slice(0, 10).replace(/-/g, '');
    
    ical += `BEGIN:VEVENT
UID:test-today@magicmirror.builders
DTSTART;VALUE=DATE:${todayStr}
DTEND;VALUE=DATE:${todayStr}
SUMMARY:Өнөөдрийн тест (Today's Test)
DESCRIPTION:Test event for today to verify calendar loading
END:VEVENT

`;

    // Add a test event for tomorrow
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const tomorrowStr = tomorrow.toISOString().slice(0, 10).replace(/-/g, '');
    
    ical += `BEGIN:VEVENT
UID:test-tomorrow@magicmirror.builders
DTSTART;VALUE=DATE:${tomorrowStr}
DTEND;VALUE=DATE:${tomorrowStr}
SUMMARY:Маргаашийн тест (Tomorrow's Test)
DESCRIPTION:Test event for tomorrow
END:VEVENT

`;

    holidays.forEach((holiday, index) => {
        const date = holiday.date.iso;
        const name = holiday.name;
        const description = holiday.description;
        const mongolianName = holidayTranslations[name] || name;
        
        // Convert date from YYYY-MM-DD to YYYYMMDD
        const icalDate = date.replace(/-/g, '');
        
        ical += `BEGIN:VEVENT
UID:mongolian-${index}-${icalDate}@calendarific.com
DTSTART;VALUE=DATE:${icalDate}
DTEND;VALUE=DATE:${icalDate}
SUMMARY:${mongolianName}
DESCRIPTION:${description}
END:VEVENT

`;
    });

    ical += 'END:VCALENDAR';
    return ical;
}

async function updateHolidays() {
    try {
        console.log('🔄 Fetching Mongolian holidays from Calendarific API...');
        
        const data = await fetchHolidays();
        
        if (data.meta.code !== 200) {
            throw new Error(`API Error: ${data.meta.code}`);
        }
        
        const holidays = data.response.holidays;
        console.log(`✅ Fetched ${holidays.length} holidays`);
        
        // Filter for public holidays and observances only
        const importantHolidays = holidays.filter(holiday => 
            holiday.type.includes('National holiday') || 
            holiday.type.includes('Public Holiday') ||
            holiday.type.includes('Observance')
        );
        
        console.log(`📅 Filtered to ${importantHolidays.length} important holidays`);
        
        const icalContent = generateICal(importantHolidays);
        
        // Ensure calendars directory exists
        const calendarsDir = path.dirname(OUTPUT_FILE);
        if (!fs.existsSync(calendarsDir)) {
            fs.mkdirSync(calendarsDir, { recursive: true });
        }
        
        fs.writeFileSync(OUTPUT_FILE, icalContent, 'utf8');
        
        console.log(`✅ Generated iCal file: ${OUTPUT_FILE}`);
        console.log('📋 Sample holidays:');
        
        importantHolidays.slice(0, 5).forEach(holiday => {
            const mongolianName = holidayTranslations[holiday.name] || holiday.name;
            console.log(`   • ${mongolianName} - ${holiday.date.iso}`);
        });
        
        console.log('\n🎉 Mongolian holidays calendar updated successfully!');
        
    } catch (error) {
        console.error('❌ Error updating holidays:', error.message);
        process.exit(1);
    }
}

// Run the update
updateHolidays();
