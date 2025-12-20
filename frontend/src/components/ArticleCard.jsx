import React from 'react';
import {
    ExternalLink,
    Bookmark,
    BookmarkCheck,
    TrendingUp,
    TrendingDown,
    Minus,
    Calendar,
    Tag as TagIcon
} from 'lucide-react';

const ArticleCard = ({ article, onBookmark, isBookmarked, onReadMore }) => {
    // Determine sentiment color and label
    const getSentimentInfo = (score) => {
        if (!score && score !== 0) return { label: 'Neutral', color: 'cyan', icon: Minus };
        if (score > 0.3) return { label: 'Positive', color: 'emerald', icon: TrendingUp };
        if (score < -0.3) return { label: 'Negative', color: 'pink', icon: TrendingDown };
        return { label: 'Neutral', color: 'cyan', icon: Minus };
    };

    // Determine impact badge color
    const getImpactColor = (impact) => {
        if (!impact) return 'slate';
        if (impact >= 8) return 'gold';
        if (impact >= 5) return 'purple';
        return 'slate';
    };

    const sentiment = getSentimentInfo(article.sentiment_score);
    const impactColor = getImpactColor(article.impact_score);
    const SentimentIcon = sentiment.icon;

    // Parse tickers if stored as JSON string
    const tickers = React.useMemo(() => {
        if (!article.related_tickers) return [];
        try {
            return typeof article.related_tickers === 'string'
                ? JSON.parse(article.related_tickers)
                : article.related_tickers;
        } catch {
            return [];
        }
    }, [article.related_tickers]);

    const formatDate = (dateString) => {
        if (!dateString) return '';
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));

        if (diffHours < 1) return 'Just now';
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffHours < 48) return 'Yesterday';
        return date.toLocaleDateString();
    };

    return (
        <div className={`glass-card hover-lift p-4 border-l-4 border-[var(--color-${sentiment.color})]`}>
            {/* Header */}
            <div className="flex justify-between items-start gap-3 mb-3">
                <div className="flex-1 min-w-0">
                    <h3 className="text-base font-semibold text-slate-100 leading-snug line-clamp-2 mb-2">
                        {article.title}
                    </h3>
                    <div className="flex items-center gap-2 text-xs text-slate-400">
                        {article.source_name && (
                            <span className="font-medium">{article.source_name}</span>
                        )}
                        {article.published_at && (
                            <>
                                <span>•</span>
                                <span className="flex items-center gap-1">
                                    <Calendar size={12} />
                                    {formatDate(article.published_at)}
                                </span>
                            </>
                        )}
                    </div>
                </div>

                {/* Image thumbnail */}
                {article.image_url && (
                    <img
                        src={article.image_url}
                        alt={article.title}
                        className="w-20 h-20 object-cover rounded-lg border border-slate-700/50"
                        onError={(e) => e.target.style.display = 'none'}
                    />
                )}
            </div>

            {/* Description */}
            {article.description && (
                <p className="text-sm text-slate-300 line-clamp-2 mb-3">
                    {article.description}
                </p>
            )}

            {/* Summary (if available) */}
            {article.summary && article.summary !== article.description && (
                <div className="bg-slate-800/40 border border-slate-700/50 rounded-lg p-2 mb-3">
                    <div className="flex items-center gap-1 text-xs text-slate-400 mb-1">
                        <span className="text-[var(--color-purple-light)]">AI Summary:</span>
                    </div>
                    <p className="text-xs text-slate-300 line-clamp-2">{article.summary}</p>
                </div>
            )}

            {/* Metadata badges */}
            <div className="flex flex-wrap items-center gap-2 mb-3">
                {/* Sentiment */}
                <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full border text-[10px] uppercase tracking-wide bg-[var(--color-${sentiment.color})]/10 border-[var(--color-${sentiment.color})]/40 text-[var(--color-${sentiment.color}-light)]`}>
                    <SentimentIcon size={10} />
                    {sentiment.label}
                </span>

                {/* Impact score */}
                {article.impact_score && (
                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full border text-[10px] uppercase tracking-wide bg-[var(--color-${impactColor})]/10 border-[var(--color-${impactColor})]/40 text-[var(--color-${impactColor}-light)]`}>
                        Impact: {article.impact_score}/10
                    </span>
                )}

                {/* Tickers */}
                {tickers.length > 0 && tickers.slice(0, 3).map((ticker) => (
                    <span
                        key={ticker}
                        className="px-2 py-0.5 rounded text-[10px] bg-[var(--color-cyan)]/10 text-[var(--color-cyan-light)] border border-[var(--color-cyan)]/30"
                    >
                        #{ticker}
                    </span>
                ))}
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between pt-3 border-t border-slate-700/50">
                <div className="flex items-center gap-2">
                    {/* Read more button */}
                    <a
                        href={article.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs px-3 py-1.5 rounded-lg bg-[image:var(--gradient-primary)] hover:shadow-[var(--shadow-glow)] text-white transition-all flex items-center gap-1"
                    >
                        <ExternalLink size={12} />
                        Read Full Article
                    </a>
                </div>

                {/* Bookmark button */}
                <button
                    onClick={() => onBookmark(article.id)}
                    className={`p-2 rounded-lg border transition-all ${isBookmarked
                            ? 'bg-[var(--color-gold)]/20 border-[var(--color-gold)]/40 text-[var(--color-gold-light)]'
                            : 'border-slate-600 text-slate-400 hover:bg-slate-800/50'
                        }`}
                    title={isBookmarked ? 'Remove bookmark' : 'Bookmark article'}
                >
                    {isBookmarked ? <BookmarkCheck size={16} /> : <Bookmark size={16} />}
                </button>
            </div>
        </div>
    );
};

export default ArticleCard;
