/* global Module, Log, moment */

Module.register("skinanalysis", {
	// Default module config.
	defaults: {
		updateInterval: 30 * 60 * 1000, // Check for updates every 30 minutes
		animationSpeed: 2000,
		apiKey: "", // OpenAI API key - set in config
		apiUrl: "https://api.openai.com/v1/chat/completions",
		model: "gpt-4o", // Vision model
		maxTokens: 300,
		statusFile: "/tmp/magicmirror_face_status.json",
		skinPhotosDir: "Skin",
		showAnalysis: true,
		showAdvice: true,
		analysisStyle: "large bright", // CSS classes
		adviceStyle: "medium light", // CSS classes
		// Personalized greetings for different people
		greetings: {
			"default": "Тавтай морил {name}!",
			"unknown": "Таныг танихгүй байна"
		}
	},

	// Define required scripts.
	getScripts: function() {
		return ["moment.js"];
	},

	// Define start sequence.
	start: function() {
		console.log("Starting Skin Analysis module: " + this.name);

		// Set locale.
		moment.locale(config.language);

		this.currentPerson = null;
		this.currentAnalysis = null;
		this.lastAnalysisTime = null;
		this.isAnalyzing = false;
		this.analysisTimer = null;
		this.statusCheckTimer = null;

		this.startStatusChecking();
		this.scheduleAnalysis();
	},

	// Start checking for status updates from face recognition
	startStatusChecking: function() {
		const self = this;
		this.statusCheckTimer = setInterval(function() {
			self.checkFaceStatus();
		}, 2000); // Check every 2 seconds
	},

	// Check face recognition status
	checkFaceStatus: function() {
		this.sendSocketNotification("CHECK_SKIN_STATUS", {
			statusFile: this.config.statusFile
		});
	},

	// Handle socket notifications
	socketNotificationReceived: function(notification, payload) {
		if (notification === "FACE_STATUS_UPDATE") {
			this.processFaceStatus(payload);
		} else if (notification === "SKIN_ANALYSIS_RESULT") {
			this.processAnalysisResult(payload);
		} else if (notification === "SKIN_ANALYSIS_ERROR") {
			this.processAnalysisError(payload);
		}
	},

	// Process face recognition status
	processFaceStatus: function(data) {
		const previousPerson = this.currentPerson;
		this.currentPerson = data.person;
		this.isActive = data.active;

		// If person changed and is recognized, wait for photo to be saved
		if (this.currentPerson && this.currentPerson !== previousPerson && this.currentPerson !== "Unknown") {
			console.log("New person recognized, waiting for photo to be saved:", this.currentPerson);
			// Wait 10 seconds for photo to be saved before analysis
			const self = this;
			setTimeout(function() {
				if (self.currentPerson === data.person) {
					console.log("Starting skin analysis after delay:", self.currentPerson);
					self.scheduleAnalysis();
				}
			}, 10000); // 10 second delay
		}

		// Clear analysis if no person
		if (!this.currentPerson || this.currentPerson === "Unknown") {
			this.currentAnalysis = null;
			this.lastAnalysisTime = null;
		}

		this.updateDom(this.config.animationSpeed);
	},

	// Process analysis result
	processAnalysisResult: function(data) {
		this.currentAnalysis = data;
		this.lastAnalysisTime = Date.now();
		this.isAnalyzing = false;
		console.log("Skin analysis completed:", data.person);
		this.updateDom(this.config.animationSpeed);
	},

	// Process analysis error
	processAnalysisError: function(error) {
		console.error("Skin analysis error:", error);
		this.isAnalyzing = false;
		this.currentAnalysis = {
			person: this.currentPerson,
			analysis: "Анализ хийхэд алдаа гарлаа",
			advice: "Дахин оролдоно уу"
		};
		this.updateDom(this.config.animationSpeed);
	},

	// Schedule skin analysis
	scheduleAnalysis: function() {
		if (this.analysisTimer) {
			clearTimeout(this.analysisTimer);
		}

		const self = this;
		// Wait 5 seconds after recognition to allow photo to be saved
		this.analysisTimer = setTimeout(function() {
			if (self.currentPerson && self.currentPerson !== "Unknown") {
				self.analyzeSkin();
			}
		}, 5000);
	},

	// Analyze skin using OpenAI Vision API
	analyzeSkin: function() {
		if (!this.config.apiKey) {
			console.error("OpenAI API key not configured");
			return;
		}

		if (this.isAnalyzing) {
			console.log("Analysis already in progress");
			return;
		}

		this.isAnalyzing = true;
		console.log("Starting skin analysis for:", this.currentPerson);

		this.sendSocketNotification("ANALYZE_SKIN", {
			person: this.currentPerson,
			apiKey: this.config.apiKey,
			apiUrl: this.config.apiUrl,
			model: this.config.model,
			maxTokens: this.config.maxTokens,
			skinPhotosDir: this.config.skinPhotosDir
		});

		this.updateDom(this.config.animationSpeed);
	},

	// Override dom generator.
	getDom: function() {
		const wrapper = document.createElement("div");
		wrapper.className = "skinanalysis";

		if (!this.currentPerson || this.currentPerson === "Unknown") {
			// No person recognized
			const statusElement = document.createElement("div");
			statusElement.className = "skinanalysis-status dimmed light small";
			statusElement.innerHTML = "Хүнийг таних хэрэгтэй";
			wrapper.appendChild(statusElement);
			return wrapper;
		}

		if (this.isAnalyzing) {
			// Analysis in progress
			const statusElement = document.createElement("div");
			statusElement.className = "skinanalysis-status medium light";
			statusElement.innerHTML = `Арьсны шинжилгээ хийж байна...`;
			wrapper.appendChild(statusElement);
			return wrapper;
		}

		if (!this.currentAnalysis) {
			// No analysis available
			const statusElement = document.createElement("div");
			statusElement.className = "skinanalysis-status medium light";
			statusElement.innerHTML = "Арьсны шинжилгээ хийхэд бэлэн";
			wrapper.appendChild(statusElement);
			return wrapper;
		}

		// Show analysis results
		if (this.config.showAnalysis && this.currentAnalysis.analysis) {
			const analysisElement = document.createElement("div");
			analysisElement.className = "skinanalysis-analysis " + this.config.analysisStyle;
			analysisElement.innerHTML = this.currentAnalysis.analysis;
			wrapper.appendChild(analysisElement);
		}

		if (this.config.showAdvice && this.currentAnalysis.advice) {
			const adviceElement = document.createElement("div");
			adviceElement.className = "skinanalysis-advice " + this.config.adviceStyle;
			adviceElement.innerHTML = this.currentAnalysis.advice;
			wrapper.appendChild(adviceElement);
		}

		// Show last analysis time
		if (this.lastAnalysisTime) {
			const timeElement = document.createElement("div");
			timeElement.className = "skinanalysis-time dimmed light small";
			const timeAgo = moment(this.lastAnalysisTime).fromNow();
			timeElement.innerHTML = `Шинжилгээ: ${timeAgo}`;
			wrapper.appendChild(timeElement);
		}

		return wrapper;
	},

	// Override suspend method.
	suspend: function() {
		if (this.analysisTimer) {
			clearTimeout(this.analysisTimer);
			this.analysisTimer = null;
		}
		if (this.statusCheckTimer) {
			clearInterval(this.statusCheckTimer);
			this.statusCheckTimer = null;
		}
	},

	// Override resume method.
	resume: function() {
		this.startStatusChecking();
		this.scheduleAnalysis();
	}
});
