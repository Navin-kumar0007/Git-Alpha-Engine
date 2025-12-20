import React from 'react';
import { TrendingUp, Hash } from 'lucide-react';

const TrendingTopics = ({ topics, onTopicClick, loading, className = '' }) => {
    if (loading) {
        return (
            <div className={`glass-card p-4 ${className}`}>
                <div className="flex items-center gap-2 mb-3">
                    <TrendingUp size={18} className="text-[var(--color-gold-light)]" />
                    <h3 className="font-semibold text-slate-100">Trending Topics</h3>
                </div>
                <div className="text-sm text-slate-400">Loading topics...</div>
            </div>
        );
    }

    if (!topics || topics.length === 0) {
        return (
            <div className={`glass-card p-4 ${className}`}>
                <div className="flex items-center gap-2 mb-3">
                    <TrendingUp size={18} className="text-[var(--color-gold-light)]" />
                    <h3 className="font-semibold text-slate-100">Trending Topics</h3>
                </div>
                <div className="text-sm text-slate-400">No trending topics available</div>
            </div>
        );
    }

    // Get max score for scaling
    const maxScore = Math.max(...topics.map(t => t.score || 0));

    return (
        <div className={`glass-card p-4 ${className}`}>
            {/* Header */}
            <div className="flex items-center gap-2 mb-4">
                <TrendingUp size={18} className="text-[var(--color-gold-light)]" />
                <h3 className="font-semibold text-slate-100">Trending Topics</h3>
            </div>

            {/* Topics list */}
            <div className="space-y-2">
                {topics.map((topic, index) => {
                    const scorePercent = maxScore > 0 ? (topic.score / maxScore) * 100 : 0;

                    return (
                        <button
                            key={topic.topic || index}
                            onClick={() => onTopicClick && onTopicClick(topic.topic)}
                            className="w-full text-left group hover:bg-slate-800/50 rounded-lg p-2 transition-all"
                        >
                            <div className="flex items-center justify-between mb-1">
                                <div className="flex items-center gap-2 flex-1 min-w-0">
                                    <Hash size={14} className="text-[var(--color-cyan-light)] flex-shrink-0" />
                                    <span className="text-sm font-medium text-slate-200 group-hover:text-[var(--color-cyan-light)] transition-colors truncate">
                                        {topic.topic}
                                    </span>
                                </div>
                                <span className="text-xs text-slate-400 ml-2 flex-shrink-0">
                                    {topic.article_count} {topic.article_count === 1 ? 'article' : 'articles'}
                                </span>
                            </div>

                            {/* Score bar */}
                            <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-[var(--color-cyan)] to-[var(--color-purple)] transition-all duration-300"
                                    style={{ width: `${scorePercent}%` }}
                                />
                            </div>
                        </button>
                    );
                })}
            </div>

            {/* Footer note */}
            <div className="mt-3 pt-3 border-t border-slate-700/50">
                <p className="text-xs text-slate-500 text-center">
                    Based on last 7 days of articles
                </p>
            </div>
        </div>
    );
};

export default TrendingTopics;
