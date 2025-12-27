/**
 * LiveMarketWidget Component
 * Displays live prices for Angel One market data with real-time updates
 */

import React from 'react';
import { TrendingUp, TrendingDown, Minus, Radio, Activity } from 'lucide-react';

const LiveMarketWidget = ({ marketData, tokens, layout = 'grid' }) => {
    if (!tokens || tokens.length === 0) {
        return (
            <div className="text-center py-8">
                <Activity className="w-12 h-12 text-slate-600 mx-auto mb-3" />
                <p className="text-sm text-slate-400">No tokens subscribed</p>
                <p className="text-xs text-slate-500 mt-1">
                    Subscribe to tokens to see live market data
                </p>
            </div>
        );
    }

    const PriceCard = ({ token }) => {
        const data = marketData[token.token];

        // Default values if no data
        const ltp = data?.last_traded_price_rupees || data?.last_traded_price / 100 || 0;
        const change = data?.change || 0;
        const changePercent = data?.change_percent || 0;
        const volume = data?.volume || 0;
        const isLive = data?.received_at && (Date.now() - new Date(data.received_at).getTime()) < 10000;

        const isPositive = changePercent > 0;
        const isNegative = changePercent < 0;
        const colorClass = isPositive
            ? 'text-emerald-400'
            : isNegative
                ? 'text-red-400'
                : 'text-slate-400';

        const TrendIcon = isPositive ? TrendingUp : isNegative ? TrendingDown : Minus;

        return (
            <div className="bg-slate-900/60 border border-slate-700/50 rounded-xl p-4 hover:border-[var(--color-cyan)]/40 transition-all group relative overflow-hidden">
                {/* Background gradient on hover */}
                <div className="absolute inset-0 bg-gradient-to-br from-[var(--color-cyan)]/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

                {/* Content */}
                <div className="relative">
                    {/* Header */}
                    <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                            <div className="flex items-center gap-2">
                                <h3 className="font-semibold text-[var(--color-cyan-light)] text-sm">
                                    {token.symbol}
                                </h3>
                                {isLive && (
                                    <div className="flex items-center gap-1">
                                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                                        <span className="text-[10px] text-emerald-400 font-medium">LIVE</span>
                                    </div>
                                )}
                            </div>
                            <p className="text-xs text-slate-500 mt-0.5">{token.name}</p>
                        </div>
                    </div>

                    {/* Price */}
                    <div className="mb-2">
                        <div className={`text-2xl font-bold ${data ? 'text-white' : 'text-slate-600'} transition-all`}>
                            {data ? `₹${ltp.toFixed(2)}` : '—'}
                        </div>
                    </div>

                    {/* Change */}
                    {data && (
                        <div className={`flex items-center gap-2 text-sm ${colorClass}`}>
                            <TrendIcon size={16} />
                            <span className="font-medium">
                                {changePercent > 0 && '+'}{changePercent.toFixed(2)}%
                            </span>
                            <span className="text-xs">
                                ({change > 0 && '+'}{change.toFixed(2)})
                            </span>
                        </div>
                    )}

                    {/* Volume */}
                    {data && volume > 0 && (
                        <div className="mt-2 pt-2 border-t border-slate-700/50">
                            <span className="text-xs text-slate-500">
                                Vol: {(volume / 1000000).toFixed(2)}M
                            </span>
                        </div>
                    )}

                    {/* No Data State */}
                    {!data && (
                        <div className="text-xs text-slate-500 mt-2">
                            Waiting for data...
                        </div>
                    )}
                </div>

                {/* Price Flash Effect */}
                {data && (
                    <div
                        key={data.received_at}
                        className={`absolute inset-0 pointer-events-none ${isPositive ? 'bg-emerald-500/5' : 'bg-red-500/5'} animate-[flash_0.3s_ease-out]`}
                    />
                )}
            </div>
        );
    };

    if (layout === 'ticker') {
        return (
            <div className="overflow-hidden border-y border-slate-700/50 bg-slate-900/40">
                <div className="flex animate-scroll">
                    {tokens.map((token) => (
                        <div key={token.token} className="flex items-center gap-4 px-6 py-3 border-r border-slate-700/30">
                            <span className="text-sm font-medium text-[var(--color-cyan-light)] whitespace-nowrap">
                                {token.symbol}
                            </span>
                            <span className="text-sm font-bold text-white whitespace-nowrap">
                                ₹{(marketData[token.token]?.last_traded_price_rupees || 0).toFixed(2)}
                            </span>
                            <span className={`text-xs ${marketData[token.token]?.change_percent > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                {marketData[token.token]?.change_percent > 0 && '+'}
                                {(marketData[token.token]?.change_percent || 0).toFixed(2)}%
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    if (layout === 'list') {
        return (
            <div className="space-y-2">
                {tokens.map((token) => {
                    const data = marketData[token.token];
                    const ltp = data?.last_traded_price_rupees || data?.last_traded_price / 100 || 0;
                    const changePercent = data?.change_percent || 0;
                    const isPositive = changePercent > 0;
                    const colorClass = isPositive ? 'text-emerald-400' : changePercent < 0 ? 'text-red-400' : 'text-slate-400';
                    const TrendIcon = isPositive ? TrendingUp : changePercent < 0 ? TrendingDown : Minus;

                    return (
                        <div key={token.token} className="flex items-center justify-between p-3 bg-slate-900/40 border border-slate-700/50 rounded-lg hover:border-[var(--color-cyan)]/40 transition-all">
                            <div className="flex items-center gap-3">
                                {data?.received_at && (
                                    <Radio className="w-3 h-3 text-emerald-500 animate-pulse" />
                                )}
                                <div>
                                    <div className="font-medium text-sm text-[var(--color-cyan-light)]">{token.symbol}</div>
                                    <div className="text-xs text-slate-500">{token.name}</div>
                                </div>
                            </div>
                            <div className="text-right">
                                <div className="font-bold text-sm text-white">
                                    {data ? `₹${ltp.toFixed(2)}` : '—'}
                                </div>
                                {data && (
                                    <div className={`flex items-center gap-1 text-xs ${colorClass} justify-end`}>
                                        <TrendIcon size={12} />
                                        {changePercent > 0 && '+'}{changePercent.toFixed(2)}%
                                    </div>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        );
    }

    // Default: grid layout
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {tokens.map((token) => (
                <PriceCard key={token.token} token={token} />
            ))}
        </div>
    );
};

export default LiveMarketWidget;
