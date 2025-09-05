const NodeHelper = require("node_helper");
const Log = require("logger");

module.exports = NodeHelper.create({
	// Override socketNotificationReceived method.
	socketNotificationReceived: function(notification, payload) {
		Log.log(`${this.name} received a socket notification: ${notification}`);
		
		if (notification === "GET_PERSONAL_API_DATA") {
			this.fetchPersonalData(payload);
		}
	},

	// Fetch data from personal API
	fetchPersonalData: function(config) {
		const self = this;
		
		Log.log(`Personal API: Fetching data from ${config.apiUrl}`);
		
		fetch(config.apiUrl)
			.then(response => {
				if (!response.ok) {
					throw new Error(`HTTP ${response.status}: ${response.statusText}`);
				}
				return response.json();
			})
			.then(data => {
				Log.log(`Personal API: Successfully fetched data - ${data.users.length} users, ${data.summary.totalEvents} events, ${data.summary.totalLists} lists`);
				self.sendSocketNotification("PERSONAL_API_DATA", data);
			})
			.catch(error => {
				Log.error(`Personal API: Error fetching data: ${error.message}`);
				self.sendSocketNotification("PERSONAL_API_ERROR", error.message);
			});
	}
});
