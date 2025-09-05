/* global Module, Log, moment */

Module.register("facerecognition", {
	// Default module config.
	defaults: {
		updateInterval: 1000, // Check for updates every 1 second
		proximityThreshold: 20, // 20 cm threshold
		timeoutDelay: 10000, // 10 seconds delay before shutdown
		greetingDuration: 5000, // Show greeting for 5 seconds
		pythonScriptPath: "/home/pi/face_recognition_system.py", // Path to your Python script
		apiEndpoint: "http://localhost:5000", // If using Flask API
		useAPI: false, // Set to true if using Flask API instead of file communication
		statusFile: "/tmp/magicmirror_face_status.json", // Status file for communication
		greetingStyle: "large bright", // CSS classes for greeting display
		showDistance: true, // Show current distance
		showStatus: true, // Show recognition status
		animationSpeed: 1000, // Animation speed for greetings
		// Personalized greetings for different people
						greetings: {
					"default": "Тавтай Морил {name}!",
					"unknown": "Таныг танихгүй байна",
					// Add specific greetings for known people
					// "John": "Тавтай Морил John!",
					// "Jane": "Тавтай Морил Jane!"
				}
	},

	// Define required scripts.
	getScripts: function() {
		return ["moment.js"];
	},

	// Define start sequence.
	start: function() {
		console.log("Starting Face Recognition module: " + this.name);

		// Set locale.
		moment.locale(config.language);

		this.currentPerson = null;
		this.currentDistance = 0;
		this.isActive = false;
		this.lastDetectionTime = null;
		this.greetingTimer = null;
		this.shutdownTimer = null;
		this.statusCheckTimer = null;

		this.startStatusChecking();
	},

	// Start checking for status updates from Python script
	startStatusChecking: function() {
		const self = this;
		this.statusCheckTimer = setInterval(function() {
			self.checkStatus();
		}, this.config.updateInterval);
	},

	// Check status from Python script
	checkStatus: function() {
		if (this.config.useAPI) {
			this.checkStatusViaAPI();
		} else {
			this.checkStatusViaFile();
		}
	},

	// Check status via Flask API
	checkStatusViaAPI: function() {
		const self = this;
		fetch(`${this.config.apiEndpoint}/status`)
			.then(response => response.json())
			.then(data => {
				self.processStatusData(data);
			})
			.catch(error => {
				console.log("Face recognition API not available:", error);
			});
	},

	// Check status via file communication
	checkStatusViaFile: function() {
		const self = this;
		// This would require a node_helper to read files
		this.sendSocketNotification("CHECK_FACE_STATUS", {
			statusFile: this.config.statusFile
		});
	},

	// Process status data from Python script
	processStatusData: function(data) {
		const previousPerson = this.currentPerson;
		const previousDistance = this.currentDistance;
		const previousActive = this.isActive;

		this.currentDistance = data.distance || 0;
		this.currentPerson = data.person || null;
		this.isActive = data.active || false;

		// Handle proximity detection
		if (this.currentDistance < this.config.proximityThreshold) {
			// Object detected within threshold
			if (!previousActive) {
				console.log("Object detected within", this.config.proximityThreshold, "cm");
				this.onProximityDetected();
			}

			// Handle face recognition
			if (this.currentPerson && this.currentPerson !== previousPerson) {
				console.log("Face recognized:", this.currentPerson);
				this.onFaceRecognized(this.currentPerson);
			}
		} else {
			// Object moved away
			if (previousActive) {
				console.log("Object moved away, starting shutdown timer");
				this.onProximityLost();
			}
		}

		// Update display
		this.updateDom(this.config.animationSpeed);
	},

	// Handle proximity detected
	onProximityDetected: function() {
		this.isActive = true;
		this.lastDetectionTime = Date.now();
		
		// Clear any existing shutdown timer
		if (this.shutdownTimer) {
			clearTimeout(this.shutdownTimer);
			this.shutdownTimer = null;
		}

		// Send notification to wake up MagicMirror
		this.sendNotification("PROXIMITY_DETECTED", {
			distance: this.currentDistance
		});
	},

	// Handle face recognized
	onFaceRecognized: function(personName) {
		this.currentPerson = personName;
		
		// Clear any existing greeting timer
		if (this.greetingTimer) {
			clearTimeout(this.greetingTimer);
		}

		// Show greeting for specified duration
		this.greetingTimer = setTimeout(() => {
			this.currentPerson = null; // Hide greeting after duration
			this.updateDom(this.config.animationSpeed);
		}, this.config.greetingDuration);

		// Send notification about face recognition
		this.sendNotification("FACE_RECOGNIZED", {
			person: personName,
			distance: this.currentDistance
		});

		this.updateDom(this.config.animationSpeed);
	},

	// Handle proximity lost
	onProximityLost: function() {
		this.isActive = false;
		this.currentPerson = null;

		// Start shutdown timer
		const self = this;
		this.shutdownTimer = setTimeout(() => {
			console.log("Shutting down MagicMirror after timeout");
			self.sendNotification("SHUTDOWN_MAGICMIRROR", {
				reason: "proximity_timeout"
			});
		}, this.config.timeoutDelay);

		// Send notification about proximity lost
		this.sendNotification("PROXIMITY_LOST", {
			distance: this.currentDistance
		});

		this.updateDom(this.config.animationSpeed);
	},

	// Override socket notification handler.
	socketNotificationReceived: function(notification, payload) {
		if (notification === "FACE_STATUS_UPDATE") {
			this.processStatusData(payload);
			// Broadcast the status update to all modules
			this.sendNotification("FACE_STATUS_UPDATE", payload);
		}
	},

	// Override dom generator.
	getDom: function() {
		const wrapper = document.createElement("div");
		wrapper.className = "facerecognition";

		// Show greeting if person is recognized
		if (this.currentPerson && this.currentPerson !== "Unknown") {
			const greetingElement = document.createElement("div");
			greetingElement.className = `greeting ${this.config.greetingStyle}`;
			
			// Create personalized greeting
			let greetingText;
			if (this.config.greetings[this.currentPerson]) {
				greetingText = this.config.greetings[this.currentPerson];
			} else {
				greetingText = this.config.greetings.default.replace("{name}", this.currentPerson);
			}
			
			greetingElement.innerHTML = greetingText;
			wrapper.appendChild(greetingElement);
		}

		return wrapper;
	},

	// Override suspend method.
	suspend: function() {
		if (this.statusCheckTimer) {
			clearInterval(this.statusCheckTimer);
			this.statusCheckTimer = null;
		}
		if (this.greetingTimer) {
			clearTimeout(this.greetingTimer);
			this.greetingTimer = null;
		}
		if (this.shutdownTimer) {
			clearTimeout(this.shutdownTimer);
			this.shutdownTimer = null;
		}
	},

	// Override resume method.
	resume: function() {
		this.startStatusChecking();
	}
});
