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
		this.lastSent = null; // throttle duplicate updates
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
		
		// Faster polling for lower UI latency
		if (this.watchTimer) {
			clearInterval(this.watchTimer);
		}
		this.watchTimer = setInterval(() => {
			self.readStatusFile();
		}, 150);
	},

	// Read status from file
	readStatusFile: function() {
		if (!this.statusFile || !fs.existsSync(this.statusFile)) {
			// File doesn't exist, send default status
			const payload = {
				distance: 999,
				person: null,
				active: false,
				status: "waiting",
				timestamp: Date.now()
			};
			this._maybeSend(payload);
			return;
		}

		try {
			const data = fs.readFileSync(this.statusFile, 'utf8');
			const status = JSON.parse(data);
			
			// Only log when status changes significantly or every 10 reads
			if (!this.lastStatus || 
				this.lastStatus.person !== status.person || 
				this.lastStatus.active !== status.active ||
				(this.readCount && this.readCount % 10 === 0)) {
				console.log("Face Recognition Node Helper: Status update:", {
					distance: status.distance,
					person: status.person,
					active: status.active,
					status: status.status
				});
				this.lastStatus = { ...status };
			}
			
			// Increment read count
			this.readCount = (this.readCount || 0) + 1;
			
			// Build payload (pass through additional fields if present)
			const payload = {
				distance: status.distance || 999,
				person: status.person || null,
				active: status.active || false,
				status: status.status || "waiting",
				confidence: status.confidence || 0,
				recognition_image: status.recognition_image || null,
				log_messages: status.log_messages || [],
				timestamp: status.timestamp || Date.now()
			};
			// Throttle duplicate updates to prevent flicker
			this._maybeSend(payload);
		} catch (error) {
			console.log("Error reading face status file:", error.message);
			// Send default status on error
			const payload = {
				distance: 999,
				person: null,
				active: false,
				status: "waiting",
				timestamp: Date.now()
			};
			this._maybeSend(payload);
		}
	},

	// Only send if meaningful change occurred
	_maybeSend: function(payload) {
		const last = this.lastSent;
		const significantDistanceChange = !last || Math.abs((payload.distance || 0) - (last.distance || 0)) > 5;
		const logMessagesChanged = !last || JSON.stringify(last.log_messages || []) !== JSON.stringify(payload.log_messages || []);
		// Check if image changed (handle null/undefined/string comparisons)
		const lastImage = last ? last.recognition_image : null;
		const currentImage = payload.recognition_image || null;
		const imageChanged = lastImage !== currentImage;
		const confidenceChanged = !last || Math.abs((last.confidence || 0) - (payload.confidence || 0)) > 1;
		let changed =
			!last ||
			last.person !== payload.person ||
			last.active !== payload.active ||
			last.status !== payload.status ||
			significantDistanceChange ||
			logMessagesChanged ||
			imageChanged ||
			confidenceChanged;
		
		// Always send if person is recognized and image is available
		if (payload.person && payload.person !== "Unknown" && currentImage) {
			if (!last || !last.recognition_image) {
				changed = true; // Force send if person recognized but image wasn't sent before
			}
		}
		if (changed) {
			this.lastSent = { ...payload };
			this.sendSocketNotification("FACE_STATUS_UPDATE", payload);
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
