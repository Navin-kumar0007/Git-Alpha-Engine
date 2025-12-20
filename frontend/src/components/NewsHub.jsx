import React, { useState, useEffect } from 'react';
import { Newspaper, RefreshCw, Loader2, Search, X } from 'lucide-react';
import ArticleCard from './ArticleCard';
import NewsFilters from './NewsFilters';
import TrendingTopics from './TrendingTopics';
import PortfolioNewsSection from './PortfolioNewsSection';
import NewsAlerts from './NewsAlerts';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const getAuthHeaders = () => {
    const token = localStorage.getItem('git_alpha_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
};

const NewsHub = ({ user }) => {
    // State
    const [activeView, setActiveView] = useState('all'); // 'all', 'portfolio', 'alerts'
    const [articles, setArticles] = useState([]);
    const [portfolioNews, setPortfolioNews] = useState([]);
    const [portfolioTickers, setPortfolioTickers] = useState([]);
    const [alerts, setAlerts] = useState([]);
    const [trendingTopics, setTrendingTopics] = useState([]);
    const [bookmarkedIds, setBookmarkedIds] = useState([]);

    // Loading states
    const [loading, setLoading] = useState(false);
    const [portfolioLoading, setPortfolioLoading] = useState(false);
    const [alertsLoading, setAlertsLoading] = useState(false);
    const [trendingLoading, setTrendingLoading] = useState(false);

    // Filters
    const [filters, setFilters] = useState({
        category: null,
        sentiment: null,
        ticker: null,
        portfolioOnly: false,
    });

    // Pagination
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);

    // Fetch all articles
    const fetchArticles = async (resetPage = false) => {
        setLoading(true);
        try {
            const params = new URLSearchParams({
                page: resetPage ? 1 : page,
                page_size: 20,
            });

            if (filters.category) params.append('category', filters.category);
            if (filters.sentiment) params.append('sentiment', filters.sentiment);
            if (filters.ticker) params.append('ticker', filters.ticker);

            const res = await fetch(`${API_URL}/api/news/articles?${params}`);
            const data = await res.json();

            if (resetPage) {
                setArticles(data.articles || []);
                setPage(1);
            } else {
                setArticles((prev) => [...prev, ...(data.articles || [])]);
            }

            setHasMore((data.articles || []).length >= 20);
        } catch (error) {
            console.error('Error fetching articles:', error);
        } finally {
            setLoading(false);
        }
    };

    // Fetch portfolio news
    const fetchPortfolioNews = async () => {
        if (!user) return;
        setPortfolioLoading(true);
        try {
            const res = await fetch(`${API_URL}/api/news/portfolio/news?days=7&limit=50`, {
                headers: getAuthHeaders(),
            });
            const data = await res.json();
            setPortfolioNews(data.articles || []);
            setPortfolioTickers(data.portfolio_tickers || []);
        } catch (error) {
            console.error('Error fetching portfolio news:', error);
        } finally {
            setPortfolioLoading(false);
        }
    };

    // Fetch alerts
    const fetchAlerts = async () => {
        if (!user) return;
        setAlertsLoading(true);
        try {
            const res = await fetch(`${API_URL}/api/news/alerts?limit=20`, {
                headers: getAuthHeaders(),
            });
            const data = await res.json();
            setAlerts(data.alerts || []);
        } catch (error) {
            console.error('Error fetching alerts:', error);
        } finally {
            setAlertsLoading(false);
        }
    };

    // Fetch trending topics
    const fetchTrendingTopics = async () => {
        setTrendingLoading(true);
        try {
            const res = await fetch(`${API_URL}/api/news/articles/trending?days=7&limit=10`);
            const data = await res.json();
            setTrendingTopics(data.topics || []);
        } catch (error) {
            console.error('Error fetching trending topics:', error);
        } finally {
            setTrendingLoading(false);
        }
    };

    // Fetch bookmarks
    const fetchBookmarks = async () => {
        if (!user) return;
        try {
            const res = await fetch(`${API_URL}/api/news/bookmarks`, {
                headers: getAuthHeaders(),
            });
            const data = await res.json();
            setBookmarkedIds(data.map((b) => b.article_id));
        } catch (error) {
            console.error('Error fetching bookmarks:', error);
        }
    };

    // Handle bookmark toggle
    const handleBookmark = async (articleId) => {
        if (!user) return;

        const isBookmarked = bookmarkedIds.includes(articleId);

        try {
            if (isBookmarked) {
                // Find bookmark and delete
                const res = await fetch(`${API_URL}/api/news/bookmarks`, {
                    headers: getAuthHeaders(),
                });
                const bookmarks = await res.json();
                const bookmark = bookmarks.find((b) => b.article_id === articleId);

                if (bookmark) {
                    await fetch(`${API_URL}/api/news/bookmarks/${bookmark.id}`, {
                        method: 'DELETE',
                        headers: getAuthHeaders(),
                    });
                    setBookmarkedIds((prev) => prev.filter((id) => id !== articleId));
                }
            } else {
                // Create bookmark
                await fetch(`${API_URL}/api/news/bookmarks`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...getAuthHeaders(),
                    },
                    body: JSON.stringify({ article_id: articleId }),
                });
                setBookmarkedIds((prev) => [...prev, articleId]);
            }
        } catch (error) {
            console.error('Error toggling bookmark:', error);
        }
    };

    // Create portfolio alerts
    const handleCreateAlerts = async () => {
        if (!user) return;
        try {
            const res = await fetch(`${API_URL}/api/news/portfolio/alerts?threshold=7`, {
                method: 'POST',
                headers: getAuthHeaders(),
            });
            const data = await res.json();
            alert(`Created ${data.created_alerts} new alerts for your portfolio`);
            fetchAlerts();
        } catch (error) {
            console.error('Error creating alerts:', error);
        }
    };

    // Mark alert as read
    const handleMarkRead = async (alertId) => {
        if (!user) return;
        try {
            await fetch(`${API_URL}/api/news/alerts/${alertId}/read`, {
                method: 'PUT',
                headers: getAuthHeaders(),
            });
            setAlerts((prev) =>
                prev.map((a) => (a.id === alertId ? { ...a, is_read: true } : a))
            );
        } catch (error) {
            console.error('Error marking alert as read:', error);
        }
    };

    // Handle topic click (filter by topic)
    const handleTopicClick = (topic) => {
        // For simplicity, search for topic in article titles/descriptions
        // In a real app, you'd have a proper search/filter endpoint
        setActiveView('all');
        fetchArticles(true);
    };

    // Initial load
    useEffect(() => {
        fetchArticles(true);
        fetchTrendingTopics();
        if (user) {
            fetchBookmarks();
            fetchAlerts();
        }
    }, [user]);

    // Refetch when filters change
    useEffect(() => {
        fetchArticles(true);
    }, [filters.category, filters.sentiment, filters.ticker]);

    // Fetch portfolio news when switching to portfolio view
    useEffect(() => {
        if (activeView === 'portfolio' && user) {
            fetchPortfolioNews();
        }
    }, [activeView, user]);

    // Load more articles
    const loadMore = () => {
        setPage((prev) => prev + 1);
        fetchArticles(false);
    };

    // Reset filters
    const handleResetFilters = () => {
        setFilters({
            category: null,
            sentiment: null,
            ticker: null,
            portfolioOnly: false,
        });
    };

    return (
        <div className="min-h-screen bg-transparent">
            {/* Header */}
            <div className="mb-6">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <div className="p-3 rounded-xl bg-[image:var(--gradient-primary)]">
                            <Newspaper size={24} className="text-white" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-slate-100">News Hub</h1>
                            <p className="text-sm text-slate-400">
                                AI-powered news aggregation & portfolio alerts
                            </p>
                        </div>
                    </div>

                    <button
                        onClick={() => {
                            fetchArticles(true);
                            fetchTrendingTopics();
                            if (activeView === 'portfolio') fetchPortfolioNews();
                            if (activeView === 'alerts') fetchAlerts();
                        }}
                        className="px-4 py-2 rounded-lg border border-[var(--color-cyan)]/40 hover:bg-[var(--color-cyan)]/10 text-[var(--color-cyan-light)] flex items-center gap-2 transition-all"
                    >
                        <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
                        Refresh
                    </button>
                </div>

                {/* View tabs */}
                <div className="flex gap-2">
                    {['all', 'portfolio', 'alerts'].map((view) => (
                        <button
                            key={view}
                            onClick={() => setActiveView(view)}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeView === view
                                ? 'bg-[image:var(--gradient-primary)] text-white'
                                : 'border border-slate-700 text-slate-400 hover:bg-slate-800/50'
                                }`}
                        >
                            {view.charAt(0).toUpperCase() + view.slice(1)}
                        </button>
                    ))}
                </div>
            </div>

            {/* Main content */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Sidebar */}
                <div className="lg:col-span-3 space-y-4">
                    <NewsFilters
                        filters={filters}
                        onChange={setFilters}
                        onReset={handleResetFilters}
                    />
                    <TrendingTopics
                        topics={trendingTopics}
                        loading={trendingLoading}
                        onTopicClick={handleTopicClick}
                    />
                </div>

                {/* Main feed */}
                <div className="lg:col-span-9">
                    {activeView === 'all' && (
                        <div className="space-y-4">
                            {loading && articles.length === 0 ? (
                                <div className="glass-card p-12 text-center">
                                    <Loader2 className="animate-spin mx-auto mb-3 text-[var(--color-purple-light)]" size={32} />
                                    <p className="text-slate-400">Loading news articles...</p>
                                </div>
                            ) : articles.length === 0 ? (
                                <div className="glass-card p-12 text-center">
                                    <Newspaper className="mx-auto mb-3 text-slate-600" size={48} />
                                    <p className="text-slate-400">No articles found</p>
                                </div>
                            ) : (
                                <>
                                    <div className="space-y-3">
                                        {articles.map((article) => (
                                            <ArticleCard
                                                key={article.id}
                                                article={article}
                                                onBookmark={handleBookmark}
                                                isBookmarked={bookmarkedIds.includes(article.id)}
                                            />
                                        ))}
                                    </div>

                                    {/* Load more */}
                                    {hasMore && !loading && (
                                        <div className="text-center mt-6">
                                            <button
                                                onClick={loadMore}
                                                className="px-6 py-3 rounded-lg bg-[image:var(--gradient-primary)] hover:shadow-[var(--shadow-glow)] text-white transition-all"
                                            >
                                                Load More
                                            </button>
                                        </div>
                                    )}
                                </>
                            )}
                        </div>
                    )}

                    {activeView === 'portfolio' && (
                        <PortfolioNewsSection
                            articles={portfolioNews}
                            portfolioTickers={portfolioTickers}
                            loading={portfolioLoading}
                            onBookmark={handleBookmark}
                            bookmarkedIds={bookmarkedIds}
                            onCreateAlerts={handleCreateAlerts}
                        />
                    )}

                    {activeView === 'alerts' && (
                        <NewsAlerts
                            alerts={alerts}
                            loading={alertsLoading}
                            onMarkRead={handleMarkRead}
                            onViewArticle={(article) => {
                                // Scroll to article or show modal
                                console.log('View article:', article);
                            }}
                        />
                    )}
                </div>
            </div>
        </div>
    );
};

export default NewsHub;
