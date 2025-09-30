/* Config for Mongolian Language MagicMirror²
 * Optimized for Raspberry Pi 4 with 1GB RAM
 * For more information on configuration, see:
 * https://docs.magicmirror.builders/configuration/introduction.html
 */

let config = {
	address: "0.0.0.0",
	port: 8080,
	basePath: "/",
	ipWhitelist: [],

	// Use HTTP for better performance on Pi 4
	useHttps: false,
	httpsPrivateKey: "",
	httpsCertificate: "",

	// Mongolian language configuration
	language: "mn",
	locale: "mn-MN",

	// Optimized logging for Pi 4 (reduce I/O)
	logLevel: ["INFO", "WARN", "ERROR"], // Removed DEBUG and LOG for better performance
	timeFormat: 24,
	units: "metric",

	// Performance optimizations for Pi 4
	zoom: 1.0, // Adjust if needed for your display
	customCss: "css/custom.css",
	electronOptions: {
		// Optimize for Pi 4 performance
		webPreferences: {
			contextIsolation: true,
			nodeIntegration: false,
			enableRemoteModule: false,
			// Reduce memory usage
			experimentalFeatures: false
		}
	},

	// Disable server restart checking to save resources
	reloadAfterServerRestart: false,
	
	// Optimize for standalone operation (no browser)
	kioskmode: true,

	modules: [
		{
			module: "alert",
		},
		{
			module: "updatenotification",
			position: "top_bar"
		},
		{
			module: "clock",
			position: "top_left",
			config: {
				displayType: "digital",
				timeFormat: 24,
				displaySeconds: true,
				showDate: true,
				dateFormat: "dddd, MMMM Do",
				// Mongolian timezone (adjust as needed)
				timezone: "Asia/Ulaanbaatar"
			}
		},
		{
			module: "mongolianholidays",
			header: "Монголын баярын өдрүүд", // "Mongolian Holidays"
			position: "top_left",
			config: {
				apiUrl: "https://date.nager.at/api/v3/PublicHolidays",
				updateInterval: 24 * 60 * 60 * 1000, // Update once per day
				animationSpeed: 2000,
				maximumEntries: 5,
				maximumNumberOfDays: 365,
				showDescription: true,
				dateFormat: "MMM Do",
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
			}
		},
		// Temporarily disabled weather modules
		// {
		// 	module: "weather",
		// 	position: "bottom_left",
		// 	config: {
		// 		weatherProvider: "openmeteo", // Free weather provider
		// 		type: "current",
		// 		// Ulaanbaatar coordinates (adjust for your location)
		// 		lat: 47.8864,
		// 		lon: 106.9057,
		// 		updateInterval: 10 * 60 * 1000, // 10 minutes
		// 		animationSpeed: 1000,
		// 		showFeelsLike: true,
		// 		showHumidity: "wind"
		// 	}
		// },
		// {
		// 	module: "weather",
		// 	position: "bottom_left",
		// 	header: "Цаг агаарын урьдчилсан мэдээ", // "Weather Forecast" in Mongolian
		// 	config: {
		// 		weatherProvider: "openmeteo",
		// 		type: "forecast",
		// 		lat: 47.8864,
		// 		lon: 106.9057,
		// 		maxNumberOfDays: 3, // Limit for Pi 4 performance
		// 		updateInterval: 10 * 60 * 1000
		// 	}
		// },
		{
			module: "mongoliannews",
			position: "bottom_bar",
			header: "Монголын мэдээ", // "Mongolian News" in Mongolian
			config: {
				apiKey: "pub_cb951c5b3961435ea0feb4edc321f1d2",
				apiUrl: "https://newsdata.io/api/1/latest",
				country: "mn",
				updateInterval: 10 * 60 * 1000, // 10 minutes
				animationSpeed: 3000,
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
			}
		},
		{
			module: "personalapi",
			position: "top_right",
			header: "", // Hidden - only provides data to other modules
			config: {
				apiUrl: "https://calendar-app-production-6d2d.up.railway.app/api/magic-mirror/future-data",
				updateInterval: 300000, // 5 minutes - no real-time updates
				animationSpeed: 2000,
				statusFile: "/tmp/magicmirror_face_status.json", // Linux path
				maxEvents: 2,
				maxLists: 2, // Allow todo lists to be fetched
				showCompleted: false,
				dateFormat: "MMM Do",
				timeFormat: "HH:mm",
				hidden: true // Hide this module from display
			}
		},
		{
			module: "personaltodo",
			position: "top_right",
			header: "", // Will be overridden by face recognition
			config: {
				updateInterval: 300000, // Check for updates every 5 minutes
				statusFile: "/tmp/magicmirror_face_status.json",
				profilesFile: "user_profiles.json",
				animationSpeed: 1000,
				showCompleted: false,
				maxItems: 0 // 0 = show all items (no limit)
			}
		},
		{
			module: "personalcalendar",
			position: "top_right",
			header: "", // Will be overridden by face recognition
			config: {
				updateInterval: 300000, // Check for updates every 5 minutes
				statusFile: "/tmp/magicmirror_face_status.json",
				profilesFile: "user_profiles.json",
				animationSpeed: 1000,
				maximumEntries: 5,
				maximumNumberOfDays: 7,
				displaySymbol: true,
				defaultSymbol: "calendar",
				maxTitleLength: 20,
				wrapEvents: true,
				fade: false
			}
		},
		{
			module: "facerecognition",
			position: "top_center",
			config: {
				updateInterval: 1000, // Check for updates every 1 second
				proximityThreshold: 20, // 20 cm threshold
				timeoutDelay: 10000, // 10 seconds delay before shutdown
				greetingDuration: 5000, // Show greeting for 5 seconds
				statusFile: "/tmp/magicmirror_face_status.json",
				greetingStyle: "large bright", // CSS classes for greeting display
				showDistance: true, // Show current distance
				showStatus: true, // Show recognition status
				animationSpeed: 1000, // Animation speed for greetings
				// Personalized greetings for different people
				greetings: {
					"default": "Тавтай морил {name}!",
					"unknown": "Таныг танихгүй байна",
					"Andii": "Тавтай морил Анди!",
					"Jane": "Тавтай морил Жейн!"
				}
			}
		},
		// Enable current weather (left side)
		{
			module: "weather",
			position: "bottom_left",
			config: {
				weatherProvider: "openmeteo", // Free weather provider
				type: "current",
				// Ulaanbaatar coordinates (adjust for your location)
				lat: 47.8864,
				lon: 106.9057,
				updateInterval: 10 * 60 * 1000, // 10 minutes
				animationSpeed: 1000,
				showFeelsLike: true,
				showHumidity: "wind"
			}
		},
		// Enable forecast weather (left side)
		{
			module: "weather",
			position: "bottom_left",
			header: "Цаг агаарын урьдчилсан мэдээ", // "Weather Forecast" in Mongolian
			config: {
				weatherProvider: "openmeteo",
				type: "forecast",
				lat: 47.8864,
				lon: 106.9057,
				maxNumberOfDays: 3, // Limit for Pi 4 performance
				updateInterval: 10 * 60 * 1000
			}
		}
	]
};

/*************** DO NOT EDIT THE LINE BELOW ***************/
if (typeof module !== "undefined") { module.exports = config; }
