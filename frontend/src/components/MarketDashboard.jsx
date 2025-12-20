/**
 * MarketDashboard Component
 * Main view for displaying all market indices
 */

import React, { useState } from 'react';
import { RefreshCw, Loader2, AlertCircle, BarChart3 } from 'lucide-react';
import { useAllMarketData, useMarkets } from '../hooks/useMarketData';
import MarketCard from './MarketCard';
import MarketSelector from './MarketSelector';
import MarketChartDetail from './MarketChartDetail';

const MarketDashboard = () => {
    const [selectedMarket, setSelectedMarket] = useState('ALL');
    const [chartModalOpen, setChartModalOpen] = useState(false);
    const [selectedChartData, setSelectedChartData] = useState(null);
    const { markets, loading: marketsLoading } = useMarkets();
    const { marketData, loading: dataLoading, error, refetch } = useAllMarketData();
    const [refreshing, setRefreshing] = useState(false);

    // Filter market data based on selected market
    const filteredData = selectedMarket === 'ALL'
        ? marketData
        : marketData.filter(item => item.market_code === selectedMarket);

    // Handle manual refresh
    const handleRefresh = async () => {
        setRefreshing(true);
        await refetch();
        setTimeout(() => setRefreshing(false), 500);
    };

    // Handle chart view
    const handleViewChart = (data) => {
        setSelectedChartData(data);
        setChartModalOpen(true);
    };

    // Loading state
    if (dataLoading && marketData.length === 0) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-center">
                    <Loader2 className="w-8 h-8 animate-spin text-[var(--color-cyan)] mx-auto mb-3" />
                    <p className="text-sm text-slate-400">Loading market data...</p>
                </div>
            </div>
        );
    }

    // Error state
    if (error && marketData.length === 0) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-center">
                    <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-3" />
                    <p className="text-sm text-slate-300 mb-2">Failed to load market data</p>
                    <p className="text-xs text-slate-500 mb-4">{error}</p>
                    <button
                        onClick={handleRefresh}
                        className="px-4 py-2 bg-[image:var(--gradient-primary)] rounded-lg text-sm font-medium hover:shadow-[var(--shadow-glow)] transition-all"
                    >
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    return (
        <>
            <div className="space-y-6">
                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    <div>
                        <h1 className="text-2xl font-bold text-white mb-1 flex items-center gap-2">
                            <BarChart3 className="text-[var(--color-cyan)]" size={28} />
                            Global Markets
                        </h1>
                        <p className="text-sm text-slate-400">
                            Live data from {marketData.length} indices across {markets.length} markets
                        </p>
                    </div>

                    <div className="flex items-center gap-3">
                        {/* Market Selector */}
                        <MarketSelector
                            markets={markets}
                            selectedMarket={selectedMarket}
                            onSelect={setSelectedMarket}
                            loading={marketsLoading}
                        />

                        {/* Refresh Button */}
                        <button
                            onClick={handleRefresh}
                            disabled={refreshing}
                            className="px-4 py-3 bg-slate-900/80 border border-[var(--color-cyan)]/40 rounded-xl hover:bg-[var(--color-cyan)]/10 hover:border-[var(--color-cyan)] transition-all flex items-center gap-2 text-sm font-medium text-[var(--color-cyan-light)] disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
                            <span className="hidden md:inline">Refresh</span>
                        </button>
                    </div>
                </div>

                {/* Auto-refresh indicator */}
                <div className="flex items-center gap-2 text-xs text-slate-500">
                    <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                    Auto-refreshing every 5 minutes
                </div>

                {/* Market Grid */}
                {filteredData.length === 0 ? (
                    <div className="text-center py-12">
                        <p className="text-slate-400">No indices found for selected market</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {filteredData.map((data) => (
                            <MarketCard
                                key={data.symbol}
                                marketData={data}
                                onClick={() => handleViewChart(data)}
                            />
                        ))}
                    </div>
                )}

                {/* Stats Footer */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-6 border-t border-slate-700/50">
                    <div className="text-center">
                        <div className="text-2xl font-bold text-[var(--color-emerald)]">
                            {filteredData.filter(d => d.change_percent > 0).length}
                        </div>
                        <div className="text-xs text-slate-400 mt-1">Gainers</div>
                    </div>
                    <div className="text-center">
                        <div className="text-2xl font-bold text-red-400">
                            {filteredData.filter(d => d.change_percent < 0).length}
                        </div>
                        <div className="text-xs text-slate-400 mt-1">Losers</div>
                    </div>
                    <div className="text-center">
                        <div className="text-2xl font-bold text-slate-300">
                            {filteredData.filter(d => d.change_percent === 0).length}
                        </div>
                        <div className="text-xs text-slate-400 mt-1">Neutral</div>
                    </div>
                    <div className="text-center">
                        <div className="text-2xl font-bold text-[var(--color-cyan)]">
                            {markets.length}
                        </div>
                        <div className="text-xs text-slate-400 mt-1">Markets</div>
                    </div>
                </div>
            </div>

            {/* Chart Modal */}
            <MarketChartDetail
                isOpen={chartModalOpen}
                onClose={() => setChartModalOpen(false)}
                marketData={selectedChartData}
            />
        </>
    );
};

export default MarketDashboard;
