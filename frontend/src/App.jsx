import { useState, useEffect, useCallback } from "react";
import {
	Newspaper,
	Plus,
	RefreshCw,
	Search,
	X,
	ExternalLink,
	Rss,
	ChevronDown,
} from "lucide-react";
import { api } from "./api";

// Tag colors for visual variety
const TAG_COLORS = [
	{ bg: "#F0EDE8", text: "#5C5C5C" },
	{ bg: "#E8F4EA", text: "#2D6A4F" },
	{ bg: "#E8F0F4", text: "#3A5A7C" },
	{ bg: "#F4EDE8", text: "#7C5A3A" },
	{ bg: "#F4E8F0", text: "#7C3A6A" },
	{ bg: "#E8EAF4", text: "#3A4A7C" },
];

function getTagStyle(tag, isActive) {
	if (isActive) {
		return { background: "#E85D04", color: "white" };
	}
	const hash = tag.split("").reduce((acc, c) => acc + c.charCodeAt(0), 0);
	const color = TAG_COLORS[hash % TAG_COLORS.length];
	return { background: color.bg, color: color.text };
}

function formatDate(dateStr) {
	if (!dateStr) return "";
	const date = new Date(dateStr);
	const now = new Date();
	const diff = now - date;

	if (diff < 60000) return "только что";
	if (diff < 3600000) return `${Math.floor(diff / 60000)} мин. назад`;
	if (diff < 86400000) return `${Math.floor(diff / 3600000)} ч. назад`;
	if (diff < 604800000) return `${Math.floor(diff / 86400000)} дн. назад`;

	return date.toLocaleDateString("ru-RU", { day: "numeric", month: "short" });
}

function EmptyState({ onAddFeed }) {
	return (
		<div className="empty-state">
			<div className="empty-state-icon">
				<Newspaper size={40} />
			</div>
			<h2 className="empty-state-title">Пока пусто</h2>
			<p className="empty-state-text">
				Добавьте RSS-источники, и мы автоматически создадим для вас краткие
				дайджесты с помощью ИИ.
			</p>
			<button className="btn btn-primary" onClick={onAddFeed}>
				<Plus size={18} />
				Добавить источник
			</button>
		</div>
	);
}

function SkeletonCard({ index }) {
	return (
		<div
			className="skeleton-card"
			style={{ animationDelay: `${index * 80}ms` }}
		>
			<div
				className="skeleton skeleton-line short"
				style={{ animationDelay: `${index * 80}ms` }}
			/>
			<div
				className="skeleton skeleton-title"
				style={{ animationDelay: `${index * 80 + 50}ms` }}
			/>
			<div
				className="skeleton skeleton-line medium"
				style={{ animationDelay: `${index * 80 + 100}ms` }}
			/>
			<div
				className="skeleton skeleton-line medium"
				style={{ animationDelay: `${index * 80 + 150}ms` }}
			/>
			<div
				className="skeleton skeleton-line short"
				style={{ animationDelay: `${index * 80 + 200}ms` }}
			/>
		</div>
	);
}

function FeedCard({ article, onRefresh, refreshing }) {
	return (
		<article className="feed-card">
			<div className="feed-card-meta">
				<span className="feed-card-source">{article.feed_title}</span>
				<span>•</span>
				<span>{formatDate(article.published)}</span>
			</div>

			<h3 className="feed-card-title">
				<a href={article.url} target="_blank" rel="noopener noreferrer">
					{article.title}
				</a>
			</h3>

			{article.summary && (
				<p className="feed-card-summary">{article.summary}</p>
			)}

			<div className="feed-card-footer">
				<div className="feed-card-tags">
					{article.tags?.map((tag) => (
						<span key={tag} className="tag" style={getTagStyle(tag, false)}>
							{tag}
						</span>
					))}
				</div>

				<div className="feed-card-actions">
					<button
						className="btn btn-ghost btn-icon"
						onClick={() => onRefresh(article.id)}
						disabled={refreshing}
						title="Обновить дайджест"
					>
						<RefreshCw size={16} className={refreshing ? "spinner" : ""} />
					</button>
					<a
						href={article.url}
						target="_blank"
						rel="noopener noreferrer"
						className="btn btn-ghost btn-icon"
						title="Читать оригинал"
					>
						<ExternalLink size={16} />
					</a>
				</div>
			</div>
		</article>
	);
}

function AddFeedModal({ isOpen, onClose, onAdd }) {
	const [url, setUrl] = useState("");
	const [category, setCategory] = useState("");
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");

	const handleSubmit = async (e) => {
		e.preventDefault();
		setError("");

		if (!url.trim()) {
			setError("Введите URL RSS-ленты");
			return;
		}

		try {
			setLoading(true);
			await onAdd({ url: url.trim(), category: category.trim() || undefined });
			setUrl("");
			setCategory("");
			onClose();
		} catch (err) {
			setError(err.message || "Не удалось добавить источник");
		} finally {
			setLoading(false);
		}
	};

	if (!isOpen) return null;

	return (
		<div className="modal-overlay" onClick={onClose}>
			<div className="modal" onClick={(e) => e.stopPropagation()}>
				<div className="modal-header">
					<h2 className="modal-title">Добавить RSS-источник</h2>
					<button className="btn btn-ghost btn-icon" onClick={onClose}>
						<X size={20} />
					</button>
				</div>

				<form onSubmit={handleSubmit}>
					<div className="modal-body">
						<div className="form-group">
							<label className="form-label">URL ленты</label>
							<input
								type="url"
								className={`form-input ${error ? "error" : ""}`}
								placeholder="https://example.com/rss"
								value={url}
								onChange={(e) => setUrl(e.target.value)}
								autoFocus
							/>
							{error && <p className="form-error">{error}</p>}
						</div>

						<div className="form-group">
							<label className="form-label">Категория (необязательно)</label>
							<input
								type="text"
								className="form-input"
								placeholder="Технологии"
								value={category}
								onChange={(e) => setCategory(e.target.value)}
							/>
						</div>
					</div>

					<div className="modal-footer">
						<button
							type="button"
							className="btn btn-secondary"
							onClick={onClose}
						>
							Отмена
						</button>
						<button
							type="submit"
							className="btn btn-primary"
							disabled={loading}
						>
							{loading ? (
								<>
									<span className="spinner" />
									Добавление...
								</>
							) : (
								<>
									<Plus size={18} />
									Добавить
								</>
							)}
						</button>
					</div>
				</form>
			</div>
		</div>
	);
}

function FeedsDropdown({ feeds, selectedFeedId, onSelect }) {
	const [isOpen, setIsOpen] = useState(false);

	const selectedFeed = feeds.find((f) => f.id === selectedFeedId);

	return (
		<div className="feeds-dropdown">
			<button className="btn btn-secondary" onClick={() => setIsOpen(!isOpen)}>
				<Rss size={16} />
				{selectedFeed ? selectedFeed.title : "Все источники"}
				<ChevronDown size={16} />
			</button>

			{isOpen && (
				<div className="feeds-dropdown-menu">
					<div
						className="feeds-dropdown-item"
						onClick={() => {
							onSelect(null);
							setIsOpen(false);
						}}
					>
						<span className="feeds-dropdown-item-title">Все источники</span>
					</div>
					{feeds.map((feed) => (
						<div
							key={feed.id}
							className="feeds-dropdown-item"
							onClick={() => {
								onSelect(feed.id);
								setIsOpen(false);
							}}
						>
							<span className="feeds-dropdown-item-title">{feed.title}</span>
							<span className="feeds-dropdown-item-meta">
								{feed.category || "Без категории"}
							</span>
						</div>
					))}
				</div>
			)}
		</div>
	);
}

function Toast({ message, type, onClose }) {
	useEffect(() => {
		const timer = setTimeout(onClose, 3000);
		return () => clearTimeout(timer);
	}, [onClose]);

	return (
		<div className={`toast ${type}`} onClick={onClose}>
			{message}
		</div>
	);
}

export default function App() {
	const [feeds, setFeeds] = useState([]);
	const [articles, setArticles] = useState([]);
	const [loading, setLoading] = useState(true);
	const [refreshing, setRefreshing] = useState(false);
	const [refreshingId, setRefreshingId] = useState(null);
	const [showAddModal, setShowAddModal] = useState(false);
	const [selectedFeedId, setSelectedFeedId] = useState(null);
	const [selectedTags, setSelectedTags] = useState([]);
	const [searchQuery, setSearchQuery] = useState("");
	const [toast, setToast] = useState(null);

	const allTags = [...new Set(articles.flatMap((a) => a.tags || []))];

	const loadData = useCallback(async () => {
		try {
			const [feedsData, articlesData] = await Promise.all([
				api.getFeeds(),
				api.getArticles({
					feed_id: selectedFeedId,
					tags: selectedTags.length > 0 ? selectedTags : undefined,
					search: searchQuery || undefined,
				}),
			]);
			setFeeds(feedsData);
			setArticles(articlesData);
		} catch (err) {
			console.error("Failed to load data:", err);
			showToast("Ошибка загрузки данных", "error");
		} finally {
			setLoading(false);
		}
	}, [selectedFeedId, selectedTags, searchQuery]);

	useEffect(() => {
		loadData();
	}, [loadData]);

	const handleAddFeed = async (data) => {
		try {
			await api.addFeed(data);
			showToast("Источник добавлен", "success");
			loadData();
		} catch (err) {
			throw err;
		}
	};

	const handleRefreshAll = async () => {
		setRefreshing(true);
		try {
			await api.refreshAll();
			showToast("Лента обновлена", "success");
			loadData();
		} catch (err) {
			showToast("Ошибка обновления", "error");
		} finally {
			setRefreshing(false);
		}
	};

	const handleRefreshArticle = async (articleId) => {
		setRefreshingId(articleId);
		try {
			await api.refreshArticle(articleId);
			showToast("Дайджест обновлён", "success");
			loadData();
		} catch (err) {
			showToast("Ошибка обновления", "error");
		} finally {
			setRefreshingId(null);
		}
	};

	const handleDeleteFeed = async (feedId) => {
		try {
			await api.deleteFeed(feedId);
			showToast("Источник удалён", "success");
			loadData();
		} catch (err) {
			showToast("Ошибка удаления", "error");
		}
	};

	const toggleTag = (tag) => {
		setSelectedTags((prev) =>
			prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag],
		);
	};

	const showToast = (message, type = "info") => {
		setToast({ message, type });
	};

	return (
		<div className="app">
			<header className="header">
				<div className="header-content">
					<a href="/" className="logo">
						<span className="logo-icon">Д</span>
						Дайджест
					</a>

					<div className="header-actions">
						<button
							className="btn btn-secondary"
							onClick={handleRefreshAll}
							disabled={refreshing || feeds.length === 0}
						>
							<RefreshCw size={16} className={refreshing ? "spinner" : ""} />
							{refreshing ? "Обновление..." : "Обновить"}
						</button>

						<button
							className="btn btn-primary"
							onClick={() => setShowAddModal(true)}
						>
							<Plus size={18} />
							Добавить RSS
						</button>
					</div>
				</div>
			</header>

			<main className="main">
				<div className="main-content">
					{feeds.length > 0 && (
						<div className="filter-bar">
							<div className="filter-section">
								<FeedsDropdown
									feeds={feeds}
									selectedFeedId={selectedFeedId}
									onSelect={setSelectedFeedId}
								/>
							</div>

							<div className="search-input">
								<Search size={16} color="#9E9E9E" />
								<input
									type="text"
									placeholder="Поиск..."
									value={searchQuery}
									onChange={(e) => setSearchQuery(e.target.value)}
								/>
								{searchQuery && (
									<button
										className="btn btn-ghost btn-icon"
										onClick={() => setSearchQuery("")}
									>
										<X size={14} />
									</button>
								)}
							</div>

							{allTags.length > 0 && (
								<div className="filter-section">
									<span className="filter-label">Теги:</span>
									<div className="tags-container">
										{allTags.map((tag) => (
											<button
												key={tag}
												className={`tag ${selectedTags.includes(tag) ? "active" : ""}`}
												style={getTagStyle(tag, selectedTags.includes(tag))}
												onClick={() => toggleTag(tag)}
											>
												{tag}
											</button>
										))}
									</div>
								</div>
							)}
						</div>
					)}

					{loading ? (
						<div className="feed-grid">
							{[0, 1, 2].map((i) => (
								<SkeletonCard key={i} index={i} />
							))}
						</div>
					) : articles.length === 0 ? (
						feeds.length === 0 ? (
							<EmptyState onAddFeed={() => setShowAddModal(true)} />
						) : (
							<div className="empty-state">
								<p className="empty-state-text">
									{searchQuery || selectedTags.length > 0
										? "Ничего не найдено. Попробуйте изменить фильтры."
										: "Статьи загружаются..."}
								</p>
							</div>
						)
					) : (
						<>
							<div className="stats">
								<span className="stat">
									<Rss size={14} />
									{articles.length}{" "}
									{articles.length === 1
										? "статья"
										: articles.length < 5
											? "статьи"
											: "статей"}
								</span>
							</div>

							<div className="feed-grid">
								{articles.map((article, index) => (
									<FeedCard
										key={article.id}
										article={article}
										onRefresh={handleRefreshArticle}
										refreshing={refreshingId === article.id}
										style={{ animationDelay: `${index * 80}ms` }}
									/>
								))}
							</div>
						</>
					)}
				</div>
			</main>

			<AddFeedModal
				isOpen={showAddModal}
				onClose={() => setShowAddModal(false)}
				onAdd={handleAddFeed}
			/>

			{toast && (
				<Toast
					message={toast.message}
					type={toast.type}
					onClose={() => setToast(null)}
				/>
			)}
		</div>
	);
}
