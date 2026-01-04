import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Minus, AlertCircle, RefreshCw, ArrowUp, ArrowDown } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const getAuthHeaders = () => {
    const token = localStorage.getItem('git_alpha_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
};

/**
 * Symbol Analytics Component
 * Displays AI-powered stock analysis with signals and insights
 */
const SymbolAnalytics = ({ symbol }) => {
    const [analytics, setAnalytics] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (symbol && symbol.symboltoken) {
            fetchAnalytics();
        }
    }, [symbol]);

    const fetchAnalytics = async () => {
        if (!symbol || !symbol.symboltoken) return;

        setLoading(true);
        setError(null);

        try {
            const res = await fetch(
                `${API_URL}/api/angel-historical/analytics/${symbol.symboltoken}?exchange=${symbol.exchange || 'NSE'}`,
                { headers: getAuthHeaders() }
            );

            const data = await res.json();

            if (data.success) {
                setAnalytics(data.analytics);
            } else {
                setError(data.error || 'Failed to fetch analytics');
            }
        } catch (err) {
            console.error('Analytics fetch error:', err);
            setError('Failed to load analytics');
        } finally {
            setLoading(false);
        }
    };

    if (!symbol) {
        return (
            <div className="glass-card flex items-center justify-center h-64">
                <p className="text-slate-400 text-sm">Select a symbol to view analytics</p>
            </div>
        );
    }

    if (loading) {
        return (
            <div className="glass-card flex flex-col items-center justify-center h-64">
                <RefreshCw className="animate-spin text-indigo-400 mb-2" size={32} />
                <p className="text-slate-400 text-sm">Analyzing {symbol.name}...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="glass-card p-4">
                <div className="flex items-start gap-3 text-red-400">
                    <AlertCircle size={20} className="flex-shrink-0 mt-0.5" />
                    <div>
                        <p className="font-semibold text-sm">Analytics Error</p>
                        <p className="text-xs mt-1">{error}</p>
                        <button
                            onClick={fetchAnalytics}
                            className="mt-2 text-xs text-indigo-400 hover:text-indigo-300"
                        >
                            Retry
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    if (!analytics || analytics.error) {
        return (
            <div className="glass-card p-4">
                <p className="text-slate-400 text-sm">{analytics?.error || 'No analytics available'}</p>
            </div>
        );
    }

    // Signal badge styling
    const getSignalStyle = (signal) => {
        const styles = {
            'BUY': 'bg-green-500/20 text-green-400 border-green-500/40',
            'SELL': 'bg-red-500/20 text-red-400 border-red-500/40',
            'HOLD': 'bg-yellow-500/20 text-yellow-400 border-yellow-500/40'
        };
        return styles[signal] || styles['HOLD'];
    };

    // Trend icon
    const getTrendIcon = (trend) => {
        if (trend === 'BULLISH') return <TrendingUp size={16} className="text-green-400" />;
        if (trend === 'BEARISH') return <TrendingDown size={16} className="text-red-400" />;
        return <Minus size={16} className="text-yellow-400" />;
    };

    return (
        <div className="space-y-4">
            {/* Signal Card */}
            <div className="glass-card p-4">
                <div className="flex items-center justify-between mb-3">
                    <h3 className="text-sm font-semibold">Signal</h3>
                    <button
                        onClick={fetchAnalytics}
                        className="text-slate-400 hover:text-white transition-colors"
                        title="Refresh analytics"
                    >
                        <RefreshCw size={14} />
                    </button>
                </div>

                <div className={`px-4 py-3 rounded-lg border ${getSignalStyle(analytics.signal)} mb-3`}>
                    <div className="flex items-center justify-between">
                        <span className="text-2xl font-bold">{analytics.signal}</span>
                        <span className="text-sm opacity-75">{analytics.confidence}% confidence</span>
                    </div>
                </div>

                <div className="flex items-center gap-2 mb-2">
                    {getTrendIcon(analytics.trend)}
                    <span className="text-sm font-medium">
                        {analytics.trend} <span className="text-slate-400">({analytics.strength})</span>
                    </span>
                </div>

                {/* ML Indicator Badge */}
                {analytics.signal_source && analytics.signal_source !== 'TRADITIONAL' && (
                    <div className={`mt-3 px-3 py-2 rounded-md text-xs font-medium ${analytics.signal_source === 'HYBRID_AGREEMENT'
                            ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/40'
                            : 'bg-purple-500/20 text-purple-300 border border-purple-500/40'
                        }`}>
                        <div className="flex items-center gap-2">
                            <span>🤖</span>
                            <span>
                                {analytics.signal_source === 'HYBRID_AGREEMENT'
                                    ? 'AI + Indicators Agree'
                                    : 'AI High Confidence'}
                            </span>
                            {analytics.ml_prediction && (
                                <span className="opacity-75 ml-auto">
                                    AI: {analytics.ml_prediction.probability ?
                                        `${(analytics.ml_prediction.probability * 100).toFixed(0)}%` :
                                        `${analytics.ml_prediction.confidence}%`}
                                </span>
                            )}
                        </div>
                    </div>
                )}

                <p className="text-xs text-slate-400 leading-relaxed mt-2">
                    {analytics.summary}
                </p>
            </div>

            {/* Technical Indicators */}
            <div className="glass-card p-4">
                <h3 className="text-sm font-semibold mb-3">Technical Indicators</h3>

                <div className="space-y-3">
                    {/* RSI */}
                    {analytics.indicators.rsi && (
                        <div>
                            <div className="flex items-center justify-between text-xs mb-1">
                                <span className="text-slate-400">RSI (14)</span>
                                <span className="font-semibold">{analytics.indicators.rsi}</span>
                            </div>
                            <div className="w-full bg-slate-800 rounded-full h-1.5">
                                <div
                                    className={`h-1.5 rounded-full ${analytics.indicators.rsi > 70
                                        ? 'bg-red-500'
                                        : analytics.indicators.rsi < 30
                                            ? 'bg-green-500'
                                            : 'bg-yellow-500'
                                        }`}
                                    style={{ width: `${analytics.indicators.rsi}%` }}
                                />
                            </div>
                            <p className="text-xs text-slate-500 mt-1">{analytics.indicators.rsi_interpretation}</p>
                        </div>
                    )}

                    {/* MACD */}
                    {analytics.indicators.macd && (
                        <div>
                            <div className="flex items-center justify-between text-xs mb-1">
                                <span className="text-slate-400">MACD</span>
                                <span className="font-semibold">{analytics.indicators.macd.histogram > 0 ? '+' : ''}{analytics.indicators.macd.histogram}</span>
                            </div>
                            <p className="text-xs text-slate-500">{analytics.indicators.macd_signal}</p>
                        </div>
                    )}

                    {/* Moving Averages */}
                    <div className="text-xs space-y-1">
                        {analytics.indicators.sma_20 && (
                            <div className="flex justify-between">
                                <span className="text-slate-400">SMA (20)</span>
                                <span className="font-mono">₹{analytics.indicators.sma_20.toLocaleString()}</span>
                            </div>
                        )}
                        {analytics.indicators.sma_50 && (
                            <div className="flex justify-between">
                                <span className="text-slate-400">SMA (50)</span>
                                <span className="font-mono">₹{analytics.indicators.sma_50.toLocaleString()}</span>
                            </div>
                        )}
                        {analytics.indicators.sma_200 && (
                            <div className="flex justify-between">
                                <span className="text-slate-400">SMA (200)</span>
                                <span className="font-mono">₹{analytics.indicators.sma_200.toLocaleString()}</span>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Volume Analysis - NEW! */}
            {analytics.volume && (
                <div className="glass-card p-4">
                    <h3 className="text-sm font-semibold mb-3">Volume Analysis</h3>
                    <div className="space-y-3">
                        {/* Volume Ratio */}
                        <div>
                            <div className="flex items-center justify-between text-xs mb-1">
                                <span className="text-slate-400">Volume Ratio</span>
                                <span className={`font-semibold ${analytics.volume.volume_ratio > 1.5 ? 'text-green-400' :
                                    analytics.volume.volume_ratio < 0.7 ? 'text-red-400' :
                                        'text-yellow-400'
                                    }`}>
                                    {analytics.volume.volume_ratio}x
                                </span>
                            </div>
                            <div className="w-full bg-slate-800 rounded-full h-1.5">
                                <div
                                    className={`h-1.5 rounded-full ${analytics.volume.volume_ratio > 1.5 ? 'bg-green-500' :
                                        analytics.volume.volume_ratio < 0.7 ? 'bg-red-500' :
                                            'bg-yellow-500'
                                        }`}
                                    style={{ width: `${Math.min(analytics.volume.volume_ratio * 50, 100)}%` }}
                                />
                            </div>
                            <p className="text-xs text-slate-500 mt-1">
                                {analytics.volume.volume_ratio > 1.5 ? 'High volume confirms movement' :
                                    analytics.volume.volume_ratio < 0.7 ? 'Low volume - weak signal' :
                                        'Normal volume'}
                            </p>
                        </div>

                        {/* Volume Trend */}
                        <div className="flex justify-between text-xs">
                            <span className="text-slate-400">Trend</span>
                            <span className={`font-semibold ${analytics.volume.trend === 'INCREASING' ? 'text-green-400' :
                                analytics.volume.trend === 'DECREASING' ? 'text-red-400' :
                                    'text-yellow-400'
                                }`}>
                                {analytics.volume.trend}
                            </span>
                        </div>

                        {/* Price-Volume Correlation */}
                        <div className="flex justify-between text-xs">
                            <span className="text-slate-400">Correlation</span>
                            <span className={`font-semibold ${analytics.volume.price_volume_correlation === 'CONFIRMATORY' ? 'text-green-400' :
                                analytics.volume.price_volume_correlation === 'DIVERGENT' ? 'text-red-400' :
                                    'text-yellow-400'
                                }`}>
                                {analytics.volume.price_volume_correlation}
                            </span>
                        </div>

                        {/* Current vs Average */}
                        <div className="text-xs space-y-1 pt-2 border-t border-slate-700">
                            <div className="flex justify-between">
                                <span className="text-slate-400">Current Volume</span>
                                <span className="font-mono">{(analytics.volume.current_volume / 1000000).toFixed(2)}M</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-slate-400">Avg Volume (20d)</span>
                                <span className="font-mono">{(analytics.volume.avg_volume / 1000000).toFixed(2)}M</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Key Levels */}
            {analytics.levels && (
                <div className="glass-card p-4">
                    <h3 className="text-sm font-semibold mb-3">Key Levels</h3>
                    <div className="space-y-2 text-xs">
                        <div className="flex justify-between items-center">
                            <span className="text-red-400 flex items-center gap-1">
                                <ArrowDown size={12} />
                                Support
                            </span>
                            <span className="font-mono font-semibold">₹{analytics.levels.support.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-green-400 flex items-center gap-1">
                                <ArrowUp size={12} />
                                Resistance
                            </span>
                            <span className="font-mono font-semibold">₹{analytics.levels.resistance.toLocaleString()}</span>
                        </div>
                    </div>
                </div>
            )}

            {/* Performance */}
            {analytics.performance && Object.keys(analytics.performance).length > 0 && (
                <div className="glass-card p-4">
                    <h3 className="text-sm font-semibold mb-3">Performance</h3>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                        {analytics.performance.week_return !== undefined && (
                            <div>
                                <span className="text-slate-400 block">1 Week</span>
                                <span className={`font-semibold ${analytics.performance.week_return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                    {analytics.performance.week_return >= 0 ? '+' : ''}{analytics.performance.week_return}%
                                </span>
                            </div>
                        )}
                        {analytics.performance.month_return !== undefined && (
                            <div>
                                <span className="text-slate-400 block">1 Month</span>
                                <span className={`font-semibold ${analytics.performance.month_return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                    {analytics.performance.month_return >= 0 ? '+' : ''}{analytics.performance.month_return}%
                                </span>
                            </div>
                        )}
                        {analytics.performance.quarter_return !== undefined && (
                            <div>
                                <span className="text-slate-400 block">3 Months</span>
                                <span className={`font-semibold ${analytics.performance.quarter_return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                    {analytics.performance.quarter_return >= 0 ? '+' : ''}{analytics.performance.quarter_return}%
                                </span>
                            </div>
                        )}
                        {analytics.performance.year_return !== undefined && (
                            <div>
                                <span className="text-slate-400 block">1 Year</span>
                                <span className={`font-semibold ${analytics.performance.year_return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                    {analytics.performance.year_return >= 0 ? '+' : ''}{analytics.performance.year_return}%
                                </span>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default SymbolAnalytics;
