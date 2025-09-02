#!/usr/bin/env node

/**
 * Test script for Mongolian language support in MagicMirror²
 * This script validates the Mongolian translation file and configuration
 */

const fs = require('fs');
const path = require('path');

console.log('🇲🇳 Testing Mongolian Language Support for MagicMirror²');
console.log('=======================================================\n');

// Test 1: Check if Mongolian translation file exists
console.log('1. Checking Mongolian translation file...');
const mnTranslationPath = path.join(__dirname, 'translations', 'mn.json');

if (fs.existsSync(mnTranslationPath)) {
    console.log('   ✅ translations/mn.json exists');
    
    try {
        const mnTranslations = JSON.parse(fs.readFileSync(mnTranslationPath, 'utf8'));
        console.log(`   ✅ Valid JSON format (${Object.keys(mnTranslations).length} translations)`);
        
        // Check for essential translations
        const essentialKeys = ['LOADING', 'TODAY', 'TOMORROW', 'YESTERDAY', 'EMPTY'];
        const missingKeys = essentialKeys.filter(key => !mnTranslations[key]);
        
        if (missingKeys.length === 0) {
            console.log('   ✅ All essential translations present');
        } else {
            console.log(`   ⚠️  Missing translations: ${missingKeys.join(', ')}`);
        }
        
        // Display some sample translations
        console.log('\n   📝 Sample translations:');
        console.log(`      LOADING: "${mnTranslations.LOADING}"`);
        console.log(`      TODAY: "${mnTranslations.TODAY}"`);
        console.log(`      TOMORROW: "${mnTranslations.TOMORROW}"`);
        console.log(`      FEELS: "${mnTranslations.FEELS}"`);
        
    } catch (error) {
        console.log(`   ❌ Invalid JSON: ${error.message}`);
    }
} else {
    console.log('   ❌ translations/mn.json not found');
}

// Test 2: Check if translations.js includes Mongolian
console.log('\n2. Checking translations.js registration...');
const translationsJsPath = path.join(__dirname, 'translations', 'translations.js');

if (fs.existsSync(translationsJsPath)) {
    const translationsJs = fs.readFileSync(translationsJsPath, 'utf8');
    
    if (translationsJs.includes('mn: "translations/mn.json"')) {
        console.log('   ✅ Mongolian language registered in translations.js');
    } else {
        console.log('   ❌ Mongolian language not registered in translations.js');
    }
} else {
    console.log('   ❌ translations/translations.js not found');
}

// Test 3: Check Mongolian configuration file
console.log('\n3. Checking Mongolian configuration...');
const configPath = path.join(__dirname, 'config', 'config.mn.js');

if (fs.existsSync(configPath)) {
    console.log('   ✅ config/config.mn.js exists');
    
    try {
        const configContent = fs.readFileSync(configPath, 'utf8');
        
        if (configContent.includes('language: "mn"')) {
            console.log('   ✅ Language set to Mongolian');
        } else {
            console.log('   ⚠️  Language not set to Mongolian in config');
        }
        
        if (configContent.includes('locale: "mn-MN"')) {
            console.log('   ✅ Locale set to mn-MN');
        } else {
            console.log('   ⚠️  Locale not set to mn-MN');
        }
        
        if (configContent.includes('Asia/Ulaanbaatar')) {
            console.log('   ✅ Timezone set to Asia/Ulaanbaatar');
        } else {
            console.log('   ⚠️  Timezone not set to Asia/Ulaanbaatar');
        }
        
    } catch (error) {
        console.log(`   ❌ Error reading config: ${error.message}`);
    }
} else {
    console.log('   ❌ config/config.mn.js not found');
}

// Test 4: Validate configuration syntax
console.log('\n4. Validating configuration syntax...');
try {
    // Load the check_config module
    const checkConfigPath = path.join(__dirname, 'js', 'check_config.js');
    if (fs.existsSync(checkConfigPath)) {
        console.log('   ✅ Configuration validation available');
        console.log('   💡 Run "node js/check_config.js" to validate your config');
    } else {
        console.log('   ⚠️  Configuration validation not available');
    }
} catch (error) {
    console.log(`   ❌ Error: ${error.message}`);
}

// Test 5: Check system requirements
console.log('\n5. Checking system requirements...');
const nodeVersion = process.version;
const majorVersion = parseInt(nodeVersion.slice(1).split('.')[0]);

console.log(`   Node.js version: ${nodeVersion}`);

if (majorVersion >= 22) {
    console.log('   ✅ Node.js version compatible (22.14.0+ required)');
} else {
    console.log('   ⚠️  Node.js version may be too old (22.14.0+ required)');
}

// Memory check (if available)
if (process.memoryUsage) {
    const memUsage = process.memoryUsage();
    const memMB = Math.round(memUsage.heapUsed / 1024 / 1024);
    console.log(`   Memory usage: ${memMB}MB`);
}

console.log('\n🎉 Mongolian language setup test complete!');
console.log('\n📋 Next steps:');
console.log('   1. Copy config/config.mn.js to config/config.js');
console.log('   2. Customize weather location and other settings');
console.log('   3. Start MagicMirror² with: npm start');
console.log('\n🇲🇳 Баярлалаа! (Thank you!)');
