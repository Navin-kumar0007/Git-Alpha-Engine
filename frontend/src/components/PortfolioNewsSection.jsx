import React from 'react';
import { Wallet, AlertTriangle, Loader2 } from 'lucide-react';
import ArticleCard from './ArticleCard';

const PortfolioNewsSection = ({
    articles,
    portfolioTickers,
    loading,
    onBookmark,
    bookmarkedIds,
    onCreateAlerts
}) => {
    if (loading) {
        return (
            <div className="glass-card p-6">
                <div className="flex items-center justify-center gap-2 text-slate-400">
                    <Loader2 className="animate-spin" size={20} />
                    <span>Loading portfolio news...</span>
                </div>
            </div>
        );
    }

    if (portfolioTickers.length === 0) {
        return (
            <div className="glass-card p-6 text-center">
                <Wallet size={48} className="mx-auto text-slate-600 mb-3" />
                <h3 className="text-lg font-semibold text-slate-300 mb-2">No Portfolio Assets</h3>
                <p className="text-sm text-slate-400">
                    Add assets to your portfolio to see relevant news
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {/* Header with portfolio tickers */}
            <div className="glass-card p-4">
                <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                        <Wallet size={18} className="text-[var(--color-purple-light)]" />
                        <h3 className="font-semibold text-slate-100">Your Portfolio News</h3>
                    </div>
                    <button
                        onClick={onCreateAlerts}
                        className="text-xs px-3 py-1.5 rounded-lg border border-[var(--color-gold)]/40 hover:bg-[var(--color-gold)]/10 text-[var(--color-gold-light)] flex items-center gap-1 transition-all"
                    >
                        <AlertTriangle size={12} />
                        Create Alerts
                    </button>
                </div>

                {/* Portfolio tickers */}
                <div className="flex flex-wrap gap-2">
                    <span className="text-xs text-slate-400">Tracking:</span>
                    {portfolioTickers.map((ticker) => (
                        <span
                            key={ticker}
                            className="px-2 py-1 rounded text-xs bg-[var(--color-purple)]/10 text-[var(--color-purple-light)] border border-[var(--color-purple)]/30"
                        >
                            {ticker}
                        </span>
                    ))}
                </div>
            </div>

            {/* Articles */}
            {articles.length === 0 ? (
                <div className="glass-card p-6 text-center">
                    <p className="text-sm text-slate-400">
                        No recent news for your portfolio assets
                    </p>
                </div>
            ) : (
                <div className="space-y-3">
                    {articles.map((article) => (
                        <ArticleCard
                            key={article.id}
                            article={article}
                            onBookmark={onBookmark}
                            isBookmarked={bookmarkedIds.includes(article.id)}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

export default PortfolioNewsSection;
