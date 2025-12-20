import React, { useMemo } from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

const MarketHeatmap = ({ assets = [], onAssetSelect }) => {
    // Calculate grid layout
    const gridData = useMemo(() => {
        if (!assets || assets.length === 0) return [];

        // Sort assets by market cap/volume for better visualization
        const sorted = [...assets].sort((a, b) => (b.alphaScore || 0) - (a.alphaScore || 0));

        return sorted.map(asset => ({
            ...asset,
            displayChange: asset.change24h || 0,
            size: Math.max(1, Math.min(3, Math.abs(asset.change24h || 1))), // Size based on volatility
        }));
    }, [assets]);

    // Get color based on performance
    const getColor = (change) => {
        if (change >= 5) return 'var(--color-emerald-500)';
        if (change >= 2) return 'var(--color-emerald-400)';
        if (change > 0) return 'var(--color-emerald-300)';
        if (change > -2) return 'var(--color-rose-300)';
        if (change > -5) return 'var(--color-rose-400)';
        return 'var(--color-rose-500)';
    };

    const getBgColor = (change) => {
        if (change >= 5) return 'bg-[var(--color-emerald)]/30';
        if (change >= 2) return 'bg-[var(--color-emerald)]/20';
        if (change > 0) return 'bg-[var(--color-emerald)]/10';
        if (change > -2) return 'bg-[var(--color-rose)]/10';
        if (change > -5) return 'bg-[var(--color-rose)]/20';
        return 'bg-[var(--color-rose)]/30';
    };

    const getBorderColor = (change) => {
        if (change >= 0) return 'border-[var(--color-emerald)]/40';
        return 'border-[var(--color-rose)]/40';
    };

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <div>
                    <h3 className="text-sm font-semibold text-[var(--color-purple-light)]">Market Heatmap</h3>
                    <p className="text-xs text-slate-400 mt-0.5">Color intensity shows performance strength</p>
                </div>
                <div className="flex items-center gap-4 text-xs">
                    <div className="flex items-center gap-1">
                        <div className="w-3 h-3 rounded bg-[var(--color-emerald)]/30 border border-[var(--color-emerald)]/40"></div>
                        <span className="text-slate-400">Gains</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <div className="w-3 h-3 rounded bg-[var(--color-rose)]/30 border border-[var(--color-rose)]/40"></div>
                        <span className="text-slate-400">Losses</span>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-2">
                {gridData.map((asset) => (
                    <button
                        key={asset.id}
                        onClick={() => onAssetSelect && onAssetSelect(asset)}
                        className={`${getBgColor(asset.displayChange)} ${getBorderColor(asset.displayChange)} border rounded-lg p-3 hover-lift hover-glow transition-all text-left relative overflow-hidden group`}
                        style={{
                            boxShadow: `0 0 20px ${getColor(asset.displayChange)}33`,
                        }}
                    >
                        {/* Background gradient effect */}
                        <div
                            className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                            style={{
                                background: `linear-gradient(135deg, ${getColor(asset.displayChange)}10 0%, transparent 100%)`,
                            }}
                        />

                        {/* Content */}
                        <div className="relative z-10">
                            <div className="flex items-start justify-between mb-2">
                                <div>
                                    <div className="text-xs font-semibold text-slate-200">{asset.symbol}</div>
                                    <div className="text-[10px] text-slate-400 truncate">{asset.name}</div>
                                </div>
                                {asset.displayChange >= 0 ? (
                                    <TrendingUp size={12} className="text-gain flex-shrink-0" />
                                ) : (
                                    <TrendingDown size={12} className="text-loss flex-shrink-0" />
                                )}
                            </div>

                            <div className="flex items-end justify-between">
                                <div>
                                    <div
                                        className="text-sm font-bold font-mono"
                                        style={{ color: getColor(asset.displayChange) }}
                                    >
                                        {asset.displayChange >= 0 ? '+' : ''}{asset.displayChange.toFixed(2)}%
                                    </div>
                                    <div className="text-[9px] text-slate-500">24h change</div>
                                </div>

                                {asset.alphaScore && (
                                    <div className="text-right">
                                        <div className="text-xs font-semibold text-gradient-primary">
                                            {asset.alphaScore}
                                        </div>
                                        <div className="text-[9px] text-slate-500">Alpha</div>
                                    </div>
                                )}
                            </div>

                            {/* Progress bar */}
                            <div className="mt-2 h-1 bg-slate-800 rounded-full overflow-hidden">
                                <div
                                    className="h-full rounded-full transition-all duration-500"
                                    style={{
                                        width: `${Math.min(100, Math.abs(asset.displayChange) * 10)}%`,
                                        backgroundColor: getColor(asset.displayChange),
                                    }}
                                />
                            </div>
                        </div>
                    </button>
                ))}
            </div>

            {/* Summary Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4">
                <div className="glass-card p-3">
                    <div className="text-[10px] text-slate-400 uppercase tracking-wide mb-1">Total Assets</div>
                    <div className="text-xl font-bold text-gradient-primary">{assets.length}</div>
                </div>

                <div className="glass-card p-3">
                    <div className="text-[10px] text-slate-400 uppercase tracking-wide mb-1">Gainers</div>
                    <div className="text-xl font-bold text-gain">
                        {assets.filter(a => (a.change24h || 0) > 0).length}
                    </div>
                </div>

                <div className="glass-card p-3">
                    <div className="text-[10px] text-slate-400 uppercase tracking-wide mb-1">Losers</div>
                    <div className="text-xl font-bold text-loss">
                        {assets.filter(a => (a.change24h || 0) < 0).length}
                    </div>
                </div>

                <div className="glass-card p-3">
                    <div className="text-[10px] text-slate-400 uppercase tracking-wide mb-1">Avg Change</div>
                    <div className={`text-xl font-bold ${assets.reduce((sum, a) => sum + (a.change24h || 0), 0) / assets.length >= 0
                            ? 'text-gain'
                            : 'text-loss'
                        }`}>
                        {assets.length > 0
                            ? (assets.reduce((sum, a) => sum + (a.change24h || 0), 0) / assets.length).toFixed(2)
                            : '0.00'}%
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MarketHeatmap;
