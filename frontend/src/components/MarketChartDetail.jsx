/**
 * MarketChartDetail Component
 * Compact modal showing candlestick chart with controls
 */

import React, { useState } from 'react';
import { X, TrendingUp, Calendar } from 'lucide-react';
import CandlestickChart from './charts/CandlestickChart';

const MarketChartDetail = ({ isOpen, onClose, marketData }) => {
    const [selectedPeriod, setSelectedPeriod] = useState('3mo');
    const [showIndicators, setShowIndicators] = useState({
        rsi: false,
        macd: false,
        bb: false,
        sma: false,
    });

    if (!isOpen || !marketData) return null;

    const periods = [
        { label: '1D', value: '1d' },
        { label: '5D', value: '5d' },
        { label: '1M', value: '1mo' },
        { label: '3M', value: '3mo' },
        { label: '6M', value: '6mo' },
        { label: '1Y', value: '1y' },
    ];

    const formatCurrency = (value) => {
        if (!value) return '—';
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: marketData.currency || 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        }).format(value);
    };

    const isPositive = marketData.change_percent > 0;

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-4xl max-h-[85vh] overflow-hidden flex flex-col shadow-2xl">
                {/* Header */}
                <div className="flex items-center justify-between p-3 border-b border-slate-700">
                    <div className="flex items-center gap-3">
                        <div>
                            <div className="flex items-center gap-2">
                                <h2 className="text-lg font-bold text-white">{marketData.name}</h2>
                                <span className="text-xs text-slate-400 font-mono">{marketData.symbol}</span>
                            </div>
                            <div className="flex items-center gap-2 mt-0.5">
                                <span className="text-xl font-bold text-white">
                                    {formatCurrency(marketData.price)}
                                </span>
                                <span className={`text-xs font-medium flex items-center gap-1 ${isPositive ? 'text-emerald-400' : 'text-red-400'
                                    }`}>
                                    <TrendingUp size={12} className={isPositive ? '' : 'rotate-180'} />
                                    {isPositive && '+'}{marketData.change_percent?.toFixed(2)}%
                                </span>
                            </div>
                        </div>
                    </div>

                    <button
                        onClick={onClose}
                        className="p-1.5 hover:bg-slate-800 rounded-lg transition-colors"
                    >
                        <X size={18} className="text-slate-400" />
                    </button>
                </div>

                {/* Controls */}
                <div className="flex items-center justify-between p-2.5 border-b border-slate-700 bg-slate-900/50">
                    {/* Time Period Selector */}
                    <div className="flex items-center gap-2">
                        <Calendar size={14} className="text-slate-400" />
                        <div className="flex gap-1">
                            {periods.map(period => (
                                <button
                                    key={period.value}
                                    onClick={() => setSelectedPeriod(period.value)}
                                    className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition-all ${selectedPeriod === period.value
                                            ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40'
                                            : 'bg-slate-800 text-slate-400 hover:bg-slate-700 border border-transparent'
                                        }`}
                                >
                                    {period.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Indicator Toggles */}
                    <div className="flex items-center gap-1.5">
                        <span className="text-[10px] text-slate-400 mr-1">Indicators:</span>
                        {[
                            { key: 'rsi', label: 'RSI' },
                            { key: 'macd', label: 'MACD' },
                            { key: 'bb', label: 'BB' },
                            { key: 'sma', label: 'SMA' },
                        ].map(indicator => (
                            <button
                                key={indicator.key}
                                onClick={() => setShowIndicators(prev => ({
                                    ...prev,
                                    [indicator.key]: !prev[indicator.key],
                                }))}
                                className={`px-2 py-0.5 rounded-lg text-[11px] font-medium transition-all ${showIndicators[indicator.key]
                                        ? 'bg-purple-500/20 text-purple-400 border border-purple-500/40'
                                        : 'bg-slate-800 text-slate-500 hover:bg-slate-700 border border-transparent'
                                    }`}
                            >
                                {indicator.label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Chart */}
                <div className="flex-1 overflow-auto p-3">
                    <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-700/50">
                        <CandlestickChart
                            symbol={marketData.symbol}
                            period={selectedPeriod}
                            interval={selectedPeriod === '1d' ? '1h' : '1d'}
                            height={350}
                            showVolume={true}
                        />
                    </div>

                    {/* Market Info */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-3">
                        <div className="bg-slate-900/50 rounded-lg p-2 border border-slate-700/50">
                            <div className="text-[10px] text-slate-400 mb-0.5">Open</div>
                            <div className="text-xs font-medium text-white">
                                {formatCurrency(marketData.open)}
                            </div>
                        </div>
                        <div className="bg-slate-900/50 rounded-lg p-2 border border-slate-700/50">
                            <div className="text-[10px] text-slate-400 mb-0.5">High</div>
                            <div className="text-xs font-medium text-emerald-400">
                                {formatCurrency(marketData.high)}
                            </div>
                        </div>
                        <div className="bg-slate-900/50 rounded-lg p-2 border border-slate-700/50">
                            <div className="text-[10px] text-slate-400 mb-0.5">Low</div>
                            <div className="text-xs font-medium text-red-400">
                                {formatCurrency(marketData.low)}
                            </div>
                        </div>
                        <div className="bg-slate-900/50 rounded-lg p-2 border border-slate-700/50">
                            <div className="text-[10px] text-slate-400 mb-0.5">Volume</div>
                            <div className="text-xs font-medium text-cyan-400">
                                {marketData.volume > 0
                                    ? marketData.volume >= 1e9
                                        ? `${(marketData.volume / 1e9).toFixed(1)}B`
                                        : marketData.volume >= 1e6
                                            ? `${(marketData.volume / 1e6).toFixed(1)}M`
                                            : `${(marketData.volume / 1e3).toFixed(1)}K`
                                    : '—'}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MarketChartDetail;
