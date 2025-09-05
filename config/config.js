/* Config for Mongolian Language MagicMirror²
 * Optimized for Raspberry Pi 4 with 1GB RAM
 * For more information on configuration, see:
 * https://docs.magicmirror.builders/configuration/introduction.html
 */

let config = {
	address: "localhost",
	port: 8080,
	basePath: "/",
	ipWhitelist: ["127.0.0.1", "::ffff:127.0.0.1", "::1"],

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
			module: "calendar",
			header: "Цагийн хуваарь", // "Schedule" in Mongolian
			position: "top_left",
			config: {
				calendars: [
					{
						symbol: "calendar-check",
						url: "http://localhost:8080/calendars/mongolian-holidays-api.ics",
						name: "Монголын баярын өдрүүд" // "Mongolian Holidays"
					}
				],
				maximumEntries: 10, // Show more holidays
				maximumNumberOfDays: 365, // Show events for the next year
				animationSpeed: 2000,
				showLocation: false,
				showEnd: false,
				timeFormat: "relative",
				dateFormat: "MMM Do",
				hidePrivate: false,
				hideOngoing: false,
				fetchInterval: 5 * 60 * 1000, // Update every 5 minutes for testing
				urgency: 365, // Show all events within a year
				fade: true,
				fadePoint: 0.25,
				displaySymbol: true,
				defaultSymbol: "calendar-check"
			}
		},
		{
			module: "compliments",
			position: "lower_third",
			config: {
				compliments: {
					anytime: [
						"Өнөөдөр ч сайхан байна шүү!", // Today is beautiful!
						"Таны өдөр амжилттай болтугай!", // May your day be successful!
						"Хүч чадалтай байгаарай!", // Stay strong!
						"Амьдрал сайхан байна!", // Life is beautiful!
						"Бүх зүйл сайн болно!", // Everything will be fine!
						"Өнөөдөр ч гайхалтай байна!", // Today is amazing!
						"Таны хүсэл мөрөөдөл биелэгдэх болтугай!", // May your wishes come true!
						"Эерэг энергитэй байгаарай!", // Stay positive!
						"Өнөөдөр ч гайхалтай өдөр байна!", // Today is a wonderful day!
						"Таны амьдрал сайхан болтугай!" // May your life be beautiful!
					],
					morning: [
						"Сайн өглөө!", // Good morning!
						"Өглөөний мэнд!", // Morning greetings!
						"Сайхан өдөр байна шүү!", // It's a beautiful day!
						"Өнөөдөр ч гайхалтай өглөө байна!", // Today is a wonderful morning!
						"Амжилттай өдөр эхэлтугай!", // May a successful day begin!
						"Өглөөний эрч хүчтэй байгаарай!", // Stay energetic in the morning!
						"Өнөөдөр ч сайхан өдөр болтугай!", // May today be a beautiful day!
						"Өглөөний аз жаргалтай байгаарай!" // Be happy in the morning!
					],
					afternoon: [
						"Сайн өдөр!", // Good day!
						"Өдрийн мэнд!", // Day greetings!
						"Амжилттай байгаарай!", // Be successful!
						"Өдрийн цаг сайхан өнгөрч байна!", // The day is going well!
						"Өнөөдөр ч гайхалтай өдөр байна!", // Today is an amazing day!
						"Амжилттай цаг болтугай!", // May it be a successful time!
						"Өдрийн эрч хүчтэй байгаарай!", // Stay energetic during the day!
						"Өнөөдөр ч сайхан өдөр байна шүү!" // Today is a beautiful day!
					],
					evening: [
						"Сайн орой!", // Good evening!
						"Оройн мэнд!", // Evening greetings!
						"Амрах цаг болтугай!", // Have a good rest!
						"Өнөөдөр ч сайхан өдөр байлаа!", // Today was a beautiful day!
						"Оройн амрах цаг сайхан болтугай!", // May the evening rest be good!
						"Өдрийн ажил амжилттай боллоо!", // The day's work was successful!
						"Оройн аз жаргалтай байгаарай!", // Be happy in the evening!
						"Өнөөдөр ч гайхалтай өдөр байлаа шүү!" // Today was an amazing day!
					]
				},
				updateInterval: 30000 // 30 seconds
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
			header: "Personal Calendar", // Will be overridden by face recognition
			config: {
				apiUrl: "https://calendar-app-production-6d2d.up.railway.app/api/magic-mirror/future-data",
				updateInterval: 5 * 60 * 1000, // 5 minutes
				animationSpeed: 2000,
				statusFile: "/tmp/magicmirror_face_status.json", // Linux path
				maxEvents: 5,
				maxLists: 0, // Hide todo lists from this module
				showCompleted: false,
				dateFormat: "MMM Do",
				timeFormat: "HH:mm"
			}
		},
		{
			module: "personaltodo",
			position: "top_right",
			header: "Personal Todo", // Will be overridden by face recognition
			config: {
				updateInterval: 1000, // Check for updates every 1 second
				statusFile: "/tmp/magicmirror_face_status.json",
				profilesFile: "user_profiles.json",
				animationSpeed: 2000,
				showCompleted: false,
				maxItems: 10
			}
		},
		{
			module: "personalcalendar",
			position: "bottom_right",
			header: "Personal Calendar", // Will be overridden by face recognition
			config: {
				updateInterval: 1000, // Check for updates every 1 second
				statusFile: "/tmp/magicmirror_face_status.json",
				profilesFile: "user_profiles.json",
				animationSpeed: 2000,
				maximumEntries: 5,
				maximumNumberOfDays: 7,
				displaySymbol: true,
				defaultSymbol: "calendar",
				maxTitleLength: 25,
				wrapEvents: true,
				fade: true,
				fadePoint: 0.25
			}
		},
		{
			module: "facerecognition",
			position: "top_center",
			config: {
				statusFile: "/tmp/magicmirror_face_status.json"
			}
		}
	]
};

/*************** DO NOT EDIT THE LINE BELOW ***************/
if (typeof module !== "undefined") { module.exports = config; }
