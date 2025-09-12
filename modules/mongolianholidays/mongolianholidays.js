/* global Module, Log, moment */

Module.register("mongolianholidays", {
	// Default module config.
	defaults: {
		apiUrl: "https://date.nager.at/api/v3/PublicHolidays",
		updateInterval: 24 * 60 * 60 * 1000, // Update once per day
		animationSpeed: 2000,
		maximumEntries: 10,
		maximumNumberOfDays: 365,
		showDescription: true,
		dateFormat: "MMM Do",
		timeFormat: "HH:mm",
		displaySymbol: true,
		defaultSymbol: "calendar-check",
		fade: true,
		fadePoint: 0.25,
		showLocation: false,
		showEnd: false,
		timeFormat: "relative",
		hidePrivate: false,
		hideOngoing: false,
		urgency: 365,
		errorTimeout: 10000,
		debug: true,
		showError: true
	},

	// Define required scripts.
	getScripts: function() {
		return ["moment.js"];
	},

	// Define start sequence.
	start: function() {
		console.log("Starting Mongolian Holidays module: " + this.name);

		// Set locale.
		moment.locale(config.language);

		this.holidays = [];
		this.loaded = false;
		this.currentYear = new Date().getFullYear();

		this.fetchHolidays();
		this.scheduleUpdate();
	},

	// Fetch holidays from Nager.Date API
	fetchHolidays: function() {
		const self = this;
		const apiUrl = `${this.config.apiUrl}/${this.currentYear}/MN`;
		
		console.log(`Mongolian Holidays: Fetching holidays for ${this.currentYear} from ${apiUrl}`);

		fetch(apiUrl)
			.then(response => {
				if (!response.ok) {
					throw new Error(`HTTP ${response.status}: ${response.statusText}`);
				}
				return response.json();
			})
			.then(data => {
				console.log(`Mongolian Holidays: Successfully fetched ${data.length} holidays`);
				self.processHolidays(data);
			})
			.catch(error => {
				console.error(`Mongolian Holidays: Error fetching holidays: ${error.message}`);
				self.showError("API Error: " + error.message);
			});
	},

	// Process holidays data from API
	processHolidays: function(holidaysData) {
		this.holidays = holidaysData.map(holiday => {
			const startDate = moment(holiday.date);
			const endDate = moment(holiday.date).add(1, 'day'); // Most holidays are single day

			return {
				title: holiday.localName, // Use Mongolian name
				startDate: startDate.toISOString(),
				endDate: endDate.toISOString(),
				allDay: true,
				description: holiday.name, // English name as description
				location: "Mongolia",
				symbol: this.config.defaultSymbol,
				color: this.getHolidayColor(holiday.localName),
				holidayType: holiday.types ? holiday.types[0] : "Public",
				countryCode: holiday.countryCode
			};
		});

		// Sort holidays by date
		this.holidays.sort((a, b) => moment(a.startDate).diff(moment(b.startDate)));

		this.loaded = true;
		console.log(`Mongolian Holidays: Processed ${this.holidays.length} holidays`);
		this.updateDom(this.config.animationSpeed);
	},

	// Get color for different types of holidays
	getHolidayColor: function(holidayName) {
		if (holidayName.includes("Шинэ жил") || holidayName.includes("New Year")) {
			return "#ff6b6b"; // Red for New Year
		} else if (holidayName.includes("Наадам")) {
			return "#4ecdc4"; // Teal for Naadam
		} else if (holidayName.includes("Эмэгтэйчүүдийн")) {
			return "#ff9ff3"; // Pink for Women's Day
		} else if (holidayName.includes("Тусгаар") || holidayName.includes("Independence")) {
			return "#45b7d1"; // Blue for Independence
		} else {
			return "#96ceb4"; // Green for other holidays
		}
	},

	// Show error message
	showError: function(message) {
		this.loaded = true;
		this.errorMessage = message;
		this.updateDom(this.config.animationSpeed);
	},

	// Schedule regular updates
	scheduleUpdate: function() {
		const self = this;
		this.updateTimer = setTimeout(function() {
			self.fetchHolidays();
			self.scheduleUpdate();
		}, this.config.updateInterval);
	},

	// Override dom generator.
	getDom: function() {
		const wrapper = document.createElement("div");
		wrapper.className = "mongolianholidays";

		if (!this.loaded) {
			wrapper.innerHTML = this.translate("LOADING");
			wrapper.className = "dimmed light small";
			return wrapper;
		}

		if (this.errorMessage) {
			wrapper.innerHTML = `<div class="error">${this.errorMessage}</div>`;
			wrapper.className = "dimmed light small";
			return wrapper;
		}

		if (this.holidays.length === 0) {
			wrapper.innerHTML = "Баярын өдрүүд олдсонгүй";
			wrapper.className = "dimmed light small";
			return wrapper;
		}

		// Create holidays list (header is handled by MagicMirror config)
		const holidaysList = document.createElement("div");
		holidaysList.className = "holidays-list";

		// Filter holidays for the next year
		const now = moment();
		const nextYear = now.clone().add(1, 'year');
		const upcomingHolidays = this.holidays.filter(holiday => {
			const holidayDate = moment(holiday.startDate);
			return holidayDate.isAfter(now) && holidayDate.isBefore(nextYear);
		});

		upcomingHolidays.slice(0, this.config.maximumEntries).forEach(holiday => {
			const holidayElement = this.createHolidayElement(holiday);
			holidaysList.appendChild(holidayElement);
		});

		wrapper.appendChild(holidaysList);

		return wrapper;
	},

	// Create individual holiday element
	createHolidayElement: function(holiday) {
		const holidayElement = document.createElement("div");
		holidayElement.className = "holiday-item";
		holidayElement.style.borderLeft = `4px solid ${holiday.color}`;

		// Holiday title
		const titleElement = document.createElement("div");
		titleElement.className = "holiday-title";
		titleElement.innerHTML = holiday.title;
		holidayElement.appendChild(titleElement);

		// Holiday date
		const dateElement = document.createElement("div");
		dateElement.className = "holiday-date";
		dateElement.innerHTML = this.formatHolidayDate(holiday.startDate);
		holidayElement.appendChild(dateElement);

		// Holiday description (English name)
		if (this.config.showDescription && holiday.description) {
			const descElement = document.createElement("div");
			descElement.className = "holiday-description";
			descElement.innerHTML = holiday.description;
			holidayElement.appendChild(descElement);
		}

		return holidayElement;
	},

	// Format holiday date
	formatHolidayDate: function(dateString) {
		const holidayDate = moment(dateString);
		const now = moment();
		const diffDays = holidayDate.diff(now, 'days');

		if (diffDays === 0) {
			return "Өнөөдөр"; // Today
		} else if (diffDays === 1) {
			return "Маргааш"; // Tomorrow
		} else if (diffDays < 7) {
			return holidayDate.format('dddd'); // Day name
		} else {
			return holidayDate.format(this.config.dateFormat);
		}
	},

	// Override suspend method.
	suspend: function() {
		if (this.updateTimer) {
			clearTimeout(this.updateTimer);
			this.updateTimer = null;
		}
	},

	// Override resume method.
	resume: function() {
		this.scheduleUpdate();
	}
});
