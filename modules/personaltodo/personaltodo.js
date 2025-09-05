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

	// Define start sequence.
	start: function() {
		console.log("Starting Personal Todo module: " + this.name);
		this.currentUser = null;
		this.userProfile = null;
		this.todoItems = [];
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
				console.log("Personal Todo: User profiles loaded");
			})
			.catch(error => {
				console.error("Personal Todo: Error loading user profiles:", error);
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

		// Only show if user has todo enabled
		if (!this.userProfile || !this.userProfile.todo || !this.userProfile.todo.enabled || this.todoItems.length === 0) {
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
			listItem.className = "personaltodo-item";
			listItem.innerHTML = `
				<span class="personaltodo-checkbox">☐</span>
				<span class="personaltodo-text">${item}</span>
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
