const NodeHelper = require("node_helper");
const Log = require("logger");
const fs = require("fs");
const path = require("path");

module.exports = NodeHelper.create({
	// Helper function to wrap text after every 4 words and remove person recognition disclaimers
	wrapTextEveryFourWords: function(text) {
		if (!text) return text;
		
		// First, remove any person recognition disclaimers
		const disclaimers = [
			/уучлаарай[^.]*[.]/gi,
			/би энэ зураг дээрх хүнийг таних боломжгүй[^.]*[.]/gi,
			/хүн таних[^.]*[.]/gi,
			/таних боломжгүй[^.]*[.]/gi
		];
		
		let cleaned = text;
		for (const pattern of disclaimers) {
			cleaned = cleaned.replace(pattern, '');
		}
		
		// Split by existing newlines first to preserve paragraph structure
		const lines = cleaned.split('\n');
		const wrappedLines = lines.map(line => {
			if (!line.trim()) return line;
			
			// Split into words (handling Mongolian text and punctuation)
			const words = line.trim().split(/\s+/).filter(w => w.length > 0);
			const wrapped = [];
			
			for (let i = 0; i < words.length; i += 4) {
				const chunk = words.slice(i, i + 4).join(' ');
				wrapped.push(chunk);
			}
			
			return wrapped.join('\n');
		});
		
		return wrappedLines.join('\n').trim();
	},

	// Generate a short, simple advice line based on detected keywords
	generateSimpleAdvice: function(analysisText) {
		const text = (analysisText || '').toLowerCase();
		if (!text) return "Цэвэрлэгээ, чийгшлээ тогтмол баримтлаарай.";
		if (text.includes('батга') || text.includes('үрэвс')) {
			return "Зөөлөн цэвэрлэгээ, BHA-г 7 хоногт 2-3 удаа.";
		}
		if (text.includes('хуурай') || text.includes('хуурайш')) {
			return "Өглөө, орой чийгшүүлэгч; өдөр SPF заавал.";
		}
		if (text.includes('тослог')) {
			return "Хөнгөн гель чийгшүүлэгч, тослог багатай бүтээгдэхүүн.";
		}
		return "Цэвэрлэгээ, чийгшлээ тогтмол баримтлаарай.";
	},
	
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

			// Prepare OpenAI Vision API request (3 moderately long sentences with line breaks; focus on acne, dryness, oiliness)
		const requestBody = {
			model: config.model,
			messages: [
				{
					role: "system",
					content: "Та нь зураг дээр харагдах арьсны гадаад шинжийг дүгнэдэг туслах. ЭНЭ БОЛ АРЬСНЫ ШИНЖИЛГЭЭ, ХҮН ТАНИХ БИШ. Зураг дээр харагдах арьсны байдлыг ажиглаж, зөвхөн батга/үрэвсэл, хуурайшилт, тослогжилтын шинжийг тайлбарла. ХҮН ТАНИХ, УУЧЛАХ, БОЛОМЖГҮЙ гэх мэт үг ашиглахгүй. Шууд арьсны байдлыг тайлбарла. Монгол хэлээр хариул."
				},
				{
					role: "user",
					content: [
						{
							type: "text",
							text: "Энэ зураг дээрх арьсны байдлыг гурван дунд урт өгүүлбэрээр тайлбарла. Өгүүлбэр бүрийн төгсгөлд \\n ашиглаж шинэ мөр хий. ХҮН ТАНИХ, УУЧЛАХ, БОЛОМЖГҮЙ гэх мэт үг бүү ашигла. Шууд арьсны байдлыг тайлбарла. Эхний өгүүлбэр: Зургийг хараад батга, үрэвслийн шинж тэмдэг эсвэл нөхцөл байдлыг дэлгэрэнгүй дүгнэ (хэрэв байхгүй бол энгийн, цэвэрхэн гэж хэл). \\n Хоёр дахь өгүүлбэр: Хуурайшилт эсвэл чийгшлийн түвшинг ажиглаж, дэлгэрэнгүй тайлбарла (хэрэв хэвийн бол тодорхой хэл). \\n Гурав дахь өгүүлбэр: Тослогжилтын түвшин болон өдөр бүрийн зөвлөмжийг дэлгэрэнгүй өг (хэрэв арьс сайн байвал цэвэрлэгээ, чийгшлээ тогтмол баримтлаарай гэж хэл). Жагсаалт, эмоджи ашиглахгүй, зөвхөн гурван өгүүлбэр бөгөөд мөр бүрийн төгсгөлд \\n байх ёстой."
						},
						{
							type: "image_url",
							image_url: { url: `data:${mimeType};base64,${base64Image}` }
						}
					]
				}
			],
			max_tokens: config.maxTokens || 400,
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
					let content = data.choices[0].message.content;
					
					Log.log(`Skin Analysis: Raw response: ${content}`);
					
					// Convert literal \n or \\n into actual line breaks
					if (content) {
						content = content
							.replace(/\\n/g, '\n')
							.replace(/\\\\n/g, '\n');
					}
					
					// Remove person recognition disclaimers and wrap every 4 words
					content = self.wrapTextEveryFourWords(content);
					
					// Accept free-form 3-sentence output
					if (!content || content.trim().length < 30) {
						throw new Error("Response too short - AI may not have analyzed properly");
					}
					self.sendSocketNotification("SKIN_ANALYSIS_RESULT", {
						person: config.person,
						analysis: content.trim(),
						advice: this.generateSimpleAdvice(content),
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
		
		// Alternative prompt (same 3-sentence spec with line breaks)
		const alternativePrompt = "Энэ зураг дээрх арьсны байдлыг гурван дунд урт өгүүлбэрээр тайлбарла. Өгүүлбэр бүрийн төгсгөлд \\n ашиглаж шинэ мөр хий. ХҮН ТАНИХ, УУЧЛАХ, БОЛОМЖГҮЙ гэх мэт үг бүү ашигла. Шууд арьсны байдлыг тайлбарла. 1) Батга/үрэвслийн түвшинг дэлгэрэнгүй дүгнэ. \\n 2) Хуурайшилт, чийгшлийн шинжийг дэлгэрэнгүй тайлбарла. \\n 3) Тослогжилтын түвшин, өдөр бүрийн зөвлөмжийг дэлгэрэнгүй өг. Асуудал ажиглагдахгүй бол арьс хэвийн, цэвэрлэгээ, чийгшлээ тогтмол баримтлаарай гэж хэл. Жагсаалт, эмоджи ашиглахгүй.";
		
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
				let content = data.choices[0].message.content;
				
				Log.log(`Skin Analysis: Alternative prompt response: ${content}`);
				
				// Convert literal \n or \\n into actual line breaks
				if (content) {
					content = content
						.replace(/\\n/g, '\n')
						.replace(/\\\\n/g, '\n');
				}
				
				// Remove person recognition disclaimers and wrap every 4 words
				content = self.wrapTextEveryFourWords(content);
				
				// Accept full content as analysis
				if ((content?.trim() || "").length < 30) {
					throw new Error("Alternative response too short");
				}
				self.sendSocketNotification("SKIN_ANALYSIS_RESULT", {
					person: config.person,
					analysis: content.trim(),
					advice: this.generateSimpleAdvice(content),
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
		
		// Final fallback prompt (3 sentences with line breaks)
		const fallbackPrompt = "Гурван дунд урт өгүүлбэрээр дүгнэ, мөр бүрийн төгсгөлд \\n ашигла. ХҮН ТАНИХ, УУЧЛАХ, БОЛОМЖГҮЙ гэх мэт үг бүү ашигла. Шууд арьсны байдлыг тайлбарла. 1) Батга/үрэвсэлийн түвшинг дэлгэрэнгүй. \\n 2) Хуурайшилт/чийгшлийн шинжийг дэлгэрэнгүй. \\n 3) Тослогжилт ба нийт зөвлөгөөг дэлгэрэнгүй. Асуудал тод биш бол арьс хэвийн, тогтмол цэвэрлэж чийгшүүлээрэй гэж хэл.";
		
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
				let content = data.choices[0].message.content;
				
				Log.log(`Skin Analysis: Fallback prompt response: ${content}`);
				
				// Convert literal \n or \\n into actual line breaks
				if (content) {
					content = content
						.replace(/\\n/g, '\n')
						.replace(/\\\\n/g, '\n');
				}
				
				// Remove person recognition disclaimers and wrap every 4 words
				content = self.wrapTextEveryFourWords(content);
				
				// Use the whole content as analysis
				self.sendSocketNotification("SKIN_ANALYSIS_RESULT", {
					person: config.person,
					analysis: (content || "").trim(),
					advice: this.generateSimpleAdvice(content),
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
		const ultraBasicPrompt = "Энэ зураг дээрх арьсны харагдах байдлыг тайлбарлаж, МОНГОЛ хэлээр хариул. ХҮН ТАНИХ, УУЧЛАХ, БОЛОМЖГҮЙ гэх мэт үг бүү ашигла. ЗУРАГ ДЭЭРХ АРЬСНЫ БАЙДЛЫГ ШУУД ТАЙЛБАРЛА. Дараах хэлбэрээр хариул:\n\nАрьсны байдал:\n[3 мөр, мөр бүрт 3 үг, \\n ашиглаж шинэ мөр хий]\n\nЗөвлөмж:\n[3 мөр, мөр бүрт 3 үг, \\n ашиглаж шинэ мөр хий]\n\nЗөвхөн МОНГОЛ хэл ашигла.";
		
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
				
				// Remove person recognition disclaimers and wrap every 4 words
				analysis = self.wrapTextEveryFourWords(analysis);
				advice = self.wrapTextEveryFourWords(advice);
				// Simplify advice to a short single line based on analysis
				advice = self.generateSimpleAdvice(analysis);
				
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
			const genericAnalysis = "Арьсны өнгө тэгш\nГэрэлтэлт сайн байна\nГадаргуу жигд харагдаж\nТослог зөв байна\nӨнгө тогтмол байна\nАрьсны байдал сайн";
			const genericAdvice = "Өдөр бүр чийгшүүлэгч\nНарны хамгаалалтын бодис\nВитамин С агуулсан бүтээгдэхүүн\nТослогийг багасгах\nАрьсны арчилгаа хийх\nГүн цэвэрлэгээ хийх";
			
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
