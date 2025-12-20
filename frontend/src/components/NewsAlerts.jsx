import React from 'react';
import { Bell, BellOff, Check, ExternalLink, AlertTriangle } from 'lucide-react';

const NewsAlerts = ({ alerts, loading, onMarkRead, onViewArticle }) => {
    const unreadCount = alerts.filter(a => !a.is_read).length;

    if (loading) {
        return (
            <div className="glass-card p-4">
                <div className="text-sm text-slate-400">Loading alerts...</div>
            </div>
        );
    }

    return (
        <div className="glass-card p-4">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <Bell size={18} className="text-[var(--color-gold-light)]" />
                    <h3 className="font-semibold text-slate-100">News Alerts</h3>
                    {unreadCount > 0 && (
                        <span className="px-2 py-0.5 rounded-full bg-[var(--color-pink)]/20 text-[var(--color-pink-light)] text-xs">
                            {unreadCount} new
                        </span>
                    )}
                </div>
            </div>

            {/* Alerts list */}
            {alerts.length === 0 ? (
                <div className="text-center py-6">
                    <BellOff size={32} className="mx-auto text-slate-600 mb-2" />
                    <p className="text-sm text-slate-400">No alerts yet</p>
                    <p className="text-xs text-slate-500 mt-1">
                        Alerts will appear when high-impact news affects your portfolio
                    </p>
                </div>
            ) : (
                <div className="space-y-2 max-h-96 overflow-y-auto custom-scrollbar">
                    {alerts.map((alert) => (
                        <div
                            key={alert.id}
                            className={`p-3 rounded-lg border transition-all ${alert.is_read
                                    ? 'bg-slate-800/30 border-slate-700/50'
                                    : 'bg-[var(--color-gold)]/5 border-[var(--color-gold)]/30'
                                }`}
                        >
                            {/* Alert header */}
                            <div className="flex items-start justify-between gap-2 mb-2">
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-1">
                                        <AlertTriangle
                                            size={14}
                                            className={alert.is_read ? 'text-slate-500' : 'text-[var(--color-gold-light)]'}
                                        />
                                        <span className="text-xs font-medium text-slate-300">
                                            {alert.alert_type === 'portfolio_impact' ? 'Portfolio Impact' : alert.alert_type}
                                        </span>
                                        <span className="text-xs text-slate-500">
                                            {new Date(alert.triggered_at).toLocaleDateString()}
                                        </span>
                                    </div>
                                    <p className="text-sm text-slate-300">
                                        {alert.trigger_reason}
                                    </p>
                                </div>

                                {/* Mark as read button */}
                                {!alert.is_read && (
                                    <button
                                        onClick={() => onMarkRead(alert.id)}
                                        className="p-1 rounded hover:bg-slate-700/50 text-slate-400 hover:text-[var(--color-cyan-light)] transition-all"
                                        title="Mark as read"
                                    >
                                        <Check size={16} />
                                    </button>
                                )}
                            </div>

                            {/* Article link */}
                            {alert.article && (
                                <div className="mt-2 pt-2 border-t border-slate-700/50">
                                    <button
                                        onClick={() => onViewArticle(alert.article)}
                                        className="text-xs text-[var(--color-cyan-light)] hover:text-[var(--color-cyan)] flex items-center gap-1 transition-all"
                                    >
                                        <ExternalLink size={12} />
                                        View Article
                                    </button>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default NewsAlerts;
