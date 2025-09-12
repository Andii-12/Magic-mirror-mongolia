Module.register("personalcalendar", {
	// Default module config.
	defaults: {
		updateInterval: 1000, // Check for updates every 1 second
		statusFile: "/tmp/magicmirror_face_status.json",
		profilesFile: "user_profiles.json",
		animationSpeed: 2000,
		maximumEntries: 5,
		maximumNumberOfDays: 7,
		displaySymbol: true,
		defaultSymbol: "calendar",
		maxTitleLength: 25,
		wrapEvents: true,
		fade: true,
		fadePoint: 0.25
	},

	// Define required scripts.
	getScripts: function() {
		return ["moment.js"];
	},

	// Define start sequence.
	start: function() {
		console.log("Starting Personal Calendar module: " + this.name);
		this.currentUser = null;
		this.userProfile = null;
		this.events = [];
		this.userProfiles = null;
		this.loadUserProfiles();
		this.startStatusCheck();
	},

	// Load user profiles from JSON file
	loadUserProfiles: function() {
		const self = this;
		// Load profiles via node helper instead of fetch
		this.sendSocketNotification("LOAD_USER_PROFILES", {
			profilesFile: this.config.profilesFile
		});
	},

	// Start checking for face recognition status
	startStatusCheck: function() {
		const self = this;
		this.statusCheckTimer = setInterval(function() {
			self.checkFaceStatus();
		}, this.config.updateInterval);
	},

	// Check face recognition status via node helper
	checkFaceStatus: function() {
		this.sendSocketNotification("CHECK_FACE_STATUS", {
			statusFile: this.config.statusFile
		});
	},

	// Override socket notification handler
	socketNotificationReceived: function(notification, payload) {
		console.log("Personal Calendar received notification:", notification);
		
		if (notification === "FACE_STATUS_UPDATE") {
			console.log("Personal Calendar: Face status update:", payload);
			if (payload.person && payload.person !== this.currentUser) {
				this.currentUser = payload.person;
				console.log("Personal Calendar: User changed to", this.currentUser);
				this.loadUserProfile();
			} else if (!payload.person && this.currentUser) {
				this.currentUser = null;
				this.userProfile = null;
				this.events = [];
				console.log("Personal Calendar: User cleared");
				this.updateDom(this.config.animationSpeed);
			}
		} else if (notification === "USER_PROFILES_LOADED") {
			console.log("Personal Calendar: User profiles loaded");
			this.userProfiles = payload;
			if (this.currentUser) {
				this.loadUserProfile();
			}
		} else if (notification === "PERSONAL_API_DATA") {
			// Get events from the API data
			console.log("Personal Calendar: Received API data");
			console.log("Personal Calendar: Current user:", this.currentUser);
			console.log("Personal Calendar: Available users:", payload.users ? payload.users.map(u => u.name) : "No users");
			
			if (payload.users && this.currentUser) {
				const user = payload.users.find(u => 
					u.name.toLowerCase() === this.currentUser.toLowerCase()
				);
				if (user) {
					this.events = user.events || [];
					console.log(`Personal Calendar: Loaded ${this.events.length} events for ${this.currentUser}`);
					console.log("Personal Calendar: Events:", this.events.map(e => e.title));
					this.updateDom(this.config.animationSpeed);
				} else {
					console.log(`Personal Calendar: User ${this.currentUser} not found in API data`);
				}
			} else {
				console.log("Personal Calendar: No users in payload or no current user");
			}
		} else if (notification === "USER_DATA_LOADED") {
			// Handle user data from socket notification
			console.log("Personal Calendar: Received user data via socket:", payload);
			if (payload.user && payload.user === this.currentUser) {
				this.events = payload.events || [];
				console.log(`Personal Calendar: Loaded ${this.events.length} events for ${this.currentUser}`);
				console.log("Personal Calendar: Events:", this.events.map(e => e.title));
				this.updateDom(this.config.animationSpeed);
			} else if (payload.user && !this.currentUser) {
				// If we receive data but no current user, ignore it
				console.log("Personal Calendar: Received data but no current user, ignoring");
			} else if (!payload.user) {
				// Clear data if no user specified
				this.events = [];
				console.log("Personal Calendar: Cleared events (no user)");
				this.updateDom(this.config.animationSpeed);
			}
		}
	},

	// Override notificationReceived method to handle MM notifications
	notificationReceived: function(notification, payload, sender) {
		if (notification === "FACE_STATUS_UPDATE") {
			console.log("Personal Calendar: Received face status via MM notification:", payload);
			if (payload.person && payload.person !== this.currentUser) {
				// Clear old data immediately when user changes
				this.events = [];
				this.updateDom(this.config.animationSpeed);
				
				this.currentUser = payload.person;
				console.log("Personal Calendar: User changed to", this.currentUser);
				this.loadUserProfile();
			} else if (!payload.person && this.currentUser) {
				this.currentUser = null;
				this.userProfile = null;
				this.events = [];
				console.log("Personal Calendar: User cleared");
				this.updateDom(this.config.animationSpeed);
			}
		} else if (notification === "USER_DATA_LOADED") {
			// Handle user data from personalapi module
			console.log("Personal Calendar: Received user data:", payload);
			if (payload.user && payload.user === this.currentUser) {
				this.events = payload.events || [];
				console.log(`Personal Calendar: Loaded ${this.events.length} events for ${this.currentUser}`);
				console.log("Personal Calendar: Events:", this.events.map(e => e.title));
				this.updateDom(this.config.animationSpeed);
			} else if (payload.user && !this.currentUser) {
				// If we receive data but no current user, ignore it
				console.log("Personal Calendar: Received data but no current user, ignoring");
			} else if (!payload.user) {
				// Clear data if no user specified
				this.events = [];
				console.log("Personal Calendar: Cleared events (no user)");
				this.updateDom(this.config.animationSpeed);
			}
		} else if (notification === "PERSONAL_API_DATA") {
			// Handle API data from MM notifications
			console.log("Personal Calendar: Received API data via MM notification");
			console.log("Personal Calendar: Current user:", this.currentUser);
			console.log("Personal Calendar: Available users:", payload.users ? payload.users.map(u => u.name) : "No users");
			
			if (payload.users && this.currentUser) {
				const user = payload.users.find(u => 
					u.name.toLowerCase() === this.currentUser.toLowerCase()
				);
				if (user) {
					this.events = user.events || [];
					console.log(`Personal Calendar: Loaded ${this.events.length} events for ${this.currentUser}`);
					console.log("Personal Calendar: Events:", this.events.map(e => e.title));
					this.updateDom(this.config.animationSpeed);
				} else {
					console.log(`Personal Calendar: User ${this.currentUser} not found in API data`);
				}
			} else {
				console.log("Personal Calendar: No users in payload or no current user");
			}
		}
	},

	// Load user profile and calendar
	loadUserProfile: function() {
		if (!this.userProfiles || !this.currentUser) {
			return;
		}

		const userProfile = this.userProfiles.users[this.currentUser] || this.userProfiles.default;
		this.userProfile = userProfile;

		if (userProfile.calendar && userProfile.calendar.enabled) {
			// Load calendar events
			this.loadCalendarEvents(userProfile.calendar);
		} else {
			this.events = [];
		}

		this.updateDom(this.config.animationSpeed);
	},

	// Load calendar events from API data
	loadCalendarEvents: function(calendarConfig) {
		// This will be called from the personalapi module when user data is loaded
		// The events are already loaded in the personalapi module
		console.log(`Personal Calendar: Using API data for ${this.currentUser}`);
	},

	// Override dom generator.
	getDom: function() {
		const wrapper = document.createElement("div");
		wrapper.className = "personalcalendar";

		// Show message when no user is recognized
		if (!this.currentUser) {
			wrapper.innerHTML = "Царай танилт хүлээж байна...<br><small>Царай танигдсаны дараа хувийн цагийн хуваарь харагдана</small>";
			wrapper.className = "dimmed light small";
			return wrapper;
		}

		// Show events if available
		if (this.events.length === 0) {
			wrapper.innerHTML = `${this.currentUser}-ийн цагийн хуваарь хоосон байна`;
			wrapper.className = "dimmed light small";
			return wrapper;
		}

		// Create header
		const header = document.createElement("div");
		header.className = "personalcalendar-header";
		header.innerHTML = `📅 ${this.currentUser}-ийн цагийн хуваарь`;
		wrapper.appendChild(header);

		// Create events list
		const eventsList = document.createElement("div");
		eventsList.className = "personalcalendar-events";

		this.events.slice(0, this.config.maximumEntries).forEach((event, index) => {
			const eventElement = document.createElement("div");
			eventElement.className = "personalcalendar-event";

			const timeElement = document.createElement("div");
			timeElement.className = "personalcalendar-time";
			
			if (event.allDay) {
				timeElement.innerHTML = this.formatDate(event.startDate);
			} else {
				timeElement.innerHTML = this.formatTime(event.startDate);
			}

			const titleElement = document.createElement("div");
			titleElement.className = "personalcalendar-title";
			titleElement.innerHTML = this.shortenTitle(event.title);

			eventElement.appendChild(timeElement);
			eventElement.appendChild(titleElement);
			eventsList.appendChild(eventElement);
		});

		wrapper.appendChild(eventsList);

		return wrapper;
	},

	// Format time for display
	formatTime: function(dateString) {
		if (!dateString) return "00:00";
		const date = new Date(dateString);
		return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
	},

	// Format date for display
	formatDate: function(dateString) {
		if (!dateString) return "Өнөөдөр";
		
		const date = new Date(dateString);
		const today = new Date();
		const tomorrow = new Date(today);
		tomorrow.setDate(tomorrow.getDate() + 1);

		if (date.toDateString() === today.toDateString()) {
			return "Өнөөдөр"; // Today
		} else if (date.toDateString() === tomorrow.toDateString()) {
			return "Маргааш"; // Tomorrow
		} else {
			return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
		}
	},

	// Shorten title if too long
	shortenTitle: function(title) {
		if (title.length > this.config.maxTitleLength) {
			return title.substring(0, this.config.maxTitleLength) + "...";
		}
		return title;
	},

	// Override suspend method.
	suspend: function() {
		if (this.statusCheckTimer) {
			clearInterval(this.statusCheckTimer);
		}
	},

	// Override resume method.
	resume: function() {
		this.startStatusCheck();
	}
});
