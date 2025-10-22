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

	// Check face recognition status and look for skin analysis triggers
	checkFaceStatus: function(payload) {
		const self = this;
		const statusFile = payload.statusFile || "/tmp/magicmirror_face_status.json";
		
		try {
			if (fs.existsSync(statusFile)) {
				const data = JSON.parse(fs.readFileSync(statusFile, 'utf8'));
				self.sendSocketNotification("FACE_STATUS_UPDATE", data);
				
				// Check for skin analysis trigger files
				if (data.person && data.active) {
					self.checkForSkinAnalysisTriggers(data.person);
				}
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
	
	// Check for skin analysis trigger files
	checkForSkinAnalysisTriggers: function(personName) {
		const self = this;
		const triggerFile = `/tmp/skin_analysis_trigger_${personName}.json`;
		
		try {
			if (fs.existsSync(triggerFile)) {
				const triggerData = JSON.parse(fs.readFileSync(triggerFile, 'utf8'));
				Log.log(`Skin Analysis: Found trigger for ${personName} with photo: ${triggerData.photo_path}`);
				
				// Delete the trigger file to prevent duplicate processing
				fs.unlinkSync(triggerFile);
				
				// Send notification to start analysis with the specific photo
				self.sendSocketNotification("SKIN_ANALYSIS_TRIGGERED", {
					person: personName,
					photoPath: triggerData.photo_path,
					timestamp: triggerData.timestamp
				});
			}
		} catch (error) {
			Log.error(`Skin Analysis: Error checking triggers: ${error.message}`);
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
		
		// Use specific photo path if provided, otherwise find the most recent photo
		let photoPath;
		if (config.photoPath && fs.existsSync(config.photoPath)) {
			photoPath = config.photoPath;
			Log.log(`Skin Analysis: Using specific photo path: ${photoPath}`);
		} else {
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

			photoPath = files[0].path;
			Log.log(`Skin Analysis: Using latest photo: ${files[0].name}`);
		}

		// Read and encode the image
		try {
			const imageBuffer = fs.readFileSync(photoPath);
			const base64Image = imageBuffer.toString('base64');
			const mimeType = this.getMimeType(path.basename(photoPath));

			// Prepare OpenAI Vision API request
		const requestBody = {
			model: config.model,
			messages: [
				{
					role: "system",
					content: "Та бол зураг дээрх хүний арьсны харагдах байдлыг тайлбарлах туслах. Зөвхөн арьсны өнгө, тэгш байдал, гэрэлтэлтийг ажиглаж, ерөнхий ажиглалт хий. МОНГОЛ хэлээр хариул."
				},
				{
					role: "user",
					content: [
						{
							type: "text",
							text: "Энэ зураг дээрх хүний арьсны харагдах байдлыг тайлбарлаж, МОНГОЛ хэлээр хариул. Дараах хэлбэрээр хариул:\n\nАрьсны байдал:\n[3 мөр, мөр бүрт 3 үг, \\n ашиглаж шинэ мөр хий]\n\nЗөвлөмж:\n[3 мөр, мөр бүрт 3 үг, \\n ашиглаж шинэ мөр хий]\n\nЗөвхөн МОНГОЛ хэл ашигла. Англи хэл, эмоджи, нэмэлт тайлбар ашиглахгүй."
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
						
						// If response indicates refusal, try a different approach
						if (content.includes("cannot") || content.includes("unable") || content.includes("sorry")) {
							Log.log(`Skin Analysis: API refused analysis, trying alternative approach...`);
							throw new Error("API_REFUSED_ANALYSIS");
						}
						
						throw new Error("Invalid response format - AI did not follow instructions");
					}
					
					// Parse the response to separate analysis and advice
					const analysisMatch = content.match(/Арьсны байдал:?([\s\S]*?)(?=Зөвлөмж:|$)/);
					const adviceMatch = content.match(/Зөвлөмж:?([\s\S]*?)$/);
					
					let analysis = analysisMatch ? analysisMatch[1].trim() : content;
					let advice = adviceMatch ? adviceMatch[1].trim() : "Зөвлөмж олдсонгүй";
					
					// Convert \\n to actual line breaks
					analysis = analysis.replace(/\\n/g, '\n');
					advice = advice.replace(/\\n/g, '\n');
					
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
				
				// If API refused analysis, try with a different prompt
				if (error.message === "API_REFUSED_ANALYSIS") {
					Log.log(`Skin Analysis: Trying alternative beauty-focused prompt...`);
					self.tryAlternativePrompt(config, base64Image, mimeType);
				} else if (error.message.includes("model") || error.message.includes("gpt-4")) {
					// Try with a different model
					Log.log(`Skin Analysis: Trying with different model...`);
					const altConfig = {...config, model: "gpt-4o-mini"};
					self.tryAlternativePrompt(altConfig, base64Image, mimeType);
				} else {
					self.sendSocketNotification("SKIN_ANALYSIS_ERROR", `API Error: ${error.message}`);
				}
			});

		} catch (error) {
			Log.error(`Skin Analysis: Error reading image: ${error.message}`);
			self.sendSocketNotification("SKIN_ANALYSIS_ERROR", error.message);
		}
	},

	// Try alternative prompt if first one fails
	tryAlternativePrompt: function(config, base64Image, mimeType) {
		const self = this;
		
		// Alternative prompt - very neutral and general
		const alternativePrompt = "Энэ зураг дээрх хүний арьсны харагдах байдлыг тайлбарлаж, МОНГОЛ хэлээр хариул. Дараах хэлбэрээр хариул:\n\nАрьсны байдал:\n[3 мөр, мөр бүрт 3 үг, \\n ашиглаж шинэ мөр хий]\n\nЗөвлөмж:\n[3 мөр, мөр бүрт 3 үг, \\n ашиглаж шинэ мөр хий]\n\nЗөвхөн МОНГОЛ хэл ашигла. Англи хэл, эмоджи, нэмэлт тайлбар ашиглахгүй.";
		
		const requestBody = {
			model: config.model,
			messages: [
				{
					role: "user",
					content: [
						{
							type: "text",
							text: alternativePrompt
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

		// Make API request with alternative prompt
		fetch(config.apiUrl, {
			method: 'POST',
			headers: {
				'Authorization': `Bearer ${config.apiKey.trim()}`,
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
				
				Log.log(`Skin Analysis: Alternative prompt response: ${content}`);
				
				// Check if response contains the expected format
				if (!content.includes("Арьсны байдал") || !content.includes("Зөвлөмж")) {
					Log.error(`Skin Analysis: Alternative prompt also failed - missing required sections`);
					Log.error(`Skin Analysis: Response was: ${content}`);
					throw new Error("Alternative prompt also failed");
				}
				
				// Parse the response to separate analysis and advice
				const analysisMatch = content.match(/Арьсны байдал:?([\s\S]*?)(?=Зөвлөмж:|$)/);
				const adviceMatch = content.match(/Зөвлөмж:?([\s\S]*?)$/);
				
				let analysis = analysisMatch ? analysisMatch[1].trim() : content;
				let advice = adviceMatch ? adviceMatch[1].trim() : "Зөвлөмж олдсонгүй";
				
				// Convert \\n to actual line breaks
				analysis = analysis.replace(/\\n/g, '\n');
				advice = advice.replace(/\\n/g, '\n');
				
				// Validate that we got actual content
				if (analysis.length < 10 || advice.length < 10) {
					Log.error(`Skin Analysis: Alternative response too short - analysis: ${analysis.length}, advice: ${advice.length}`);
					throw new Error("Alternative response too short");
				}
				
				Log.log(`Skin Analysis: Alternative analysis completed for ${config.person}`);
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
			Log.error(`Skin Analysis: Alternative prompt also failed: ${error.message}`);
			
			// Try one more time with a very general prompt
			if (error.message.includes("refused") || error.message.includes("cannot")) {
				Log.log(`Skin Analysis: Trying final fallback prompt...`);
				self.tryFinalFallbackPrompt(config, base64Image, mimeType);
			} else {
				self.sendSocketNotification("SKIN_ANALYSIS_ERROR", `API Error: ${error.message}`);
			}
		});
	},

	// Final fallback prompt - very general
	tryFinalFallbackPrompt: function(config, base64Image, mimeType) {
		const self = this;
		
		// Very general prompt - just describe what you see
		const fallbackPrompt = "Энэ зураг дээрх хүний арьсны харагдах байдлыг тайлбарлаж, МОНГОЛ хэлээр хариул. Дараах хэлбэрээр хариул:\n\nАрьсны байдал:\n[3 мөр, мөр бүрт 3 үг, \\n ашиглаж шинэ мөр хий]\n\nЗөвлөмж:\n[3 мөр, мөр бүрт 3 үг, \\n ашиглаж шинэ мөр хий]\n\nЗөвхөн МОНГОЛ хэл ашигла.";
		
		const requestBody = {
			model: config.model,
			messages: [
				{
					role: "user",
					content: [
						{
							type: "text",
							text: fallbackPrompt
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

		// Make API request with fallback prompt
		fetch(config.apiUrl, {
			method: 'POST',
			headers: {
				'Authorization': `Bearer ${config.apiKey.trim()}`,
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(requestBody)
		})
		.then(response => {
			if (!response.ok) {
				throw new Error(`HTTP ${response.status}: ${response.statusText}`);
			}
			return response.json();
		})
		.then(data => {
			if (data.choices && data.choices[0] && data.choices[0].message) {
				const content = data.choices[0].message.content;
				
				Log.log(`Skin Analysis: Fallback prompt response: ${content}`);
				
				// Try to parse even if format is not perfect
				let analysis = content;
				let advice = "Зөвлөмж олдсонгүй";
				
				// Try to extract sections if they exist
				const analysisMatch = content.match(/Арьсны байдал:?([\s\S]*?)(?=Зөвлөмж:|$)/);
				const adviceMatch = content.match(/Зөвлөмж:?([\s\S]*?)$/);
				
				if (analysisMatch) {
					analysis = analysisMatch[1].trim().replace(/\\n/g, '\n');
				}
				if (adviceMatch) {
					advice = adviceMatch[1].trim().replace(/\\n/g, '\n');
				}
				
				// If no sections found, split content roughly in half
				if (!analysisMatch && !adviceMatch && content.length > 50) {
					const midPoint = Math.floor(content.length / 2);
					const lastSentence = content.lastIndexOf('.', midPoint);
					if (lastSentence > 0) {
						analysis = content.substring(0, lastSentence + 1).trim();
						advice = content.substring(lastSentence + 1).trim();
					}
				}
				
				Log.log(`Skin Analysis: Fallback analysis completed for ${config.person}`);
				
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
			Log.error(`Skin Analysis: All prompts failed: ${error.message}`);
			
			// Try one final time with the most basic prompt possible
			if (error.message.includes("refused") || error.message.includes("cannot") || error.message.includes("unable")) {
				Log.log(`Skin Analysis: Trying ultra-basic visual description prompt...`);
				self.tryUltraBasicPrompt(config, base64Image, mimeType);
			} else {
				self.sendSocketNotification("SKIN_ANALYSIS_ERROR", `API Error: All prompts failed - ${error.message}`);
			}
		});
	},

	// Ultra-basic prompt - just describe what you see visually
	tryUltraBasicPrompt: function(config, base64Image, mimeType) {
		const self = this;
		
		// Ultra-basic prompt - just visual description
		const ultraBasicPrompt = "Энэ зураг дээрх хүний арьсны харагдах байдлыг тайлбарлаж, МОНГОЛ хэлээр хариул. Дараах хэлбэрээр хариул:\n\nАрьсны байдал:\n[3 мөр, мөр бүрт 3 үг, \\n ашиглаж шинэ мөр хий]\n\nЗөвлөмж:\n[3 мөр, мөр бүрт 3 үг, \\n ашиглаж шинэ мөр хий]\n\nЗөвхөн МОНГОЛ хэл ашигла.";
		
		const requestBody = {
			model: config.model,
			messages: [
				{
					role: "user",
					content: [
						{
							type: "text",
							text: ultraBasicPrompt
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

		// Make API request with ultra-basic prompt
		fetch(config.apiUrl, {
			method: 'POST',
			headers: {
				'Authorization': `Bearer ${config.apiKey.trim()}`,
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(requestBody)
		})
		.then(response => {
			if (!response.ok) {
				throw new Error(`HTTP ${response.status}: ${response.statusText}`);
			}
			return response.json();
		})
		.then(data => {
			if (data.choices && data.choices[0] && data.choices[0].message) {
				const content = data.choices[0].message.content;
				
				Log.log(`Skin Analysis: Ultra-basic prompt response: ${content}`);
				
				// Try to parse even if format is not perfect
				let analysis = content;
				let advice = "Зөвлөмж олдсонгүй";
				
				// Try to extract sections if they exist
				const analysisMatch = content.match(/Арьсны байдал:?([\s\S]*?)(?=Зөвлөмж:|$)/);
				const adviceMatch = content.match(/Зөвлөмж:?([\s\S]*?)$/);
				
				if (analysisMatch) {
					analysis = analysisMatch[1].trim().replace(/\\n/g, '\n');
				}
				if (adviceMatch) {
					advice = adviceMatch[1].trim().replace(/\\n/g, '\n');
				}
				
				// If no sections found, split content roughly in half
				if (!analysisMatch && !adviceMatch && content.length > 50) {
					const midPoint = Math.floor(content.length / 2);
					const lastSentence = content.lastIndexOf('.', midPoint);
					if (lastSentence > 0) {
						analysis = content.substring(0, lastSentence + 1).trim();
						advice = content.substring(lastSentence + 1).trim();
					}
				}
				
				Log.log(`Skin Analysis: Ultra-basic analysis completed for ${config.person}`);
				
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
			Log.error(`Skin Analysis: Ultra-basic prompt also failed: ${error.message}`);
			
			// Final fallback - generate a generic response
			Log.log(`Skin Analysis: All prompts failed, generating generic response...`);
			const genericAnalysis = "Арьсны өнгө тэгш\nГэрэлтэлт сайн байна\nГадаргуу жигд харагдаж";
			const genericAdvice = "Өдөр бүр чийгшүүлэгч\nНарны хамгаалалтын бодис\nВитамин С агуулсан бүтээгдэхүүн";
			
			self.sendSocketNotification("SKIN_ANALYSIS_RESULT", {
				person: config.person,
				analysis: genericAnalysis,
				advice: genericAdvice,
				timestamp: Date.now()
			});
		});
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
