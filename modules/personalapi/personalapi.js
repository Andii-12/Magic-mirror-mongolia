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
		
		// Add a delay to ensure data is loaded before face recognition
		setTimeout(() => {
			console.log("Personal API: Initial data load completed");
		}, 2000);
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
			console.log(`Personal API: Cannot load data - userData: ${!!this.userData}, currentUser: ${this.currentUser}`);
			return;
		}

		console.log(`Personal API: Looking for user: ${this.currentUser}`);
		console.log(`Personal API: Available users:`, this.userData.users.map(u => u.name));

		// Find user data from API response - match by name
		const user = this.userData.users.find(u => 
			u.name.toLowerCase() === this.currentUser.toLowerCase()
		);

		if (user) {
			this.events = user.events || [];
			this.lists = user.lists || [];
			console.log(`Personal API: Loaded ${this.events.length} events and ${this.lists.length} lists for ${this.currentUser}`);
			console.log(`Personal API: Events:`, this.events.map(e => e.title));
			console.log(`Personal API: Lists:`, this.lists.map(l => l.title));
			
			// Debug: Log the actual data structure
			console.log(`Personal API: First event:`, this.events[0]);
			console.log(`Personal API: First list:`, this.lists[0]);
			
			// Send the specific user data to other modules with retry mechanism
			this.sendUserDataToModules();
		} else {
			this.events = [];
			this.lists = [];
			console.log(`Personal API: No data found for user ${this.currentUser}. Available users:`, this.userData.users.map(u => u.name));
			
			// Still send empty data to clear the display
			this.sendUserDataToModules();
		}

		this.updateDom(this.config.animationSpeed);
	},

	// Load user data from local profiles (fallback method)
	loadUserDataFromProfiles: function() {
		if (!this.userProfiles || !this.currentUser) {
			console.log(`Personal API: Cannot load from profiles - userProfiles: ${!!this.userProfiles}, currentUser: ${this.currentUser}`);
			return;
		}

		const userProfile = this.userProfiles.users[this.currentUser] || this.userProfiles.default;
		
		if (userProfile) {
			// Convert profile data to API format
			this.events = userProfile.calendar && userProfile.calendar.enabled ? 
				userProfile.calendar.events || [] : [];
			
			this.lists = userProfile.todo && userProfile.todo.enabled ? 
				[{
					title: "Personal Tasks",
					items: (userProfile.todo.list || []).map(item => ({
						title: item,
						completed: false
					}))
				}] : [];

			console.log(`Personal API: Loaded from profiles - ${this.events.length} events and ${this.lists.length} lists for ${this.currentUser}`);
			console.log(`Personal API: Events:`, this.events.map(e => e.title || e));
			console.log(`Personal API: Lists:`, this.lists.map(l => l.title));
			
			// Send the data to other modules
			this.sendUserDataToModules();
		} else {
			this.events = [];
			this.lists = [];
			console.log(`Personal API: No profile found for user ${this.currentUser}`);
		}

		this.loaded = true;
		this.updateDom(this.config.animationSpeed);
	},

	// Send user data to other modules with retry mechanism
	sendUserDataToModules: function() {
		const userData = {
			user: this.currentUser,
			events: this.events,
			lists: this.lists
		};

		console.log("Personal API: Sending user data to modules:", userData);
		
		// Send notification
		this.sendNotification("USER_DATA_LOADED", userData);
		
		// Also send via socket notification as backup
		this.sendSocketNotification("USER_DATA_LOADED", userData);
		
		// Retry after a short delay to ensure modules receive it
		setTimeout(() => {
			console.log("Personal API: Retrying user data send...");
			this.sendNotification("USER_DATA_LOADED", userData);
		}, 1000);
	},

	// Fetch data from API via node helper
	fetchData: function() {
		console.log("Personal API: Requesting data from node helper");
		this.sendSocketNotification("GET_PERSONAL_API_DATA", {
			apiUrl: this.config.apiUrl
		});
		
		// Also try to load from local profiles as fallback
		this.loadFromLocalProfiles();
	},

	// Load data from local user profiles as fallback
	loadFromLocalProfiles: function() {
		console.log("Personal API: Loading from local profiles as fallback");
		this.sendSocketNotification("LOAD_USER_PROFILES", {
			profilesFile: "user_profiles.json"
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
			console.log("Personal API: Users available:", payload.users.map(u => u.name));
			
			// Broadcast the API data to other modules
			this.sendNotification("PERSONAL_API_DATA", payload);
			
			// Load data for current user if available
			if (this.currentUser) {
				console.log("Personal API: Loading data for current user:", this.currentUser);
				this.loadUserData();
			} else {
				console.log("Personal API: No current user, waiting for face recognition");
				// Still broadcast the data so other modules can use it
				this.sendNotification("PERSONAL_API_DATA_READY", payload);
			}
		} else if (notification === "PERSONAL_API_ERROR") {
			console.error("Personal API: Error fetching data:", payload);
			this.loaded = false;
			// Try to load from local profiles when API fails
			this.loadFromLocalProfiles();
		} else if (notification === "USER_PROFILES_LOADED") {
			console.log("Personal API: User profiles loaded as fallback");
			this.userProfiles = payload;
			if (this.currentUser) {
				this.loadUserDataFromProfiles();
			}
		} else if (notification === "FACE_STATUS_UPDATE") {
			console.log("Personal API: Face status update:", payload);
			if (payload.person && payload.person !== this.currentUser) {
				this.currentUser = payload.person;
				console.log("Personal API: User changed to", this.currentUser);
				console.log("Personal API: Current loaded state:", this.loaded);
				console.log("Personal API: Current userData:", this.userData ? "Available" : "Not available");
				
				if (this.loaded && this.userData) {
					console.log("Personal API: Data already loaded, loading user data");
					this.loadUserData();
				} else if (this.userData) {
					console.log("Personal API: UserData available but not loaded, loading now");
					this.loaded = true;
					this.loadUserData();
				} else {
					console.log("Personal API: Data not loaded yet, will load when API data arrives");
				}
			} else if (!payload.person && this.currentUser) {
				this.currentUser = null;
				this.events = [];
				this.lists = [];
				console.log("Personal API: User cleared");
				this.updateDom(this.config.animationSpeed);
			}
		}
	},

	// Override notificationReceived method to handle MM notifications
	notificationReceived: function(notification, payload, sender) {
		if (notification === "FACE_STATUS_UPDATE") {
			console.log("Personal API: Received face status via MM notification:", payload);
			if (payload.person && payload.person !== this.currentUser) {
				this.currentUser = payload.person;
				console.log("Personal API: User changed to", this.currentUser);
				console.log("Personal API: Current loaded state:", this.loaded);
				console.log("Personal API: Current userData:", this.userData ? "Available" : "Not available");
				
				if (this.loaded && this.userData) {
					console.log("Personal API: Data already loaded, loading user data");
					this.loadUserData();
				} else if (this.userData) {
					console.log("Personal API: UserData available but not loaded, loading now");
					this.loaded = true;
					this.loadUserData();
				} else {
					console.log("Personal API: Data not loaded yet, will load when API data arrives");
				}
			} else if (!payload.person && this.currentUser) {
				this.currentUser = null;
				this.events = [];
				this.lists = [];
				console.log("Personal API: User cleared");
				this.updateDom(this.config.animationSpeed);
			}
		} else if (notification === "PERSONAL_API_DATA") {
			// Handle API data from MM notifications
			console.log("Personal API: Received API data via MM notification");
			console.log("Personal API: Current user:", this.currentUser);
			console.log("Personal API: Available users:", payload.users ? payload.users.map(u => u.name) : "No users");
			
			// Store the API data
			this.userData = payload;
			this.loaded = true;
			
			if (payload.users && this.currentUser) {
				const user = payload.users.find(u => 
					u.name.toLowerCase() === this.currentUser.toLowerCase()
				);
				if (user) {
					this.events = user.events || [];
					this.lists = user.lists || [];
					console.log(`Personal API: Loaded ${this.events.length} events and ${this.lists.length} lists for ${this.currentUser}`);
					console.log("Personal API: Events:", this.events.map(e => e.title));
					console.log("Personal API: Lists:", this.lists.map(l => l.title));
					
					// Send data to other modules
					this.sendUserDataToModules();
					this.updateDom(this.config.animationSpeed);
				} else {
					console.log(`Personal API: User ${this.currentUser} not found in API data`);
				}
			} else {
				console.log("Personal API: No users in payload or no current user");
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
			// Show default data for testing when no face is recognized
			wrapper.innerHTML = "Waiting for face recognition...<br><small>Personal data will appear here when a face is recognized</small>";
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

			if (event.description && event.description.trim()) {
				const descElement = document.createElement("div");
				descElement.className = "personalapi-event-description";
				// Replace \n with <br> for line breaks
				descElement.innerHTML = event.description.replace(/\n/g, '<br>');
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
		if (!event || !event.startDate) {
			return "No date";
		}
		
		const eventDate = moment(event.startDate);
		const now = moment();
		const diffDays = eventDate.diff(now, 'days');

		if (event.allDay) {
			if (diffDays === 0) {
				return "Өнөөдөр (Бүх өдөр)"; // Today (All Day)
			} else if (diffDays === 1) {
				return "Маргааш (Бүх өдөр)"; // Tomorrow (All Day)
			} else if (diffDays < 7) {
				return eventDate.format('dddd') + " (Бүх өдөр)"; // Day name (All Day)
			} else {
				return eventDate.format(this.config.dateFormat) + " (Бүх өдөр)"; // Date (All Day)
			}
		} else {
			if (diffDays === 0) {
				return "Өнөөдөр " + eventDate.format('HH:mm'); // Today time
			} else if (diffDays === 1) {
				return "Маргааш " + eventDate.format('HH:mm'); // Tomorrow time
			} else if (diffDays < 7) {
				return eventDate.format('dddd HH:mm'); // Day name time
			} else {
				return eventDate.format(this.config.dateFormat + ' HH:mm'); // Date time
			}
		}
	},

	// Format list date
	formatListDate: function(dateString) {
		if (!dateString) {
			return "Өнөөдөр"; // Today
		}
		
		const listDate = moment(dateString);
		const now = moment();
		const diffDays = listDate.diff(now, 'days');

		if (diffDays === 0) {
			return "Өнөөдөр"; // Today
		} else if (diffDays === 1) {
			return "Маргааш"; // Tomorrow
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
