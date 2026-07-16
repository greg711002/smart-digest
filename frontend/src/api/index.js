/** Smart Digest API client */

const API_BASE = "/api";

async function request(endpoint, options = {}) {
	const url = `${API_BASE}${endpoint}`;

	const config = {
		headers: {
			"Content-Type": "application/json",
			...options.headers,
		},
		...options,
	};

	if (options.body && typeof options.body === "object") {
		config.body = JSON.stringify(options.body);
	}

	const response = await fetch(url, config);

	if (!response.ok) {
		const error = await response
			.json()
			.catch(() => ({ detail: "Unknown error" }));
		throw new Error(error.detail || `HTTP ${response.status}`);
	}

	return response.json();
}

export const api = {
	// Health check
	health: () => request("/health"),

	// Feeds
	getFeeds: () => request("/feeds"),
	addFeed: (data) => request("/feeds", { method: "POST", body: data }),
	deleteFeed: (id) => request(`/feeds/${id}`, { method: "DELETE" }),

	// Articles
	getArticles: (params = {}) => {
		const query = new URLSearchParams();
		if (params.feed_id) query.set("feed_id", params.feed_id);
		if (params.tags) query.set("tags", params.tags.join(","));
		if (params.search) query.set("search", params.search);
		const qs = query.toString();
		return request(`/articles${qs ? "?" + qs : ""}`);
	},
	refreshArticle: (id) =>
		request(`/articles/${id}/refresh`, { method: "POST" }),

	// Tags
	getTags: () => request("/tags"),

	// Refresh all
	refreshAll: () => request("/refresh-all", { method: "POST" }),
};
