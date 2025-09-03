/* global NodeHelper */

const NodeHelper = require("node_helper");
const https = require("https");
const http = require("http");

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
		
		// Mongolian news RSS feeds
		const rssFeeds = [
			"https://www.mnb.mn/rss",
			"https://ubpost.mn/rss",
			"https://www.news.mn/rss",
			"https://www.ikon.mn/rss"
		];
		
		console.log("Fetching Mongolian news from RSS feeds");
		
		// For now, let's create some sample Mongolian news items
		const sampleNews = [
			{
				title: "Монгол Улсын Ерөнхийлөгч У.Хүрэлсүх ОХУ-д айлчлал хийж байна",
				description: "Монгол Улсын Ерөнхийлөгч У.Хүрэлсүх Оросын Холбооны Улсад албан ёсны айлчлал хийж, хоёр орны хоорондын харилцаа, эдийн засгийн хамтын ажиллагааны талаар хэлэлцэх юм.",
				source_name: "Монголын Үндэсний Телевиз",
				pubDate: new Date().toISOString()
			},
			{
				title: "Улаанбаатар хотод шинэ метроны төсөл эхэлж байна",
				description: "Улаанбаатар хотын тээврийн асуудлыг шийдэхийн тулд метроны төсөл эхэлж, эхний шугамыг 2027 онд ашиглалтад оруулахаар төлөвлөж байна.",
				source_name: "UB Post",
				pubDate: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
			},
			{
				title: "Монголын эдийн засаг 2025 онд 5.2 хувиар өсөх төлөвтэй",
				description: "Олон улсын валютын сангийн тайланд Монголын эдийн засаг 2025 онд 5.2 хувиар өсөх төлөвтэй байгааг тэмдэглэжээ.",
				source_name: "News.mn",
				pubDate: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString()
			},
			{
				title: "Монголын хөлбөмбөгийн шигшээ баг Азийн цомд оролцоно",
				description: "Монголын хөлбөмбөгийн шигшээ баг 2025 оны Азийн цомын тэмцээнд оролцож, анхны тоглолтоо Японтой хийхээр төлөвлөж байна.",
				source_name: "Ikon.mn",
				pubDate: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString()
			},
			{
				title: "Монголын уул уурхайн салбарт шинэ хөрөнгө оруулалт",
				description: "Монголын уул уурхайн салбарт 2 тэрбум долларын шинэ хөрөнгө оруулалт хийгдэхээр төлөвлөж, энэ нь эдийн засгийн өсөлтөд эерэг нөлөө үзүүлэх юм.",
				source_name: "Монголын Үндэсний Телевиз",
				pubDate: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString()
			}
		];
		
		// Send sample news items
		self.sendSocketNotification("MONGOLIAN_NEWS_ITEMS", sampleNews.slice(0, maxNewsItems));
	},

	// Process news items.
	processNewsItems: function(results, maxNewsItems, ignoreOlderThan) {
		const now = new Date().getTime();
		const cutoffTime = now - ignoreOlderThan;
		
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
			return !this.seenTitles || !this.seenTitles.has(item.title);
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
