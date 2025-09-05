const NodeHelper = require("node_helper");
const Log = require("logger");
const fs = require("fs");

module.exports = NodeHelper.create({
	// Override socketNotificationReceived method.
	socketNotificationReceived: function(notification, payload) {
		Log.log(`${this.name} received a socket notification: ${notification}`);
		
		if (notification === "CHECK_FACE_STATUS") {
			this.checkFaceStatus(payload);
		} else if (notification === "LOAD_USER_PROFILES") {
			this.loadUserProfiles(payload);
		}
	},

	// Check face recognition status
	checkFaceStatus: function(payload) {
		const self = this;
		const statusFile = payload.statusFile;
		
		try {
			if (fs.existsSync(statusFile)) {
				const data = JSON.parse(fs.readFileSync(statusFile, 'utf8'));
				Log.log(`Personal Todo: Face status - Person: ${data.person}, Active: ${data.active}`);
				self.sendSocketNotification("FACE_STATUS_UPDATE", data);
			} else {
				Log.log("Personal Todo: Face status file not found");
				self.sendSocketNotification("FACE_STATUS_UPDATE", {
					person: null,
					active: false,
					status: "waiting"
				});
			}
		} catch (error) {
			Log.error(`Personal Todo: Error reading face status: ${error.message}`);
		}
	},

	// Load user profiles
	loadUserProfiles: function(payload) {
		const self = this;
		const profilesFile = payload.profilesFile;
		
		try {
			if (fs.existsSync(profilesFile)) {
				const data = JSON.parse(fs.readFileSync(profilesFile, 'utf8'));
				Log.log(`Personal Todo: User profiles loaded from ${profilesFile}`);
				self.sendSocketNotification("USER_PROFILES_LOADED", data);
			} else {
				Log.error(`Personal Todo: User profiles file not found: ${profilesFile}`);
				self.sendSocketNotification("USER_PROFILES_LOADED", { users: {}, default: {} });
			}
		} catch (error) {
			Log.error(`Personal Todo: Error loading user profiles: ${error.message}`);
			self.sendSocketNotification("USER_PROFILES_LOADED", { users: {}, default: {} });
		}
	}
});