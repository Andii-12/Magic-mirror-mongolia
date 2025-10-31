/* global Module, Log, moment */

Module.register("facerecognition", {
	// Default module config.
	defaults: {
		updateInterval: 500, // Faster status checks for lower latency
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
		animationSpeed: 0, // Disable animation to avoid blinking
		// Personalized greetings for different people
		greetings: {
			"default": "Тавтай морил {name}!",
			"unknown": "Таныг танихгүй байна",
			// Add specific greetings for known people
			// "John": "Тавтай морил John!",
			// "Jane": "Тавтай морил Jane!"
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

		this.lastRecognizedPerson = null;
		this.recognitionLocked = false;
		this.currentConfidence = 0;
		this.recognitionImage = null;
		this.eventLog = [];
		this.startStatusChecking();
	},

	// Append a message to the on-screen event log
	addLog: function(message) {
		try {
			const ts = new Date();
			const hh = ts.getHours().toString().padStart(2, '0');
			const mm = ts.getMinutes().toString().padStart(2, '0');
			const ss = ts.getSeconds().toString().padStart(2, '0');
			this.eventLog = this.eventLog || [];
			this.eventLog.unshift(`[${hh}:${mm}:${ss}] ${message}`);
			if (this.eventLog.length > 10) this.eventLog.pop();
		} catch (e) {
			// no-op
		}
	},

	// Start checking for status updates from Python script
	startStatusChecking: function() {
		const self = this;
		// Lower interval for faster reaction while still bounded
		const checkInterval = Math.max(this.config.updateInterval, 200); // At least 200ms
		this.statusCheckTimer = setInterval(function() {
			self.checkStatus();
		}, checkInterval);
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
		const previousActive = this.isActive;
		const previousStatus = this.currentStatus;

		// Trust backend status entirely to avoid UI oscillation
		this.currentDistance = data.distance || 0;
		this.currentPerson = (typeof data.person === "string" && data.person.length > 0) ? data.person : null;
		this.isActive = !!data.active;
		this.currentStatus = data.status || (this.isActive ? (this.currentPerson ? "recognized" : "detecting") : "waiting");
		
		// Store confidence and recognition image
		this.currentConfidence = data.confidence || 0;
		this.recognitionImage = data.recognition_image || null;
		
		// Fire recognition notification only on first recognition or person change
		if (this.currentPerson && this.currentPerson !== previousPerson) {
			console.log("[FACE RECOGNITION] Status update received:", {
				person: this.currentPerson,
				confidence: this.currentConfidence,
				image: this.recognitionImage,
				rawData: data
			});
			this.sendNotification("FACE_RECOGNIZED", {
				person: this.currentPerson,
				distance: this.currentDistance,
				confidence: this.currentConfidence,
				image: this.recognitionImage
			});
		}

		// Log meaningful state changes
		if (previousStatus !== this.currentStatus || previousPerson !== this.currentPerson) {
			const who = this.currentPerson ? this.currentPerson : (this.isActive ? "Unknown" : "-");
			const img = this.recognitionImage ? "img" : "no-img";
			this.addLog(`status=${this.currentStatus} person=${who} conf=${Math.round(this.currentConfidence)}% ${img}`);
		}

		// Update DOM when person/active/status/confidence/image changes
		if (previousPerson !== this.currentPerson || previousActive !== this.isActive || previousStatus !== this.currentStatus) {
			this.updateDom(this.config.animationSpeed);
		}
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
			this.greetingTimer = null;
		}

		// Don't set a timer to hide the greeting - keep it visible as long as proximity is detected
		// The greeting will only be cleared when proximity is lost

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

		// Show different messages based on backend-driven status
		// Keep greeting as long as person is recognized; otherwise show waiting/detecting messages
		if (this.currentPerson && this.currentPerson !== "Unknown") {
			// Create main status container
			const statusContainer = document.createElement("div");
			statusContainer.className = "facerecognition-recognition-container";
			
			// Add greeting text
			const greetingElement = document.createElement("div");
			greetingElement.className = "facerecognition-greeting-text";
			greetingElement.innerHTML = `Сайн уу, ${this.currentPerson}`;
			statusContainer.appendChild(greetingElement);
			
			// Add confidence percentage
			if (this.currentConfidence > 0) {
				const confidenceElement = document.createElement("div");
				confidenceElement.className = "facerecognition-confidence";
				confidenceElement.innerHTML = `${Math.round(this.currentConfidence)}%-ийн магадлалтай танигдлаа`;
				statusContainer.appendChild(confidenceElement);
			}
			
			// Add recognition image if available
			if (this.recognitionImage) {
				const imageElement = document.createElement("img");
				imageElement.className = "facerecognition-recognition-image";
				// Add timestamp to prevent caching
				const timestamp = new Date().getTime();
				imageElement.src = this.recognitionImage + "?t=" + timestamp;
				imageElement.alt = `Recognized: ${this.currentPerson}`;
				
				// Add error handler for debugging
				imageElement.onerror = function() {
					console.error("Failed to load recognition image:", this.src);
				};
				
				imageElement.onload = function() {
					console.log("Successfully loaded recognition image:", this.src);
				};
				
				statusContainer.appendChild(imageElement);
			}
			
			wrapper.appendChild(statusContainer);
		} else {
			// Not recognized yet: show waiting/detecting messages prominently
			const statusElement = document.createElement("div");
			statusElement.className = "facerecognition-status";
			let text = "Ойртож зогсоорой"; // default waiting
			if (this.currentStatus === "detecting" || (this.isActive && !this.currentPerson)) {
				text = "Царай уншиж байна";
			}
			statusElement.innerHTML = text;
			wrapper.appendChild(statusElement);

			// If a recent recognition image exists, show it under the status too
			if (this.recognitionImage) {
				const imageElement = document.createElement("img");
				imageElement.className = "facerecognition-recognition-image";
				const timestamp = new Date().getTime();
				imageElement.src = this.recognitionImage + "?t=" + timestamp;
				imageElement.alt = "Recognition preview";
				imageElement.onerror = function() {
					console.error("Failed to load recognition image:", this.src);
				};
				wrapper.appendChild(imageElement);
			}
		}

		// Append a small log section
		if (this.eventLog && this.eventLog.length) {
			const logContainer = document.createElement("div");
			logContainer.className = "facerecognition-log";
			for (const line of this.eventLog) {
				const row = document.createElement("div");
				row.className = "facerecognition-log-entry";
				row.innerHTML = line;
				logContainer.appendChild(row);
			}
			wrapper.appendChild(logContainer);
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
