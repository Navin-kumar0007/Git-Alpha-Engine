/**
 * LiveMarketsDashboard Component
 * Full dashboard view for Angel One live market data
 */

import React, { useState } from 'react';
import { Radio, Settings, BarChart3, Layout, List, Grid3x3 } from 'lucide-react';
import useAngelOneWebSocket from '../hooks/useAngelOneWebSocket';
import LiveMarketWidget from './LiveMarketWidget';
import AngelOneControl from './AngelOneControl';
import { ANGEL_ONE_TOKENS } from '../services/angelOneService';

const LiveMarketsDashboard = () => {
    const { marketData, isConnected, error, reconnect } = useAngelOneWebSocket();
    const [showSettings, setShowSettings] = useState(false);
    const [layout, setLayout] = useState('grid'); // 'grid', 'list', 'ticker'

    // Get all available tokens
    const allTokens = [
        ...ANGEL_ONE_TOKENS.indices,
        ...ANGEL_ONE_TOKENS.stocks,
    ];

    // Filter tokens that have data
    const activeTokens = allTokens.filter(token => marketData[token.token]);

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white mb-1 flex items-center gap-2">
                        <Radio className={isConnected ? "text-emerald-400 animate-pulse" : "text-slate-600"} size={28} />
                        Live Markets
                    </h1>
                    <p className="text-sm text-slate-400">
                        Real-time data from Angel One • {activeTokens.length} symbols streaming
                    </p>
                </div>

                <div className="flex items-center gap-3">
                    {/* Layout Toggle */}
                    <div className="flex items-center gap-2 bg-slate-900/60 border border-slate-700/50 rounded-lg p-1">
                        <button
                            onClick={() => setLayout('grid')}
                            className={`p-2 rounded transition-all ${layout === 'grid'
                                    ? 'bg-[var(--color-cyan)]/20 text-[var(--color-cyan)]'
                                    : 'text-slate-400 hover:text-slate-300'
                                }`}
                            title="Grid View"
                        >
                            <Grid3x3 size={16} />
                        </button>
                        <button
                            onClick={() => setLayout('list')}
                            className={`p-2 rounded transition-all ${layout === 'list'
                                    ? 'bg-[var(--color-cyan)]/20 text-[var(--color-cyan)]'
                                    : 'text-slate-400 hover:text-slate-300'
                                }`}
                            title="List View"
                        >
                            <List size={16} />
                        </button>
                        <button
                            onClick={() => setLayout('ticker')}
                            className={`p-2 rounded transition-all ${layout === 'ticker'
                                    ? 'bg-[var(--color-cyan)]/20 text-[var(--color-cyan)]'
                                    : 'text-slate-400 hover:text-slate-300'
                                }`}
                            title="Ticker View"
                        >
                            <Layout size={16} />
                        </button>
                    </div>

                    {/* Settings Toggle */}
                    <button
                        onClick={() => setShowSettings(!showSettings)}
                        className={`px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium transition-all ${showSettings
                                ? 'bg-[var(--color-cyan)]/20 border border-[var(--color-cyan)] text-[var(--color-cyan)]'
                                : 'bg-slate-900/60 border border-slate-700/50 text-slate-300 hover:border-[var(--color-cyan)]/40'
                            }`}
                    >
                        <Settings size={16} />
                        {showSettings ? 'Hide' : 'Settings'}
                    </button>
                </div>
            </div>

            {/* Connection Status Banner */}
            <div className={`rounded-xl p-4 border ${isConnected
                    ? 'bg-emerald-500/10 border-emerald-500/30'
                    : 'bg-red-500/10 border-red-500/30'
                }`}>
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
                        <div>
                            <div className={`text-sm font-medium ${isConnected ? 'text-emerald-300' : 'text-red-300'}`}>
                                {isConnected ? 'Connected to live market feed' : 'Disconnected from market feed'}
                            </div>
                            <div className="text-xs text-slate-400 mt-0.5">
                                {isConnected
                                    ? 'Receiving real-time updates from Angel One'
                                    : error || 'Attempting to reconnect...'}
                            </div>
                        </div>
                    </div>

                    {!isConnected && (
                        <button
                            onClick={reconnect}
                            className="px-4 py-2 bg-[var(--color-cyan)]/20 border border-[var(--color-cyan)] text-[var(--color-cyan)] rounded-lg text-sm font-medium hover:bg-[var(--color-cyan)]/30 transition-all"
                        >
                            Reconnect
                        </button>
                    )}
                </div>
            </div>

            {/* Main Content */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Market Data - Main Area */}
                <div className={showSettings ? 'lg:col-span-2' : 'lg:col-span-3'}>
                    <div className="bg-slate-900/40 border border-slate-700/50 rounded-xl p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                                <BarChart3 className="text-[var(--color-cyan)]" size={20} />
                                Market Watch
                            </h2>
                            <div className="text-xs text-slate-500">
                                {Object.keys(marketData).length} active streams
                            </div>
                        </div>

                        {activeTokens.length > 0 ? (
                            <LiveMarketWidget
                                marketData={marketData}
                                tokens={activeTokens}
                                layout={layout}
                            />
                        ) : (
                            <div className="text-center py-12">
                                <BarChart3 className="w-16 h-16 text-slate-700 mx-auto mb-4" />
                                <p className="text-slate-400 mb-2">No symbols subscribed</p>
                                <p className="text-sm text-slate-500">
                                    {showSettings
                                        ? 'Choose symbols from the settings panel →'
                                        : 'Click "Settings" to subscribe to market symbols'}
                                </p>
                                {!showSettings && (
                                    <button
                                        onClick={() => setShowSettings(true)}
                                        className="mt-4 px-4 py-2 bg-[image:var(--gradient-primary)] rounded-lg text-sm font-medium hover:shadow-[var(--shadow-glow)] transition-all"
                                    >
                                        Open Settings
                                    </button>
                                )}
                            </div>
                        )}
                    </div>

                    {/* Quick Stats */}
                    {activeTokens.length > 0 && (
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                            <div className="bg-slate-900/60 border border-slate-700/50 rounded-xl p-4">
                                <div className="text-xs text-slate-400 mb-1">Active Streams</div>
                                <div className="text-2xl font-bold text-[var(--color-cyan)]">
                                    {Object.keys(marketData).length}
                                </div>
                            </div>
                            <div className="bg-slate-900/60 border border-slate-700/50 rounded-xl p-4">
                                <div className="text-xs text-slate-400 mb-1">Gainers</div>
                                <div className="text-2xl font-bold text-emerald-400">
                                    {Object.values(marketData).filter(d => d.change_percent > 0).length}
                                </div>
                            </div>
                            <div className="bg-slate-900/60 border border-slate-700/50 rounded-xl p-4">
                                <div className="text-xs text-slate-400 mb-1">Losers</div>
                                <div className="text-2xl font-bold text-red-400">
                                    {Object.values(marketData).filter(d => d.change_percent < 0).length}
                                </div>
                            </div>
                            <div className="bg-slate-900/60 border border-slate-700/50 rounded-xl p-4">
                                <div className="text-xs text-slate-400 mb-1">Connection</div>
                                <div className={`text-2xl font-bold ${isConnected ? 'text-emerald-400' : 'text-red-400'}`}>
                                    {isConnected ? 'Live' : 'Down'}
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Settings Panel */}
                {showSettings && (
                    <div className="lg:col-span-1">
                        <AngelOneControl
                            isConnected={isConnected}
                            reconnect={reconnect}
                            marketData={marketData}
                        />
                    </div>
                )}
            </div>

            {/* Market Hours Notice */}
            <div className="bg-slate-900/40 border border-slate-700/30 rounded-lg p-4">
                <p className="text-xs text-slate-400">
                    <strong className="text-slate-300">Note:</strong> Live market data is available during trading hours (Mon-Fri,  9:15 AM - 3:30 PM IST).
                    Outside trading hours, the connection will remain active but no price updates will occur.
                </p>
            </div>
        </div>
    );
};

export default LiveMarketsDashboard;
