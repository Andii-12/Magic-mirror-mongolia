/* global Module, Log, moment */

Module.register("facerecognitionoverlay", {
	// Default module config.
	defaults: {
		updateInterval: 500, // Check for updates every 500ms
		statusFile: "/tmp/magicmirror_face_status.json",
		showFaceIcon: false,
		showRecognitionStatus: true,
		faceIconSize: "large", // small, medium, large
		animationSpeed: 1000,
		// Face icon styles
		faceIconStyle: "pulse", // pulse, rotate, bounce
		// Recognition status messages
		messages: {
			detecting: "Царай уншиж байна",
			recognized: "Тавтай Морил",
			unknown: "Таныг танихгүй байна",
			waiting: "Ойртож зогсоорой"
		}
	},

	// Define start sequence.
	start: function() {
		console.log("Starting Face Recognition Overlay module: " + this.name);

		this.currentStatus = "waiting";
		this.currentPerson = null;
		this.isActive = false;
		this.recognitionTimer = null;
		this.statusCheckTimer = null;

		this.startStatusChecking();
	},

	// Start checking for status updates
	startStatusChecking: function() {
		const self = this;
		this.statusCheckTimer = setInterval(function() {
			self.checkStatus();
		}, this.config.updateInterval);
	},

	// Check status from Python script
	checkStatus: function() {
		this.sendSocketNotification("CHECK_FACE_STATUS", {
			statusFile: this.config.statusFile
		});
	},

	// Process status data from Python script
	processStatusData: function(data) {
		const previousStatus = this.currentStatus;
		const previousPerson = this.currentPerson;
		const previousActive = this.isActive;

		this.isActive = data.active || false;
		this.currentPerson = data.person || null;

		// Determine current status
		if (this.isActive) {
			if (this.currentPerson && this.currentPerson !== "Unknown") {
				this.currentStatus = "recognized";
			} else if (this.currentPerson === "Unknown") {
				this.currentStatus = "unknown";
			} else {
				this.currentStatus = "detecting";
			}
		} else {
			this.currentStatus = "waiting";
		}

		// Update display if status changed
		if (this.currentStatus !== previousStatus || this.currentPerson !== previousPerson) {
			this.updateDom(this.config.animationSpeed);
		}
	},

	// Override socket notification handler.
	socketNotificationReceived: function(notification, payload) {
		if (notification === "FACE_STATUS_UPDATE") {
			this.processStatusData(payload);
		}
	},

	// Override dom generator.
	getDom: function() {
		const wrapper = document.createElement("div");
		wrapper.className = "facerecognitionoverlay";

		// Always show overlay - blank black screen when not active
		if (!this.isActive) {
			// Show waiting message on blank screen
			if (this.config.showRecognitionStatus) {
				const statusElement = document.createElement("div");
				statusElement.className = "recognition-status";
				statusElement.innerHTML = this.config.messages.waiting;
				wrapper.appendChild(statusElement);
			}
			return wrapper;
		}

		// Show recognition status when active
		if (this.config.showRecognitionStatus) {
			const statusElement = document.createElement("div");
			statusElement.className = "recognition-status";
			
			let statusText = this.config.messages[this.currentStatus] || this.config.messages.waiting;
			
			// Show personalized greeting when recognized
			if (this.currentStatus === "recognized" && this.currentPerson && this.currentPerson !== "Unknown") {
				statusText = `${this.config.messages.recognized} ${this.currentPerson}`;
			}
			
			statusElement.innerHTML = statusText;
			wrapper.appendChild(statusElement);
		}

		return wrapper;
	},

	// Override suspend method.
	suspend: function() {
		if (this.statusCheckTimer) {
			clearInterval(this.statusCheckTimer);
			this.statusCheckTimer = null;
		}
		if (this.recognitionTimer) {
			clearTimeout(this.recognitionTimer);
			this.recognitionTimer = null;
		}
	},

	// Override resume method.
	resume: function() {
		this.startStatusChecking();
	}
});
