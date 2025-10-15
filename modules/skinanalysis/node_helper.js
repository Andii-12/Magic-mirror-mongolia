const NodeHelper = require("node_helper");
const Log = require("logger");
const fs = require("fs");
const path = require("path");

module.exports = NodeHelper.create({
	// Override socketNotificationReceived method.
	socketNotificationReceived: function(notification, payload) {
		Log.log(`${this.name} received a socket notification: ${notification}`);
		
		if (notification === "CHECK_SKIN_STATUS") {
			this.checkFaceStatus(payload);
		} else if (notification === "ANALYZE_SKIN") {
			this.analyzeSkin(payload);
		}
	},

	// Check face recognition status
	checkFaceStatus: function(payload) {
		const self = this;
		const statusFile = payload.statusFile || "/tmp/magicmirror_face_status.json";
		
		try {
			if (fs.existsSync(statusFile)) {
				const data = JSON.parse(fs.readFileSync(statusFile, 'utf8'));
				self.sendSocketNotification("FACE_STATUS_UPDATE", data);
			} else {
				self.sendSocketNotification("FACE_STATUS_UPDATE", {
					person: null,
					active: false,
					status: "waiting"
				});
			}
		} catch (error) {
			Log.error(`Skin Analysis: Error reading face status: ${error.message}`);
		}
	},

	// Analyze skin using OpenAI Vision API
	analyzeSkin: function(config) {
		const self = this;
		
		Log.log(`Skin Analysis: Starting analysis for ${config.person}`);
		
		// Check if API key is configured
		if (!config.apiKey || config.apiKey === "your-openai-api-key-here") {
			Log.error(`Skin Analysis: OpenAI API key not configured`);
			self.sendSocketNotification("SKIN_ANALYSIS_ERROR", "API key not configured");
			return;
		}
		
		// Validate API key format - more flexible
		if (!config.apiKey || config.apiKey.trim() === "") {
			Log.error(`Skin Analysis: API key is empty`);
			self.sendSocketNotification("SKIN_ANALYSIS_ERROR", "API key is empty");
			return;
		}
		
		// Clean the API key (remove spaces, newlines)
		const cleanApiKey = config.apiKey.trim();
		
		// Check if it looks like a valid OpenAI API key
		if (!cleanApiKey.startsWith('sk-') && !cleanApiKey.startsWith('sk-proj-')) {
			Log.error(`Skin Analysis: Invalid API key format. Should start with 'sk-' or 'sk-proj-'`);
			Log.error(`Skin Analysis: Your key starts with: ${cleanApiKey.substring(0, 10)}...`);
			self.sendSocketNotification("SKIN_ANALYSIS_ERROR", "Invalid API key format");
			return;
		}
		
		// Log API key for debugging (first 10 chars only for security)
		Log.log(`Skin Analysis: Using API key: ${config.apiKey.substring(0, 10)}...`);
		
		// Find the most recent skin photo for this person
		const skinBaseDir = path.join(process.cwd(), config.skinPhotosDir);
		const personDir = path.join(skinBaseDir, config.person);
		
		Log.log(`Skin Analysis: Looking for photos in: ${personDir}`);
		Log.log(`Skin Analysis: Current working directory: ${process.cwd()}`);
		Log.log(`Skin Analysis: Skin base directory: ${skinBaseDir}`);
		
		// List all directories in Skin folder for debugging
		try {
			const allDirs = fs.readdirSync(skinBaseDir, { withFileTypes: true })
				.filter(dirent => dirent.isDirectory())
				.map(dirent => dirent.name);
			Log.log(`Skin Analysis: Available person directories: ${allDirs.join(', ')}`);
		} catch (e) {
			Log.log(`Skin Analysis: Could not list base directory: ${e.message}`);
		}
		
		// Check if base Skin directory exists
		if (!fs.existsSync(skinBaseDir)) {
			Log.error(`Skin Analysis: Base skin directory not found: ${skinBaseDir}`);
			self.sendSocketNotification("SKIN_ANALYSIS_ERROR", "Skin directory not found");
			return;
		}
		
		if (!fs.existsSync(personDir)) {
			Log.error(`Skin Analysis: Person directory not found: ${personDir}`);
			Log.error(`Skin Analysis: Available persons: ${fs.readdirSync(skinBaseDir).join(', ')}`);
			self.sendSocketNotification("SKIN_ANALYSIS_ERROR", "Person directory not found");
			return;
		}

		// Get all image files in the person's directory
		const files = fs.readdirSync(personDir)
			.filter(file => /\.(jpg|jpeg|png)$/i.test(file))
			.map(file => ({
				name: file,
				path: path.join(personDir, file),
				stats: fs.statSync(path.join(personDir, file))
			}))
			.sort((a, b) => b.stats.mtime - a.stats.mtime); // Sort by modification time, newest first

		if (files.length === 0) {
			Log.error(`Skin Analysis: No skin photos found for ${config.person}`);
			Log.error(`Skin Analysis: Directory contents: ${fs.readdirSync(personDir).join(', ')}`);
			self.sendSocketNotification("SKIN_ANALYSIS_ERROR", "No skin photos found");
			return;
		}

		const latestPhoto = files[0];
		Log.log(`Skin Analysis: Using latest photo: ${latestPhoto.name}`);

		// Read and encode the image
		try {
			const imageBuffer = fs.readFileSync(latestPhoto.path);
			const base64Image = imageBuffer.toString('base64');
			const mimeType = this.getMimeType(latestPhoto.name);

			// Prepare OpenAI Vision API request
			const requestBody = {
				model: config.model,
				messages: [
					{
						role: "user",
						content: [
							{
								type: "text",
								text: "Энэ зураг дээрх хүний арьсны байдлыг шинжилж, МОНГОЛ хэлээр хариул. Зөвхөн арьсны шинж тэмдэг, өнгө, тэгш байдлыг ажиглаж, эмнэлгийн онош тогтоохгүйгээр ерөнхий ажиглалт хий. Дараах хэлбэрээр хариул:\n\nАрьсны байдал: [3 өгүүлбэр арьсны шинж тэмдэгийн талаар]\nЗөвлөмж: [3 өгүүлбэр арьсны арчилгааны зөвлөмж]\n\nЗөвхөн МОНГОЛ хэл ашигла. Англи хэл, эмоджи, нэмэлт тайлбар ашиглахгүй."
							},
							{
								type: "image_url",
								image_url: {
									url: `data:${mimeType};base64,${base64Image}`
								}
							}
						]
					}
				],
				max_tokens: config.maxTokens || 300,
				temperature: 0.7
			};

			// Make API request
			fetch(config.apiUrl, {
				method: 'POST',
				headers: {
					'Authorization': `Bearer ${cleanApiKey}`,
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(requestBody)
			})
			.then(response => {
				if (!response.ok) {
					if (response.status === 401) {
						throw new Error(`HTTP 401: Unauthorized - Invalid or expired API key`);
					} else if (response.status === 429) {
						throw new Error(`HTTP 429: Rate limit exceeded - Try again later`);
					} else if (response.status === 400) {
						throw new Error(`HTTP 400: Bad request - Check API parameters`);
					} else {
						throw new Error(`HTTP ${response.status}: ${response.statusText}`);
					}
				}
				return response.json();
			})
			.then(data => {
				if (data.choices && data.choices[0] && data.choices[0].message) {
					const content = data.choices[0].message.content;
					
					Log.log(`Skin Analysis: Raw response: ${content}`);
					
					// Check if response contains the expected format
					if (!content.includes("Арьсны байдал") || !content.includes("Зөвлөмж")) {
						Log.error(`Skin Analysis: Invalid response format - missing required sections`);
						Log.error(`Skin Analysis: Response was: ${content}`);
						throw new Error("Invalid response format - AI did not follow instructions");
					}
					
					// Parse the response to separate analysis and advice
					const analysisMatch = content.match(/Арьсны байдал:([\s\S]*?)(?=Зөвлөмж:|$)/);
					const adviceMatch = content.match(/Зөвлөмж:([\s\S]*?)$/);
					
					const analysis = analysisMatch ? analysisMatch[1].trim() : content;
					const advice = adviceMatch ? adviceMatch[1].trim() : "Зөвлөмж олдсонгүй";
					
					// Validate that we got actual content
					if (analysis.length < 10 || advice.length < 10) {
						Log.error(`Skin Analysis: Response too short - analysis: ${analysis.length}, advice: ${advice.length}`);
						throw new Error("Response too short - AI may not have analyzed properly");
					}
					
					Log.log(`Skin Analysis: Analysis completed for ${config.person}`);
					Log.log(`Skin Analysis: Analysis: ${analysis.substring(0, 50)}...`);
					Log.log(`Skin Analysis: Advice: ${advice.substring(0, 50)}...`);
					
					self.sendSocketNotification("SKIN_ANALYSIS_RESULT", {
						person: config.person,
						analysis: analysis,
						advice: advice,
						timestamp: Date.now()
					});
				} else {
					throw new Error("Invalid API response format");
				}
			})
			.catch(error => {
				Log.error(`Skin Analysis: API request failed: ${error.message}`);
				Log.error(`Skin Analysis: Error details:`, error);
				self.sendSocketNotification("SKIN_ANALYSIS_ERROR", `API Error: ${error.message}`);
			});

		} catch (error) {
			Log.error(`Skin Analysis: Error reading image: ${error.message}`);
			self.sendSocketNotification("SKIN_ANALYSIS_ERROR", error.message);
		}
	},

	// Get MIME type based on file extension
	getMimeType: function(filename) {
		const ext = path.extname(filename).toLowerCase();
		switch (ext) {
			case '.jpg':
			case '.jpeg':
				return 'image/jpeg';
			case '.png':
				return 'image/png';
			default:
				return 'image/jpeg';
		}
	}
});
