import React from 'react';
import { Filter, X, TrendingUp } from 'lucide-react';

const NewsFilters = ({ filters, onChange, onReset, className = '' }) => {
    const updateFilter = (key, value) => {
        onChange({ ...filters, [key]: value });
    };

    const categories = ['business', 'technology', 'crypto', 'finance'];
    const sentiments = ['positive', 'neutral', 'negative'];
    const tickers = ['BTC', 'ETH', 'SOL', 'ADA', 'DOT', 'MATIC', 'LINK'];

    return (
        <div className={` glass-card p-4 ${className}`}>
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <Filter size={18} className="text-[var(--color-purple-light)]" />
                    <h3 className="font-semibold text-slate-100">Filters</h3>
                </div>
                {(filters.category || filters.sentiment || filters.ticker) && (
                    <button
                        onClick={onReset}
                        className="text-xs text-slate-400 hover:text-[var(--color-pink-light)] flex items-center gap-1 transition-all"
                    >
                        <X size={12} />
                        Clear
                    </button>
                )}
            </div>

            {/* Category Filter */}
            <div className="mb-4">
                <label className="block text-xs text-slate-400 mb-2">Category</label>
                <select
                    value={filters.category || ''}
                    onChange={(e) => updateFilter('category', e.target.value || null)}
                    className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-[var(--color-purple)] focus:ring-1 focus:ring-[var(--color-purple)]/50 transition-all"
                >
                    <option value="">All Categories</option>
                    {categories.map((cat) => (
                        <option key={cat} value={cat}>
                            {cat.charAt(0).toUpperCase() + cat.slice(1)}
                        </option>
                    ))}
                </select>
            </div>

            {/* Sentiment Filter */}
            <div className="mb-4">
                <label className="block text-xs text-slate-400 mb-2">Sentiment</label>
                <div className="flex flex-wrap gap-2">
                    {sentiments.map((sent) => {
                        const isActive = filters.sentiment === sent;
                        const colors = {
                            positive: 'emerald',
                            negative: 'pink',
                            neutral: 'cyan',
                        };
                        const color = colors[sent];

                        return (
                            <button
                                key={sent}
                                onClick={() => updateFilter('sentiment', isActive ? null : sent)}
                                className={`px-3 py-1.5 rounded-lg text-xs border transition-all ${isActive
                                        ? `bg-[var(--color-${color})]/20 border-[var(--color-${color})]/40 text-[var(--color-${color}-light)]`
                                        : 'border-slate-700 text-slate-400 hover:bg-slate-800/50'
                                    }`}
                            >
                                {sent.charAt(0).toUpperCase() + sent.slice(1)}
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* Ticker Filter */}
            <div className="mb-4">
                <label className="block text-xs text-slate-400 mb-2">Ticker</label>
                <select
                    value={filters.ticker || ''}
                    onChange={(e) => updateFilter('ticker', e.target.value || null)}
                    className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-[var(--color-cyan)] focus:ring-1 focus:ring-[var(--color-cyan)]/50 transition-all"
                >
                    <option value="">All Tickers</option>
                    {tickers.map((ticker) => (
                        <option key={ticker} value={ticker}>
                            {ticker}
                        </option>
                    ))}
                </select>
            </div>

            {/* Portfolio Toggle */}
            <div className="pt-3 border-t border-slate-700/50">
                <label className="flex items-center gap-2 cursor-pointer">
                    <input
                        type="checkbox"
                        checked={filters.portfolioOnly || false}
                        onChange={(e) => updateFilter('portfolioOnly', e.target.checked)}
                        className="w-4 h-4 rounded border-slate-600 bg-slate-800 text-[var(--color-purple)] focus:ring-[var(--color-purple)]/50"
                    />
                    <span className="text-sm text-slate-300">Portfolio News Only</span>
                </label>
            </div>
        </div>
    );
};

export default NewsFilters;
