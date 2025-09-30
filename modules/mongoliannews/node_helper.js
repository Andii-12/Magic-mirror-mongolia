/* global NodeHelper */

const NodeHelper = require("node_helper");
const https = require("https");
const http = require("http");
const FeedMe = require("feedme");
const iconv = require("iconv-lite");

module.exports = NodeHelper.create({
	// Override start method.
	start: function() {
		console.log("Starting node helper for: " + this.name);
	},

	// Override socketNotificationReceived method.
	socketNotificationReceived: function(notification, payload) {
		if (notification === "GET_MONGOLIAN_NEWS") {
			this.getMongolianNews(payload);
		}
	},

	// Get Mongolian news from RSS feeds.
	getMongolianNews: function(payload) {
		const self = this;
		const maxNewsItems = payload.maxNewsItems || 5;
		const ignoreOlderThan = payload.ignoreOlderThan || 24 * 60 * 60 * 1000; // 24 hours
		
		// Mongolian news RSS feeds
		const rssFeeds = [
			"https://www.mnb.mn/rss",
			"https://ubpost.mn/rss", 
			"https://www.news.mn/rss",
			"https://www.ikon.mn/rss"
		];
		
		console.log("Fetching Mongolian news from RSS feeds");
		
		let allNewsItems = [];
		let completedFeeds = 0;
		
		// Function to process each RSS feed
		const processFeed = (feedUrl) => {
			return new Promise((resolve, reject) => {
				const parser = new FeedMe();
				const items = [];
				
				parser.on("item", (item) => {
					const title = item.title;
					const description = item.description || item.summary || item.content || "";
					const pubdate = item.pubdate || item.published || item.updated || item["dc:date"] || item["a10:updated"];
					const url = item.url || item.link || "";
					const source = item.source || feedUrl;
					
					if (title && pubdate) {
						items.push({
							title: title,
							description: description,
							source_name: source,
							pubDate: pubdate,
							url: url
						});
					}
				});
				
				parser.on("end", () => {
					resolve(items);
				});
				
				parser.on("error", (error) => {
					console.error(`Error parsing feed ${feedUrl}:`, error);
					resolve([]); // Return empty array on error
				});
				
				// Make HTTP request
				const protocol = feedUrl.startsWith("https") ? https : http;
				protocol.get(feedUrl, (res) => {
					if (res.statusCode === 200) {
						res.pipe(parser);
					} else {
						console.error(`HTTP error ${res.statusCode} for ${feedUrl}`);
						resolve([]);
					}
				}).on("error", (error) => {
					console.error(`Request error for ${feedUrl}:`, error);
					resolve([]);
				});
			});
		};
		
		// Process all feeds
		Promise.all(rssFeeds.map(processFeed))
			.then((results) => {
				// Flatten all results
				results.forEach((feedItems, index) => {
					console.log(`Feed ${index + 1} returned ${feedItems.length} items`);
					allNewsItems = allNewsItems.concat(feedItems);
				});
				
				console.log(`Total news items collected: ${allNewsItems.length}`);
				
				// Process and filter news items
				const processedItems = self.processNewsItems(allNewsItems, maxNewsItems, ignoreOlderThan);
				
				if (processedItems.length === 0) {
					console.log("No fresh news found, using fallback news");
					// Fallback to sample news if no real news is available
					const fallbackNews = [
						{
							title: "Монгол Улсын Ерөнхийлөгч У.Хүрэлсүх ОХУ-д айлчлал хийж байна",
							description: "Монгол Улсын Ерөнхийлөгч У.Хүрэлсүх Оросын Холбооны Улсад албан ёсны айлчлал хийж, хоёр орны хоорондын харилцаа, эдийн засгийн хамтын ажиллагааны талаар хэлэлцэх юм.",
							source_name: "Монголын Үндэсний Телевиз",
							pubDate: new Date().toISOString()
						}
					];
					self.sendSocketNotification("MONGOLIAN_NEWS_ITEMS", fallbackNews);
				} else {
					console.log(`Fetched ${processedItems.length} fresh news items`);
					// Log the first few items for debugging
					processedItems.slice(0, 3).forEach((item, index) => {
						console.log(`News ${index + 1}: ${item.title} (${item.pubDate})`);
					});
					self.sendSocketNotification("MONGOLIAN_NEWS_ITEMS", processedItems);
				}
			})
			.catch((error) => {
				console.error("Error fetching news:", error);
				self.sendSocketNotification("MONGOLIAN_NEWS_ERROR", "Failed to fetch news");
			});
	},

	// Process news items.
	processNewsItems: function(results, maxNewsItems, ignoreOlderThan) {
		const now = new Date().getTime();
		const cutoffTime = now - ignoreOlderThan;
		const seenTitles = new Set();
		
		// Filter out old items and duplicates
		const filteredItems = results.filter(function(item) {
			// Check if item is not too old
			if (item.pubDate) {
				const pubDate = new Date(item.pubDate).getTime();
				if (pubDate < cutoffTime) {
					return false;
				}
			}
			
			// Check for duplicates (same title)
			if (seenTitles.has(item.title)) {
				return false;
			}
			seenTitles.add(item.title);
			return true;
		});

		// Sort by publication date (newest first)
		filteredItems.sort(function(a, b) {
			const dateA = new Date(a.pubDate || 0).getTime();
			const dateB = new Date(b.pubDate || 0).getTime();
			return dateB - dateA;
		});

		// Limit number of items
		return filteredItems.slice(0, maxNewsItems);
	}
});
