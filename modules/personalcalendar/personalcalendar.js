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

	// Define start sequence.
	start: function() {
		console.log("Starting Personal Calendar module: " + this.name);
		this.currentUser = null;
		this.userProfile = null;
		this.events = [];
		this.loadUserProfiles();
		this.startStatusCheck();
	},

	// Load user profiles from JSON file
	loadUserProfiles: function() {
		const self = this;
		fetch(this.config.profilesFile)
			.then(response => response.json())
			.then(data => {
				self.userProfiles = data;
				console.log("Personal Calendar: User profiles loaded");
			})
			.catch(error => {
				console.error("Personal Calendar: Error loading user profiles:", error);
			});
	},

	// Start checking for face recognition status
	startStatusCheck: function() {
		const self = this;
		this.statusCheckTimer = setInterval(function() {
			self.checkFaceStatus();
		}, this.config.updateInterval);
	},

	// Check face recognition status
	checkFaceStatus: function() {
		const self = this;
		fetch(this.config.statusFile)
			.then(response => response.json())
			.then(data => {
				if (data.person && data.person !== self.currentUser) {
					self.currentUser = data.person;
					self.loadUserProfile();
				}
			})
			.catch(error => {
				// File might not exist yet, that's okay
			});
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

	// Load calendar events
	loadCalendarEvents: function(calendarConfig) {
		const self = this;
		this.events = [];

		// For now, we'll create some sample events
		// In a real implementation, you would fetch from the calendar URLs
		const today = new Date();
		const sampleEvents = [
			{
				title: "Team Meeting",
				startDate: new Date(today.getTime() + 2 * 60 * 60 * 1000), // 2 hours from now
				fullDayEvent: false
			},
			{
				title: "Doctor Appointment",
				startDate: new Date(today.getTime() + 24 * 60 * 60 * 1000), // Tomorrow
				fullDayEvent: false
			},
			{
				title: "Birthday Party",
				startDate: new Date(today.getTime() + 3 * 24 * 60 * 60 * 1000), // 3 days from now
				fullDayEvent: true
			}
		];

		this.events = sampleEvents.slice(0, calendarConfig.maxEntries || this.config.maximumEntries);
		console.log(`Personal Calendar: Loaded ${this.events.length} events for ${this.currentUser}`);
	},

	// Override dom generator.
	getDom: function() {
		const wrapper = document.createElement("div");
		wrapper.className = "personalcalendar";

		// Only show if user has calendar enabled
		if (!this.userProfile || !this.userProfile.calendar || !this.userProfile.calendar.enabled || this.events.length === 0) {
			return wrapper;
		}

		// Create header
		const header = document.createElement("div");
		header.className = "personalcalendar-header";
		header.innerHTML = `📅 ${this.currentUser}'s Calendar`;
		wrapper.appendChild(header);

		// Create events list
		const eventsList = document.createElement("div");
		eventsList.className = "personalcalendar-events";

		this.events.forEach((event, index) => {
			const eventElement = document.createElement("div");
			eventElement.className = "personalcalendar-event";

			const timeElement = document.createElement("div");
			timeElement.className = "personalcalendar-time";
			
			if (event.fullDayEvent) {
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
	formatTime: function(date) {
		return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
	},

	// Format date for display
	formatDate: function(date) {
		const today = new Date();
		const tomorrow = new Date(today);
		tomorrow.setDate(tomorrow.getDate() + 1);

		if (date.toDateString() === today.toDateString()) {
			return "Today";
		} else if (date.toDateString() === tomorrow.toDateString()) {
			return "Tomorrow";
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
