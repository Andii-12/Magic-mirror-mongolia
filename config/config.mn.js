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
						fetchInterval: 7 * 24 * 60 * 60 * 1000, // Weekly update
						symbol: "calendar-check",
						url: "https://ics.calendarlabs.com/76/mm3137/US_Holidays.ics"
					}
				],
				maximumEntries: 5, // Limit for Pi 4 performance
				animationSpeed: 2000
			}
		},
		{
			module: "compliments",
			position: "lower_third",
			config: {
				compliments: {
					morning: [
						"Сайн өглөө!", // Good morning!
						"Өглөөний мэнд!", // Morning greetings!
						"Сайхан өдөр болтугай!" // Have a great day!
					],
					afternoon: [
						"Сайн өдөр!", // Good day!
						"Өдрийн мэнд!", // Day greetings!
						"Амжилттай байгаарай!" // Be successful!
					],
					evening: [
						"Сайн орой!", // Good evening!
						"Оройн мэнд!", // Evening greetings!
						"Амрах цаг болтугай!" // Have a good rest!
					]
				},
				updateInterval: 30000 // 30 seconds
			}
		},
		{
			module: "weather",
			position: "top_right",
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
		{
			module: "weather",
			position: "top_right",
			header: "Цаг агаарын урьдчилсан мэдээ", // "Weather Forecast" in Mongolian
			config: {
				weatherProvider: "openmeteo",
				type: "forecast",
				lat: 47.8864,
				lon: 106.9057,
				maxNumberOfDays: 3, // Limit for Pi 4 performance
				updateInterval: 10 * 60 * 1000
			}
		},
		{
			module: "newsfeed",
			position: "bottom_bar",
			config: {
				feeds: [
					{
						title: "Монголын мэдээ", // Mongolian news
						url: "https://www.montsame.mn/mn/rss.xml" // Example Mongolian news RSS
					}
				],
				showSourceTitle: true,
				showPublishDate: true,
				updateInterval: 5 * 60 * 1000, // 5 minutes
				maxNewsItems: 5, // Limit for Pi 4 performance
				animationSpeed: 2000
			}
		}
	]
};

/*************** DO NOT EDIT THE LINE BELOW ***************/
if (typeof module !== "undefined") { module.exports = config; }
