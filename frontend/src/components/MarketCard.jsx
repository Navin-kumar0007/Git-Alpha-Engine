/**
 * MarketCard Component
 * Compact display of market index with live price data
 */

import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

const MarketCard = ({ marketData, onClick }) => {
    if (!marketData) return null;

    const {
        symbol,
        name,
        price,
        change_percent,
        market_code,
        currency,
        high,
        low,
        volume,
    } = marketData;

    // Determine trend
    const isPositive = change_percent > 0;
    const isNegative = change_percent < 0;

    // Format currency
    const formatCurrency = (value) => {
        if (!value) return '—';
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency || 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        }).format(value);
    };

    // Format large numbers (volume)
    const formatVolume = (val) => {
        if (!val) return '—';
        if (val >= 1e9) return `${(val / 1e9).toFixed(1)}B`;
        if (val >= 1e6) return `${(val / 1e6).toFixed(1)}M`;
        if (val >= 1e3) return `${(val / 1e3).toFixed(1)}K`;
        return val.toFixed(0);
    };

    return (
        <div
            className="glass-card hover-lift cursor-pointer transition-all duration-300 p-3"
            onClick={onClick}
        >
            {/* Header */}
            <div className="flex items-start justify-between mb-2">
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5 mb-0.5">
                        <span className="text-xs font-mono text-[var(--color-gold)]">
                            {symbol}
                        </span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800/50 text-slate-400">
                            {market_code}
                        </span>
                    </div>
                    <h3 className="text-sm font-semibold text-white truncate">
                        {name}
                    </h3>
                </div>
            </div>

            {/* Price */}
            <div className="mb-2">
                <div className="text-lg font-bold text-white mb-0.5">
                    {formatCurrency(price)}
                </div>
                <div className={`flex items-center gap-1 text-xs font-medium ${isPositive ? 'text-emerald-400' : isNegative ? 'text-red-400' : 'text-slate-400'
                    }`}>
                    {isPositive && <TrendingUp size={12} />}
                    {isNegative && <TrendingDown size={12} />}
                    <span>
                        {isPositive && '+'}{change_percent?.toFixed(2)}%
                    </span>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-700/50">
                <div>
                    <div className="text-[10px] text-slate-500 mb-0.5">High</div>
                    <div className="text-xs font-medium text-emerald-400">
                        {formatCurrency(high)}
                    </div>
                </div>
                <div>
                    <div className="text-[10px] text-slate-500 mb-0.5">Low</div>
                    <div className="text-xs font-medium text-red-400">
                        {formatCurrency(low)}
                    </div>
                </div>
                <div>
                    <div className="text-[10px] text-slate-500 mb-0.5">Vol</div>
                    <div className="text-xs font-medium text-cyan-400">
                        {formatVolume(volume)}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MarketCard;
