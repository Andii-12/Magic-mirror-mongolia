/* global Module, Log, moment */

Module.register("personalapi", {
	// Default module config.
	defaults: {
		apiUrl: "https://calendar-app-production-6d2d.up.railway.app/api/magic-mirror/future-data",
		updateInterval: 5 * 60 * 1000, // 5 minutes
		animationSpeed: 2000,
		statusFile: "/tmp/magicmirror_face_status.json",
		maxEvents: 5,
		maxLists: 3,
		showCompleted: false,
		dateFormat: "MMM Do",
		timeFormat: "HH:mm"
	},

	// Define required scripts.
	getScripts: function() {
		return ["moment.js"];
	},

	// Define start sequence.
	start: function() {
		console.log("Starting Personal API module: " + this.name);

		// Set locale.
		moment.locale(config.language);

		this.currentUser = null;
		this.userData = null;
		this.events = [];
		this.lists = [];
		this.loaded = false;
		this.lastUpdate = null;

		this.startStatusCheck();
		this.fetchData();
		this.scheduleUpdate();
	},

	// Start checking for face recognition status
	startStatusCheck: function() {
		const self = this;
		this.statusCheckTimer = setInterval(function() {
			self.checkFaceStatus();
		}, 1000); // Check every second
	},

	// Check face recognition status via node helper
	checkFaceStatus: function() {
		this.sendSocketNotification("CHECK_FACE_STATUS", {
			statusFile: this.config.statusFile
		});
	},

	// Load user-specific data
	loadUserData: function() {
		if (!this.userData || !this.currentUser) {
			return;
		}

		// Find user data from API response
		const user = this.userData.users.find(u => 
			u.name.toLowerCase() === this.currentUser.toLowerCase()
		);

		if (user) {
			this.events = user.events || [];
			this.lists = user.lists || [];
			console.log(`Personal API: Loaded ${this.events.length} events and ${this.lists.length} lists for ${this.currentUser}`);
		} else {
			this.events = [];
			this.lists = [];
			console.log(`Personal API: No data found for user ${this.currentUser}`);
		}

		this.updateDom(this.config.animationSpeed);
	},

	// Fetch data from API via node helper
	fetchData: function() {
		console.log("Personal API: Requesting data from node helper");
		this.sendSocketNotification("GET_PERSONAL_API_DATA", {
			apiUrl: this.config.apiUrl
		});
	},

	// Override socket notification handler.
	socketNotificationReceived: function(notification, payload) {
		console.log("Personal API received notification:", notification);
		
		if (notification === "PERSONAL_API_DATA") {
			this.userData = payload;
			this.loaded = true;
			this.lastUpdate = new Date();
			console.log("Personal API: Data received successfully");
			console.log(`Personal API: Found ${payload.users.length} users, ${payload.summary.totalEvents} events, ${payload.summary.totalLists} lists`);
			
			// Load data for current user if available
			if (this.currentUser) {
				this.loadUserData();
			}
		} else if (notification === "PERSONAL_API_ERROR") {
			console.error("Personal API: Error fetching data:", payload);
			this.loaded = false;
		} else if (notification === "FACE_STATUS_UPDATE") {
			console.log("Personal API: Face status update:", payload);
			if (payload.person && payload.person !== this.currentUser) {
				this.currentUser = payload.person;
				console.log("Personal API: User changed to", this.currentUser);
				this.loadUserData();
			} else if (!payload.person && this.currentUser) {
				this.currentUser = null;
				this.events = [];
				this.lists = [];
				console.log("Personal API: User cleared");
				this.updateDom(this.config.animationSpeed);
			}
		}
	},

	// Schedule regular updates
	scheduleUpdate: function() {
		const self = this;
		this.updateTimer = setTimeout(function() {
			self.fetchData();
			self.scheduleUpdate();
		}, this.config.updateInterval);
	},

	// Override dom generator.
	getDom: function() {
		const wrapper = document.createElement("div");
		wrapper.className = "personalapi";

		if (!this.loaded) {
			wrapper.innerHTML = this.translate("LOADING");
			wrapper.className = "dimmed light small";
			return wrapper;
		}

		if (!this.currentUser) {
			wrapper.innerHTML = "Waiting for face recognition...";
			wrapper.className = "dimmed light small";
			return wrapper;
		}

		// Create header
		const header = document.createElement("div");
		header.className = "personalapi-header";
		header.innerHTML = `📅 ${this.currentUser}'s Schedule`;
		wrapper.appendChild(header);

		// Show events
		if (this.events.length > 0) {
			const eventsSection = this.createEventsSection();
			wrapper.appendChild(eventsSection);
		}

		// Show todo lists
		if (this.lists.length > 0) {
			const listsSection = this.createListsSection();
			wrapper.appendChild(listsSection);
		}

		// Show last update time
		if (this.lastUpdate) {
			const updateInfo = document.createElement("div");
			updateInfo.className = "personalapi-update";
			updateInfo.innerHTML = `Last updated: ${moment(this.lastUpdate).fromNow()}`;
			wrapper.appendChild(updateInfo);
		}

		return wrapper;
	},

	// Create events section
	createEventsSection: function() {
		const section = document.createElement("div");
		section.className = "personalapi-events";

		const header = document.createElement("div");
		header.className = "personalapi-section-header";
		header.innerHTML = "📅 Upcoming Events";
		section.appendChild(header);

		const eventsList = document.createElement("div");
		eventsList.className = "personalapi-events-list";

		this.events.slice(0, this.config.maxEvents).forEach(event => {
			const eventElement = document.createElement("div");
			eventElement.className = "personalapi-event";
			eventElement.style.borderLeft = `4px solid ${event.color || '#3b82f6'}`;

			const titleElement = document.createElement("div");
			titleElement.className = "personalapi-event-title";
			titleElement.innerHTML = event.title;
			eventElement.appendChild(titleElement);

			const dateElement = document.createElement("div");
			dateElement.className = "personalapi-event-date";
			dateElement.innerHTML = this.formatEventDate(event);
			eventElement.appendChild(dateElement);

			if (event.description) {
				const descElement = document.createElement("div");
				descElement.className = "personalapi-event-description";
				descElement.innerHTML = event.description;
				eventElement.appendChild(descElement);
			}

			eventsList.appendChild(eventElement);
		});

		section.appendChild(eventsList);
		return section;
	},

	// Create todo lists section
	createListsSection: function() {
		const section = document.createElement("div");
		section.className = "personalapi-lists";

		const header = document.createElement("div");
		header.className = "personalapi-section-header";
		header.innerHTML = "📋 Todo Lists";
		section.appendChild(header);

		this.lists.slice(0, this.config.maxLists).forEach(list => {
			const listElement = document.createElement("div");
			listElement.className = "personalapi-list";

			const listHeader = document.createElement("div");
			listHeader.className = "personalapi-list-header";
			listHeader.innerHTML = `${list.title} - ${this.formatListDate(list.listDate)}`;
			listElement.appendChild(listHeader);

			if (list.description) {
				const descElement = document.createElement("div");
				descElement.className = "personalapi-list-description";
				descElement.innerHTML = list.description;
				listElement.appendChild(descElement);
			}

			const itemsList = document.createElement("ul");
			itemsList.className = "personalapi-list-items";

			list.items.forEach(item => {
				if (!this.config.showCompleted && item.completed) {
					return; // Skip completed items if not showing them
				}

				const itemElement = document.createElement("li");
				itemElement.className = `personalapi-list-item ${item.completed ? 'completed' : ''}`;
				itemElement.innerHTML = `
					<span class="personalapi-checkbox">${item.completed ? '☑' : '☐'}</span>
					<span class="personalapi-item-text">${item.title}</span>
				`;
				itemsList.appendChild(itemElement);
			});

			listElement.appendChild(itemsList);
			section.appendChild(listElement);
		});

		return section;
	},

	// Format event date
	formatEventDate: function(event) {
		const eventDate = moment(event.startDate);
		const now = moment();
		const diffDays = eventDate.diff(now, 'days');

		if (diffDays === 0) {
			return "Today";
		} else if (diffDays === 1) {
			return "Tomorrow";
		} else if (diffDays < 7) {
			return eventDate.format('dddd');
		} else {
			return eventDate.format(this.config.dateFormat);
		}
	},

	// Format list date
	formatListDate: function(dateString) {
		const listDate = moment(dateString);
		const now = moment();
		const diffDays = listDate.diff(now, 'days');

		if (diffDays === 0) {
			return "Today";
		} else if (diffDays === 1) {
			return "Tomorrow";
		} else {
			return listDate.format(this.config.dateFormat);
		}
	},

	// Override suspend method.
	suspend: function() {
		if (this.statusCheckTimer) {
			clearInterval(this.statusCheckTimer);
		}
		if (this.updateTimer) {
			clearTimeout(this.updateTimer);
		}
	},

	// Override resume method.
	resume: function() {
		this.startStatusCheck();
		this.scheduleUpdate();
	}
});
