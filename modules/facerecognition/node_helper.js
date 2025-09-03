/* global NodeHelper */

const NodeHelper = require("node_helper");
const fs = require("fs");
const path = require("path");

module.exports = NodeHelper.create({
	// Override start method.
	start: function() {
		console.log("Starting node helper for: " + this.name);
		this.statusFile = null;
		this.watchTimer = null;
	},

	// Override socketNotificationReceived method.
	socketNotificationReceived: function(notification, payload) {
		if (notification === "CHECK_FACE_STATUS") {
			this.checkFaceStatus(payload);
		}
	},

	// Check face recognition status from file
	checkFaceStatus: function(payload) {
		const statusFile = payload.statusFile || "/tmp/magicmirror_face_status.json";
		
		// If this is a new file, start watching it
		if (this.statusFile !== statusFile) {
			this.statusFile = statusFile;
			this.startFileWatcher();
		}

		// Read current status
		this.readStatusFile();
	},

	// Start watching the status file for changes
	startFileWatcher: function() {
		const self = this;
		
		// Check file every 500ms
		this.watchTimer = setInterval(() => {
			self.readStatusFile();
		}, 500);
	},

	// Read status from file
	readStatusFile: function() {
		if (!this.statusFile || !fs.existsSync(this.statusFile)) {
			// File doesn't exist, send default status
			this.sendSocketNotification("FACE_STATUS_UPDATE", {
				distance: 999,
				person: null,
				active: false,
				timestamp: Date.now()
			});
			return;
		}

		try {
			const data = fs.readFileSync(this.statusFile, 'utf8');
			const status = JSON.parse(data);
			
			// Send status update to module
			this.sendSocketNotification("FACE_STATUS_UPDATE", {
				distance: status.distance || 999,
				person: status.person || null,
				active: status.active || false,
				timestamp: status.timestamp || Date.now()
			});
		} catch (error) {
			console.log("Error reading face status file:", error.message);
			// Send default status on error
			this.sendSocketNotification("FACE_STATUS_UPDATE", {
				distance: 999,
				person: null,
				active: false,
				timestamp: Date.now()
			});
		}
	},

	// Clean up on stop
	stop: function() {
		if (this.watchTimer) {
			clearInterval(this.watchTimer);
			this.watchTimer = null;
		}
	}
});
