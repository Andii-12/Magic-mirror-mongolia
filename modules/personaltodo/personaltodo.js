Module.register("personaltodo", {
	// Default module config.
	defaults: {
		updateInterval: 1000, // Check for updates every 1 second
		statusFile: "/tmp/magicmirror_face_status.json",
		profilesFile: "user_profiles.json",
		animationSpeed: 2000,
		showCompleted: false,
		maxItems: 10
	},

	// Define required scripts.
	getScripts: function() {
		return ["moment.js"];
	},

	// Define start sequence.
	start: function() {
		console.log("Starting Personal Todo module: " + this.name);
		this.currentUser = null;
		this.userProfile = null;
		this.todoItems = [];
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
		console.log("Personal Todo received notification:", notification);
		
		if (notification === "FACE_STATUS_UPDATE") {
			console.log("Personal Todo: Face status update:", payload);
			if (payload.person && payload.person !== this.currentUser) {
				this.currentUser = payload.person;
				console.log("Personal Todo: User changed to", this.currentUser);
				this.loadUserProfile();
			} else if (!payload.person && this.currentUser) {
				this.currentUser = null;
				this.userProfile = null;
				this.todoItems = [];
				console.log("Personal Todo: User cleared");
				this.updateDom(this.config.animationSpeed);
			}
		} else if (notification === "USER_PROFILES_LOADED") {
			console.log("Personal Todo: User profiles loaded");
			this.userProfiles = payload;
			if (this.currentUser) {
				this.loadUserProfile();
			}
		} else if (notification === "PERSONAL_API_DATA") {
			// Get todo lists from the API data
			console.log("Personal Todo: Received API data");
			console.log("Personal Todo: Current user:", this.currentUser);
			console.log("Personal Todo: Available users:", payload.users ? payload.users.map(u => u.name) : "No users");
			
			if (payload.users && this.currentUser) {
				const user = payload.users.find(u => 
					u.name.toLowerCase() === this.currentUser.toLowerCase()
				);
				if (user && user.lists) {
					// Flatten all todo items from all lists
					this.todoItems = [];
					user.lists.forEach(list => {
						if (list.items) {
							list.items.forEach(item => {
								this.todoItems.push({
									title: item.title,
									completed: item.completed,
									listTitle: list.title
								});
							});
						}
					});
					console.log(`Personal Todo: Loaded ${this.todoItems.length} items for ${this.currentUser}`);
					console.log("Personal Todo: Items:", this.todoItems.map(i => i.title));
					this.updateDom(this.config.animationSpeed);
				} else {
					console.log(`Personal Todo: User ${this.currentUser} not found or no lists`);
				}
			} else {
				console.log("Personal Todo: No users in payload or no current user");
			}
		}
	},

	// Override notificationReceived method to handle MM notifications
	notificationReceived: function(notification, payload, sender) {
		if (notification === "FACE_STATUS_UPDATE") {
			console.log("Personal Todo: Received face status via MM notification:", payload);
			if (payload.person && payload.person !== this.currentUser) {
				this.currentUser = payload.person;
				console.log("Personal Todo: User changed to", this.currentUser);
				this.loadUserProfile();
			} else if (!payload.person && this.currentUser) {
				this.currentUser = null;
				this.userProfile = null;
				this.todoItems = [];
				console.log("Personal Todo: User cleared");
				this.updateDom(this.config.animationSpeed);
			}
		} else if (notification === "USER_DATA_LOADED") {
			// Handle user data from personalapi module
			console.log("Personal Todo: Received user data:", payload);
			if (payload.user === this.currentUser) {
				// Flatten all todo items from all lists
				this.todoItems = [];
				if (payload.lists) {
					payload.lists.forEach(list => {
						if (list.items) {
							list.items.forEach(item => {
								this.todoItems.push({
									title: item.title,
									completed: item.completed,
									listTitle: list.title
								});
							});
						}
					});
				}
				console.log(`Personal Todo: Loaded ${this.todoItems.length} items for ${this.currentUser}`);
				console.log("Personal Todo: Items:", this.todoItems.map(i => i.title));
				this.updateDom(this.config.animationSpeed);
			}
		} else if (notification === "PERSONAL_API_DATA") {
			// Handle API data from MM notifications
			console.log("Personal Todo: Received API data via MM notification");
			console.log("Personal Todo: Current user:", this.currentUser);
			console.log("Personal Todo: Available users:", payload.users ? payload.users.map(u => u.name) : "No users");
			
			if (payload.users && this.currentUser) {
				const user = payload.users.find(u => 
					u.name.toLowerCase() === this.currentUser.toLowerCase()
				);
				if (user && user.lists) {
					// Flatten all todo items from all lists
					this.todoItems = [];
					user.lists.forEach(list => {
						if (list.items) {
							list.items.forEach(item => {
								this.todoItems.push({
									title: item.title,
									completed: item.completed,
									listTitle: list.title
								});
							});
						}
					});
					console.log(`Personal Todo: Loaded ${this.todoItems.length} items for ${this.currentUser}`);
					console.log("Personal Todo: Items:", this.todoItems.map(i => i.title));
					this.updateDom(this.config.animationSpeed);
				} else {
					console.log(`Personal Todo: User ${this.currentUser} not found or no lists`);
				}
			} else {
				console.log("Personal Todo: No users in payload or no current user");
			}
		}
	},

	// Load user profile and todo items
	loadUserProfile: function() {
		if (!this.userProfiles || !this.currentUser) {
			return;
		}

		const userProfile = this.userProfiles.users[this.currentUser] || this.userProfiles.default;
		this.userProfile = userProfile;

		if (userProfile.todo && userProfile.todo.enabled) {
			this.todoItems = userProfile.todo.list || [];
			console.log(`Personal Todo: Loaded ${this.todoItems.length} items for ${this.currentUser}`);
		} else {
			this.todoItems = [];
		}

		this.updateDom(this.config.animationSpeed);
	},

	// Override dom generator.
	getDom: function() {
		const wrapper = document.createElement("div");
		wrapper.className = "personaltodo";

		// Show message when no user is recognized
		if (!this.currentUser) {
			wrapper.innerHTML = "Waiting for face recognition...<br><small>Personal todo list will appear here when a face is recognized</small>";
			wrapper.className = "dimmed light small";
			return wrapper;
		}

		// Show todo items if available
		if (this.todoItems.length === 0) {
			wrapper.innerHTML = `No todo items for ${this.currentUser}`;
			wrapper.className = "dimmed light small";
			return wrapper;
		}

		// Create header
		const header = document.createElement("div");
		header.className = "personaltodo-header";
		header.innerHTML = `📋 ${this.currentUser}'s Tasks`;
		wrapper.appendChild(header);

		// Create todo list
		const todoList = document.createElement("ul");
		todoList.className = "personaltodo-list";

		this.todoItems.slice(0, this.config.maxItems).forEach((item, index) => {
			const listItem = document.createElement("li");
			listItem.className = `personaltodo-item ${item.completed ? 'completed' : ''}`;
			
			const checkbox = item.completed ? '☑' : '☐';
			const text = item.listTitle ? `${item.title} (${item.listTitle})` : item.title;
			
			listItem.innerHTML = `
				<span class="personaltodo-checkbox">${checkbox}</span>
				<span class="personaltodo-text">${text}</span>
			`;
			todoList.appendChild(listItem);
		});

		wrapper.appendChild(todoList);

		return wrapper;
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
