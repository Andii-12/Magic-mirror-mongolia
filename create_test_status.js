const fs = require('fs');

const testStatus = {
    distance: 15,
    person: "Andii",
    active: true,
    status: "recognized",
    timestamp: new Date().toISOString()
};

const statusFile = "C:\\tmp\\magicmirror_face_status.json";

try {
    fs.writeFileSync(statusFile, JSON.stringify(testStatus, null, 2));
    console.log("✅ Test status file created successfully");
    console.log("📊 Content:");
    console.log(JSON.stringify(testStatus, null, 2));
} catch (error) {
    console.error("❌ Error creating status file:", error.message);
}
