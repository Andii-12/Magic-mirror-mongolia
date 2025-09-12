const NodeHelper = require("node_helper");
const Log = require("logger");

module.exports = NodeHelper.create({
	// Override socketNotificationReceived method.
	socketNotificationReceived: function(notification, payload) {
		Log.log(`${this.name} received a socket notification: ${notification}`);
		
		if (notification === "GET_MONGOLIAN_HOLIDAYS") {
			this.fetchHolidays(payload);
		}
	},

	// Fetch holidays from Nager.Date API
	fetchHolidays: function(config) {
		const self = this;
		const year = config.year || new Date().getFullYear();
		const apiUrl = `${config.apiUrl}/${year}/MN`;
		
		Log.log(`Mongolian Holidays: Fetching holidays for ${year} from ${apiUrl}`);
		
		fetch(apiUrl)
			.then(response => {
				if (!response.ok) {
					throw new Error(`HTTP ${response.status}: ${response.statusText}`);
				}
				return response.json();
			})
			.then(data => {
				Log.log(`Mongolian Holidays: Successfully fetched ${data.length} holidays`);
				self.sendSocketNotification("MONGOLIAN_HOLIDAYS_DATA", data);
			})
			.catch(error => {
				Log.error(`Mongolian Holidays: Error fetching holidays: ${error.message}`);
				self.sendSocketNotification("MONGOLIAN_HOLIDAYS_ERROR", error.message);
			});
	}
});
