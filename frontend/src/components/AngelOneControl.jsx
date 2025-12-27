/**
 * AngelOneControl Component
 * Control panel for managing Angel One WebSocket service and subscriptions
 */

import React, { useState, useEffect } from 'react';
import { Radio, Wifi, WifiOff, Plus, X, Play, Square, RefreshCw, Loader2, AlertCircle, CheckCircle } from 'lucide-react';
import { angelOneService, ANGEL_ONE_TOKENS } from '../services/angelOneService';

const AngelOneControl = ({ isConnected, reconnect, marketData }) => {
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [subscribedTokens, setSubscribedTokens] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState('indices');
    const [subscriptionMode, setSubscriptionMode] = useState(1);

    // Fetch status on mount and when connection changes
    useEffect(() => {
        fetchStatus();
    }, [isConnected]);

    const fetchStatus = async () => {
        try {
            const data = await angelOneService.getStatus();
            setStatus(data);
            // Extract subscribed tokens from status
            if (data.subscribed_tokens && data.subscribed_tokens.length > 0) {
                const tokens = data.subscribed_tokens.flatMap(group =>
                    group.tokens || []
                );
                setSubscribedTokens(tokens);
            }
        } catch (err) {
            console.error('Failed to fetch status:', err);
        }
    };

    const handleSubscribe = async (token) => {
        setLoading(true);
        setError(null);
        setSuccess(null);

        try {
            await angelOneService.subscribe(
                [{ exchangeType: token.exchangeType, tokens: [token.token] }],
                subscriptionMode
            );
            setSubscribedTokens(prev => [...prev, token.token]);
            setSuccess(`Subscribed to ${token.symbol}`);
            setTimeout(() => setSuccess(null), 3000);
            await fetchStatus();
        } catch (err) {
            setError(err.message);
            setTimeout(() => setError(null), 5000);
        } finally {
            setLoading(false);
        }
    };

    const handleUnsubscribe = async (token) => {
        setLoading(true);
        setError(null);

        try {
            await angelOneService.unsubscribe(
                [{ exchangeType: token.exchangeType, tokens: [token.token] }],
                subscriptionMode
            );
            setSubscribedTokens(prev => prev.filter(t => t !== token.token));
            setSuccess(`Unsubscribed from ${token.symbol}`);
            setTimeout(() => setSuccess(null), 3000);
            await fetchStatus();
        } catch (err) {
            setError(err.message);
            setTimeout(() => setError(null), 5000);
        } finally {
            setLoading(false);
        }
    };

    const isSubscribed = (token) => subscribedTokens.includes(token.token);
    const hasLiveData = (token) => marketData[token.token]?.received_at;

    return (
        <div className="space-y-4">
            {/* Status Card */}
            <div className="bg-slate-900/60 border border-slate-700/50 rounded-xl p-4">
                <div className="flex items-center justify-between mb-3">
                    <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                        <Radio className={isConnected ? "text-emerald-400 animate-pulse" : "text-slate-600"} size={18} />
                        Angel One Live Data
                    </h3>
                    <button
                        onClick={fetchStatus}
                        className="text-xs text-[var(--color-cyan)] hover:text-[var(--color-cyan-light)] flex items-center gap-1"
                    >
                        <RefreshCw size={12} />
                        Refresh
                    </button>
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs">
                    <div>
                        <span className="text-slate-500">Status:</span>
                        <div className={`font-medium mt-1 flex items-center gap-2 ${isConnected ? 'text-emerald-400' : 'text-slate-400'}`}>
                            {isConnected ? (
                                <>
                                    <Wifi size={14} />
                                    Connected
                                </>
                            ) : (
                                <>
                                    <WifiOff size={14} />
                                    Disconnected
                                </>
                            )}
                        </div>
                    </div>
                    <div>
                        <span className="text-slate-500">Subscriptions:</span>
                        <div className="font-medium mt-1 text-[var(--color-cyan)]">
                            {subscribedTokens.length} tokens
                        </div>
                    </div>
                    <div>
                        <span className="text-slate-500">Live Data:</span>
                        <div className="font-medium mt-1 text-white">
                            {Object.keys(marketData).length} receiving
                        </div>
                    </div>
                    <div>
                        <span className="text-slate-500">Mode:</span>
                        <div className="font-medium mt-1 text-slate-300">
                            {subscriptionMode === 1 ? 'LTP' : 'Full Quote'}
                        </div>
                    </div>
                </div>

                {status?.last_update && (
                    <div className="mt-3 pt-3 border-t border-slate-700/50 text-xs text-slate-500">
                        Last update: {new Date(status.last_update).toLocaleTimeString()}
                    </div>
                )}
            </div>

            {/* Alerts */}
            {error && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 flex items-start gap-2">
                    <AlertCircle className="text-red-400 flex-shrink-0 mt-0.5" size={16} />
                    <span className="text-sm text-red-300">{error}</span>
                </div>
            )}

            {success && (
                <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-lg p-3 flex items-start gap-2">
                    <CheckCircle className="text-emerald-400 flex-shrink-0 mt-0.5" size={16} />
                    <span className="text-sm text-emerald-300">{success}</span>
                </div>
            )}

            {/* Subscription Mode Selector */}
            <div className="bg-slate-900/60 border border-slate-700/50 rounded-xl p-4">
                <label className="block text-xs text-slate-400 mb-2">Subscription Mode</label>
                <div className="flex gap-2">
                    <button
                        onClick={() => setSubscriptionMode(1)}
                        className={`flex-1 px-3 py-2 rounded-lg text-xs font-medium transition-all ${subscriptionMode === 1
                                ? 'bg-[var(--color-cyan)]/20 border border-[var(--color-cyan)] text-[var(--color-cyan)]'
                                : 'bg-slate-800 border border-slate-700 text-slate-400 hover:border-slate-600'
                            }`}
                    >
                        LTP (Fast)
                    </button>
                    <button
                        onClick={() => setSubscriptionMode(3)}
                        className={`flex-1 px-3 py-2 rounded-lg text-xs font-medium transition-all ${subscriptionMode === 3
                                ? 'bg-[var(--color-cyan)]/20 border border-[var(--color-cyan)] text-[var(--color-cyan)]'
                                : 'bg-slate-800 border border-slate-700 text-slate-400 hover:border-slate-600'
                            }`}
                    >
                        Full Quote
                    </button>
                </div>
                <p className="text-xs text-slate-500 mt-2">
                    {subscriptionMode === 1 ? 'Only last traded price (lower bandwidth)' : 'Full market depth with OHLC data'}
                </p>
            </div>

            {/* Token Subscription */}
            <div className="bg-slate-900/60 border border-slate-700/50 rounded-xl p-4">
                <h3 className="text-sm font-semibold text-white mb-3">Subscribe to Symbols</h3>

                {/* Category Tabs */}
                <div className="flex gap-2 mb-3">
                    <button
                        onClick={() => setSelectedCategory('indices')}
                        className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${selectedCategory === 'indices'
                                ? 'bg-[var(--color-cyan)]/20 text-[var(--color-cyan)]'
                                : 'text-slate-400 hover:text-slate-300'
                            }`}
                    >
                        Indices
                    </button>
                    <button
                        onClick={() => setSelectedCategory('stocks')}
                        className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${selectedCategory === 'stocks'
                                ? 'bg-[var(--color-cyan)]/20 text-[var(--color-cyan)]'
                                : 'text-slate-400 hover:text-slate-300'
                            }`}
                    >
                        Stocks
                    </button>
                </div>

                {/* Token List */}
                <div className="space-y-2 max-h-64 overflow-y-auto custom-scrollbar">
                    {ANGEL_ONE_TOKENS[selectedCategory].map((token) => {
                        const subscribed = isSubscribed(token);
                        const live = hasLiveData(token);

                        return (
                            <div
                                key={token.token}
                                className="flex items-center justify-between p-2 bg-slate-800/50 rounded-lg border border-slate-700/30"
                            >
                                <div className="flex items-center gap-2">
                                    {live && (
                                        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                                    )}
                                    <div>
                                        <div className="text-sm font-medium text-[var(--color-cyan-light)]">
                                            {token.symbol}
                                        </div>
                                        <div className="text-xs text-slate-500">{token.name}</div>
                                    </div>
                                </div>

                                <button
                                    onClick={() => subscribed ? handleUnsubscribe(token) : handleSubscribe(token)}
                                    disabled={loading}
                                    className={`px-3 py-1 rounded-lg text-xs font-medium transition-all flex items-center gap-1 ${subscribed
                                            ? 'bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30'
                                            : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/30'
                                        } disabled:opacity-50`}
                                >
                                    {loading ? (
                                        <Loader2 className="animate-spin" size={12} />
                                    ) : subscribed ? (
                                        <><X size={12} /> Remove</>
                                    ) : (
                                        <><Plus size={12} /> Add</>
                                    )}
                                </button>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};

export default AngelOneControl;
