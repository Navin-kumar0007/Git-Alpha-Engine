import React, { useState } from 'react';
import { Search, BarChart3, TrendingUp } from 'lucide-react';
import HistoricalChart from './HistoricalChart';
import SymbolAnalytics from './SymbolAnalytics';

/**
 * Charts Page
 * Main page for viewing historical candlestick charts
 */
const Charts = ({ user }) => {
    const [selectedSymbol, setSelectedSymbol] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);

    // Popular symbols (hard-coded for now - can be fetched from API later)
    const popularSymbols = [
        { symboltoken: '99926000', name: 'NIFTY 50', exchange: 'NSE' },
        { symboltoken: '99926009', name: 'BANK NIFTY', exchange: 'NSE' },
        { symboltoken: '3045', name: 'RELIANCE', exchange: 'NSE' },
        { symboltoken: '11536', name: 'TCS', exchange: 'NSE' },
        { symboltoken: '1594', name: 'INFY', exchange: 'NSE' },
        { symboltoken: '5258', name: 'ITC', exchange: 'NSE' },
        { symboltoken: '11915', name: 'HDFCBANK', exchange: 'NSE' },
        { symboltoken: '3456', name: 'ICICIBANK', exchange: 'NSE' },
        { symboltoken: '1660', name: 'SBIN', exchange: 'NSE' },
        { symboltoken: '1922', name: 'AXISBANK', exchange: 'NSE' },
    ];

    const handleSymbolSelect = (symbol) => {
        setSelectedSymbol(symbol);
        setSearchQuery('');
        setSearchResults([]);
    };

    const handleSearch = (query) => {
        setSearchQuery(query);

        if (query.trim().length > 0) {
            // Simple client-side search through popular symbols
            const results = popularSymbols.filter(
                (symbol) =>
                    symbol.name.toLowerCase().includes(query.toLowerCase()) ||
                    symbol.symboltoken.includes(query)
            );
            setSearchResults(results);
        } else {
            setSearchResults([]);
        }
    };

    if (!user) {
        return (
            <div className="flex items-center justify-center h-96">
                <p className="text-slate-400">Please login to view charts</p>
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="p-3 bg-indigo-600 rounded-lg">
                        <BarChart3 size={24} />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold gradient-text">Charts</h1>
                        <p className="text-slate-400 text-sm">
                            Historical price data and technical analysis
                        </p>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* Sidebar - Symbol Selector */}
                <div className="lg:col-span-1 space-y-4">
                    {/* Search */}
                    <div className="glass-card">
                        <div className="relative">
                            <Search
                                size={18}
                                className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400"
                            />
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={(e) => handleSearch(e.target.value)}
                                placeholder="Search symbols..."
                                className="w-full bg-slate-800/50 border border-slate-700 rounded-lg pl-10 pr-4 py-2 text-white focus:outline-none focus:border-indigo-500"
                            />
                        </div>

                        {/* Search Results */}
                        {searchResults.length > 0 && (
                            <div className="mt-3 space-y-1 max-h-64 overflow-y-auto">
                                {searchResults.map((symbol) => (
                                    <button
                                        key={symbol.symboltoken}
                                        onClick={() => handleSymbolSelect(symbol)}
                                        className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${selectedSymbol?.symboltoken === symbol.symboltoken
                                            ? 'bg-indigo-600 text-white'
                                            : 'hover:bg-slate-800/50 text-slate-300'
                                            }`}
                                    >
                                        <div className="font-semibold text-sm">{symbol.name}</div>
                                        <div className="text-xs text-slate-400">
                                            {symbol.exchange} • {symbol.symboltoken}
                                        </div>
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Custom Symbol Input */}
                    <div className="glass-card">
                        <h3 className="text-sm font-semibold mb-3">Custom Symbol</h3>
                        <form
                            onSubmit={(e) => {
                                e.preventDefault();
                                const formData = new FormData(e.target);
                                const customSymbol = {
                                    symboltoken: formData.get('symboltoken'),
                                    name: formData.get('name') || 'Custom Symbol',
                                    exchange: formData.get('exchange') || 'NSE',
                                };
                                if (customSymbol.symboltoken) {
                                    handleSymbolSelect(customSymbol);
                                    e.target.reset();
                                }
                            }}
                            className="space-y-3"
                        >
                            <div>
                                <label className="block text-xs text-slate-400 mb-1">
                                    Symbol Token *
                                </label>
                                <input
                                    type="text"
                                    name="symboltoken"
                                    placeholder="e.g., 3045"
                                    required
                                    className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                                />
                            </div>
                            <div>
                                <label className="block text-xs text-slate-400 mb-1">
                                    Symbol Name
                                </label>
                                <input
                                    type="text"
                                    name="name"
                                    placeholder="e.g., RELIANCE"
                                    className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                                />
                            </div>
                            <div>
                                <label className="block text-xs text-slate-400 mb-1">
                                    Exchange
                                </label>
                                <select
                                    name="exchange"
                                    className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                                >
                                    <option value="NSE">NSE</option>
                                    <option value="BSE">BSE</option>
                                    <option value="NFO">NFO</option>
                                    <option value="MCX">MCX</option>
                                </select>
                            </div>
                            <button
                                type="submit"
                                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-lg transition-colors text-sm"
                            >
                                Load Chart
                            </button>
                        </form>
                        <div className="mt-3 p-3 bg-slate-800/30 rounded-lg">
                            <p className="text-xs text-slate-400">
                                💡 Find symbol tokens at{' '}
                                <a
                                    href="https://margincalculator.angelbroking.com/"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-indigo-400 hover:text-indigo-300 underline"
                                >
                                    Angel One Margin Calculator
                                </a>
                            </p>
                        </div>
                    </div>

                    {/* Popular Symbols */}
                    <div className="glass-card">
                        <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                            <TrendingUp size={16} />
                            Popular Symbols
                        </h3>
                        <div className="space-y-1">
                            {popularSymbols.map((symbol) => (
                                <button
                                    key={symbol.symboltoken}
                                    onClick={() => handleSymbolSelect(symbol)}
                                    className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${selectedSymbol?.symboltoken === symbol.symboltoken
                                        ? 'bg-indigo-600 text-white'
                                        : 'hover:bg-slate-800/50 text-slate-300'
                                        }`}
                                >
                                    <div className="font-semibold">{symbol.name}</div>
                                    <div className="text-xs text-slate-400">{symbol.exchange}</div>
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Main Content Area */}
                <div className="lg:col-span-3 space-y-6">
                    {/* Chart */}
                    <div className="lg:col-span-2">
                        <HistoricalChart user={user} symbol={selectedSymbol} />
                    </div>

                    {/* Analytics Panel - Shows when symbol is selected */}
                    {selectedSymbol && (
                        <div>
                            <SymbolAnalytics symbol={selectedSymbol} />
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Charts;
