/**
 * MarketSelector Component
 * Dropdown selector for filtering markets by region
 */

import React from 'react';
import { Globe, ChevronDown } from 'lucide-react';

const MarketSelector = ({ markets, selectedMarket, onSelect, loading }) => {
    const marketOptions = [
        { code: 'ALL', name: 'All Markets', icon: '🌍' },
        ...markets.map(m => ({
            code: m.code,
            name: m.name,
            icon: getMarketIcon(m.code),
            indices_count: m.indices_count
        }))
    ];

    function getMarketIcon(code) {
        const icons = {
            'IN': '🇮🇳',
            'US': '🇺🇸',
            'UK': '🇬🇧',
            'JP': '🇯🇵',
            'SG': '🇸🇬'
        };
        return icons[code] || '🌍';
    }

    return (
        <div className="relative">
            <select
                value={selectedMarket}
                onChange={(e) => onSelect(e.target.value)}
                disabled={loading}
                className="w-full md:w-64 bg-slate-900/80 border border-slate-700/80 rounded-xl px-4 py-3 pr-10 text-sm font-medium text-white focus:outline-none focus:border-[var(--color-cyan)] focus:ring-2 focus:ring-[var(--color-cyan)]/20 transition-all appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
                {marketOptions.map(market => (
                    <option key={market.code} value={market.code}>
                        {market.icon} {market.name}
                        {market.indices_count ? ` (${market.indices_count})` : ''}
                    </option>
                ))}
            </select>

            <ChevronDown
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none"
                size={16}
            />
        </div>
    );
};

export default MarketSelector;
