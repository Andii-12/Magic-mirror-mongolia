/* global Module, Log, moment */

Module.register("skinanalysis", {
	// Default module config.
	defaults: {
		updateInterval: 60 * 60 * 1000, // Check for updates every 60 minutes (reduced frequency)
		animationSpeed: 2000,
		apiKey: "", // OpenAI API key - set in config
		apiUrl: "https://api.openai.com/v1/chat/completions",
		model: "gpt-4o", // Vision model
		maxTokens: 200, // Reduced token limit
		statusFile: "/tmp/magicmirror_face_status.json",
		skinPhotosDir: "Skin",
		showAnalysis: true,
		showAdvice: true,
		analysisStyle: "small bright", // Smaller text
		adviceStyle: "small light", // Smaller text
		rateLimitDelay: 30000, // 30 seconds between requests
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
		this.lastAnalysisRequest = 0; // Track last analysis request time
		this.analysisRetryCount = 0; // Track retry attempts
		this.maxRetries = 2; // Maximum retry attempts

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
			// Wait 5 seconds for photo to be saved before scheduling analysis
			const self = this;
			setTimeout(function() {
				if (self.currentPerson === data.person) {
					console.log("Scheduling skin analysis after initial delay:", self.currentPerson);
					self.scheduleAnalysis();
				}
			}, 5000); // 5 second initial delay, then 15 second analysis delay
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
		
		// Check if we should retry
		if (this.analysisRetryCount < this.maxRetries && 
			(error.includes("Invalid response format") || error.includes("Response too short"))) {
			this.analysisRetryCount++;
			console.log(`Retrying analysis (attempt ${this.analysisRetryCount}/${this.maxRetries})`);
			
			// Wait 5 seconds before retry
			const self = this;
			setTimeout(function() {
				if (self.currentPerson && self.currentPerson !== "Unknown") {
					self.analyzeSkin();
				}
			}, 5000);
			return;
		}
		
		// Reset retry count
		this.analysisRetryCount = 0;
		
		let errorMessage = "Анализ хийхэд алдаа гарлаа";
		let adviceMessage = "Дахин оролдоно уу";
		
		// Provide specific error messages
		if (error.includes("401") || error.includes("Unauthorized")) {
			errorMessage = "API түлхүүр буруу байна";
			adviceMessage = "Config файлыг шалгана уу";
		} else if (error.includes("429") || error.includes("Rate limit")) {
			errorMessage = "Хэт олон хүсэлт";
			adviceMessage = "Хэсэг хэсгээр оролдоно уу";
		} else if (error.includes("Person directory not found")) {
			errorMessage = "Зураг олдсонгүй";
			adviceMessage = "Нүүр таних хэрэгтэй";
		} else if (error.includes("API key not configured")) {
			errorMessage = "API түлхүүр тохируулаагүй";
			adviceMessage = "Config файлыг засна уу";
		} else if (error.includes("Invalid response format")) {
			errorMessage = "AI хариулт буруу байна";
			adviceMessage = "Дахин оролдоно уу";
		}
		
		this.currentAnalysis = {
			person: this.currentPerson,
			analysis: errorMessage,
			advice: adviceMessage
		};
		this.updateDom(this.config.animationSpeed);
	},

	// Schedule skin analysis
	scheduleAnalysis: function() {
		if (this.analysisTimer) {
			clearTimeout(this.analysisTimer);
		}

		const self = this;
		// Wait 15 seconds after recognition to allow photo to be saved
		this.analysisTimer = setTimeout(function() {
			if (self.currentPerson && self.currentPerson !== "Unknown") {
				console.log("Scheduled analysis starting for:", self.currentPerson);
				self.analyzeSkin();
			}
		}, 15000); // Increased to 15 seconds
	},

	// Analyze skin using OpenAI Vision API
	analyzeSkin: function() {
		// Check API key configuration
		if (!this.config.apiKey || this.config.apiKey.trim() === "" || this.config.apiKey === "your-openai-api-key-here" || this.config.apiKey === "api input") {
			console.error("OpenAI API key not configured");
			this.currentAnalysis = {
				person: this.currentPerson,
				analysis: "API түлхүүр тохируулаагүй",
				advice: "Config файлд API түлхүүр оруулна уу"
			};
			this.updateDom(this.config.animationSpeed);
			return;
		}

		if (this.isAnalyzing) {
			console.log("Analysis already in progress");
			return;
		}

		// Rate limiting - check if enough time has passed since last request
		const now = Date.now();
		const timeSinceLastRequest = now - this.lastAnalysisRequest;
		const rateLimitDelay = this.config.rateLimitDelay || 30000; // 30 seconds default

		if (timeSinceLastRequest < rateLimitDelay) {
			const remainingTime = Math.ceil((rateLimitDelay - timeSinceLastRequest) / 1000);
			console.log(`Rate limit: Please wait ${remainingTime} seconds before next analysis`);
			this.currentAnalysis = {
				person: this.currentPerson,
				analysis: "Хэт олон хүсэлт",
				advice: `${remainingTime} секунд хүлээнэ үү`
			};
			this.updateDom(this.config.animationSpeed);
			return;
		}

		this.isAnalyzing = true;
		this.lastAnalysisRequest = now;
		console.log("Starting skin analysis for:", this.currentPerson);
		console.log("Using API key:", this.config.apiKey.substring(0, 10) + "...");

		this.sendSocketNotification("ANALYZE_SKIN", {
			person: this.currentPerson,
			apiKey: this.config.apiKey.trim(),
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
