/* global Module, Log, moment */

Module.register("mongoliannews", {
	// Default module config.
	defaults: {
		apiKey: "pub_cb951c5b3961435ea0feb4edc321f1d2",
		apiUrl: "https://newsdata.io/api/1/latest",
		country: "mn",
		updateInterval: 10 * 60 * 1000, // 10 minutes
		animationSpeed: 45000, // 45 seconds - very slow for comfortable reading
		maxNewsItems: 5,
		showSourceTitle: true,
		showPublishDate: true,
		showDescription: true,
		wrapTitle: true,
		wrapDescription: true,
		truncDescription: true,
		lengthDescription: 200,
		ignoreOldItems: true,
		ignoreOlderThan: 24 * 60 * 60 * 1000, // 24 hours
		hideLoading: false,
		logFeedWarnings: true,
		removeStartTags: "<p>",
		removeEndTags: "</p>",
		prohibitedWords: [],
		scrollLength: 500
	},

	// Define required scripts.
	getScripts: function() {
		return ["moment.js"];
	},

	// Define start sequence.
	start: function() {
		console.log("Starting module: " + this.name);

		// Set locale.
		moment.locale(config.language);

		this.newsItems = [];
		this.loaded = false;
		this.activeItem = 0;
		this.updateTimer = null;
		this.rotationTimer = null;

		this.updateNews();
		this.scheduleUpdate();
		this.scheduleRotation();
	},

	// Override socket notification handler.
	socketNotificationReceived: function(notification, payload) {
		if (notification === "MONGOLIAN_NEWS_ITEMS") {
			this.newsItems = payload;
			// Reset activeItem if it's out of bounds
			if (this.activeItem >= this.newsItems.length) {
				this.activeItem = 0;
			}
			this.loaded = true;
			this.updateDom(this.config.animationSpeed);
		} else if (notification === "MONGOLIAN_NEWS_ERROR") {
			console.error("Mongolian News Error: " + payload);
			this.loaded = true;
			this.updateDom(this.config.animationSpeed);
		}
	},

	// Override dom generator.
	getDom: function() {
		const wrapper = document.createElement("div");
		wrapper.className = "mongoliannews";

		if (!this.loaded) {
			wrapper.innerHTML = this.translate("LOADING");
			wrapper.className = "dimmed light small";
			return wrapper;
		}

		if (this.newsItems.length === 0) {
			wrapper.innerHTML = this.translate("NO_NEWS");
			wrapper.className = "dimmed light small";
			return wrapper;
		}

		// Show only one news item at a time
		const currentItem = this.newsItems[this.activeItem];
		const newsItemElement = this.createNewsItem(currentItem);
		wrapper.appendChild(newsItemElement);

		return wrapper;
	},

	// Create news item element.
	createNewsItem: function(newsItem) {
		const newsItemElement = document.createElement("div");
		newsItemElement.className = "news-item";

		// Title
		const titleElement = document.createElement("div");
		titleElement.className = "news-title";
		titleElement.innerHTML = this.sanitizeHTML(newsItem.title);
		newsItemElement.appendChild(titleElement);

		// Source and date
		if (this.config.showSourceTitle || this.config.showPublishDate) {
			const metaElement = document.createElement("div");
			metaElement.className = "news-meta";

			if (this.config.showSourceTitle && newsItem.source_name) {
				const sourceElement = document.createElement("span");
				sourceElement.className = "news-source";
				sourceElement.innerHTML = newsItem.source_name;
				metaElement.appendChild(sourceElement);
			}

			if (this.config.showPublishDate && newsItem.pubDate) {
				const dateElement = document.createElement("span");
				dateElement.className = "news-date";
				dateElement.innerHTML = this.formatDate(newsItem.pubDate);
				metaElement.appendChild(dateElement);
			}

			newsItemElement.appendChild(metaElement);
		}

		// Description
		if (this.config.showDescription && newsItem.description) {
			const descriptionElement = document.createElement("div");
			descriptionElement.className = "news-description";
			let description = this.sanitizeHTML(newsItem.description);
			
			if (this.config.truncDescription && description.length > this.config.lengthDescription) {
				description = description.substring(0, this.config.lengthDescription) + "...";
			}
			
			descriptionElement.innerHTML = description;
			newsItemElement.appendChild(descriptionElement);
		}

		return newsItemElement;
	},

	// Sanitize HTML content.
	sanitizeHTML: function(html) {
		if (!html) return "";
		
		// Remove start and end tags
		let sanitized = html;
		if (this.config.removeStartTags) {
			sanitized = sanitized.replace(new RegExp(this.config.removeStartTags, "g"), "");
		}
		if (this.config.removeEndTags) {
			sanitized = sanitized.replace(new RegExp(this.config.removeEndTags, "g"), "");
		}
		
		// Remove prohibited words
		if (this.config.prohibitedWords && this.config.prohibitedWords.length > 0) {
			for (let i = 0; i < this.config.prohibitedWords.length; i++) {
				const prohibitedWord = this.config.prohibitedWords[i];
				sanitized = sanitized.replace(new RegExp(prohibitedWord, "gi"), "");
			}
		}
		
		return sanitized;
	},

	// Format date.
	formatDate: function(dateString) {
		const date = moment(dateString);
		return date.fromNow();
	},

	// Update news.
	updateNews: function() {
		this.sendSocketNotification("GET_MONGOLIAN_NEWS", {
			apiKey: this.config.apiKey,
			apiUrl: this.config.apiUrl,
			country: this.config.country,
			maxNewsItems: this.config.maxNewsItems,
			ignoreOlderThan: this.config.ignoreOlderThan
		});
	},

	// Schedule update.
	scheduleUpdate: function() {
		const self = this;
		this.updateTimer = setTimeout(function() {
			self.updateNews();
			self.scheduleUpdate();
		}, this.config.updateInterval);
	},

	// Schedule rotation of news items.
	scheduleRotation: function() {
		const self = this;
		this.rotationTimer = setTimeout(function() {
			if (self.newsItems.length > 1) {
				self.activeItem = (self.activeItem + 1) % self.newsItems.length;
				console.log("Rotating to news item:", self.activeItem + 1, "of", self.newsItems.length);
				self.updateDom(1000); // 1 second fade animation
			}
			self.scheduleRotation();
		}, this.config.animationSpeed);
	},

	// Override suspend method.
	suspend: function() {
		if (this.updateTimer) {
			clearTimeout(this.updateTimer);
			this.updateTimer = null;
		}
		if (this.rotationTimer) {
			clearTimeout(this.rotationTimer);
			this.rotationTimer = null;
		}
	},

	// Override resume method.
	resume: function() {
		this.scheduleUpdate();
		this.scheduleRotation();
	}
});
