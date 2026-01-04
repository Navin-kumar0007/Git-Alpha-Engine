import React, { useState, useEffect } from 'react';
import {
    Wallet,
    TrendingUp,
    TrendingDown,
    RefreshCw,
    X,
    Building2,
    Clock,
    IndianRupee,
} from 'lucide-react';
import WealthCard from './WealthCard';
import { useToast } from './Toast';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const getAuthHeaders = () => {
    const token = localStorage.getItem('git_alpha_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
};

/**
 * Angel One Portfolio View Component
 * Displays live portfolio synced from Angel One broker account
 */
const AngelOnePortfolioView = ({ user }) => {
    const [portfolio, setPortfolio] = useState(null);
    const [loading, setLoading] = useState(true);
    const [syncing, setSyncing] = useState(false);
    const [lastSync, setLastSync] = useState(null);
    const [error, setError] = useState(null);
    const toast = useToast();

    // Fetch cached portfolio data
    const fetchCachedPortfolio = async () => {
        try {
            setLoading(true);
            setError(null);

            const res = await fetch(`${API_URL}/api/angel-portfolio/status`, {
                headers: getAuthHeaders(),
            });

            if (res.ok) {
                const status = await res.json();

                if (status.has_cached_data) {
                    // Fetch the actual data
                    const [holdingsRes, positionsRes, fundsRes] = await Promise.all([
                        fetch(`${API_URL}/api/angel-portfolio/holdings`, { headers: getAuthHeaders() }),
                        fetch(`${API_URL}/api/angel-portfolio/positions`, { headers: getAuthHeaders() }),
                        fetch(`${API_URL}/api/angel-portfolio/funds`, { headers: getAuthHeaders() }),
                    ]);

                    const [holdings, positions, funds] = await Promise.all([
                        holdingsRes.json(),
                        positionsRes.json(),
                        fundsRes.json(),
                    ]);

                    setPortfolio({
                        holdings: holdings.data || [],
                        positions: positions.data || [],
                        funds: funds.data || null,
                    });
                    setLastSync(status.last_sync);
                } else {
                    setPortfolio(null);
                }
            }
        } catch (err) {
            console.error('Failed to fetch portfolio:', err);
            setError('Failed to load portfolio data');
        } finally {
            setLoading(false);
        }
    };

    // Sync portfolio from Angel One
    const syncPortfolio = async () => {
        try {
            setSyncing(true);
            setError(null);

            const res = await fetch(`${API_URL}/api/angel-portfolio/sync`, {
                headers: getAuthHeaders(),
            });

            const data = await res.json();

            if (data.success) {
                setPortfolio(data.data);
                setLastSync(data.synced_at);

                // Check for partial errors
                if (data.partial_errors && data.partial_errors.length > 0) {
                    const syncStatus = data.sync_status;
                    const successParts = [];
                    if (syncStatus.holdings) successParts.push('holdings');
                    if (syncStatus.positions) successParts.push('positions');
                    if (syncStatus.funds) successParts.push('funds');

                    toast.success(`Partially synced: ${successParts.join(', ')}`);
                    setError(`Some data failed to sync: ${data.partial_errors.join(', ')}`);
                } else {
                    toast.success('Portfolio synced successfully!');
                    setError(null);
                }
            } else {
                setError(data.error || 'Failed to sync portfolio');
                toast.error(data.error || 'Sync failed');
            }
        } catch (err) {
            console.error('Sync error:', err);
            setError('Network error during sync');
            toast.error('Network error');
        } finally {
            setSyncing(false);
        }
    };

    useEffect(() => {
        if (user) {
            fetchCachedPortfolio();
        }
    }, [user]);

    // Calculate totals
    const calculateTotals = () => {
        if (!portfolio) return { totalValue: 0, totalPnl: 0, totalInvested: 0 };

        const holdingsValue = portfolio.holdings.reduce((sum, h) => sum + (h.current_value || 0), 0);
        const holdingsPnl = portfolio.holdings.reduce((sum, h) => sum + (h.pnl || 0), 0);
        const holdingsInvested = portfolio.holdings.reduce((sum, h) => sum + (h.quantity * h.avg_price), 0);

        const positionsValue = portfolio.positions.reduce((sum, p) => sum + (p.quantity * p.ltp), 0);
        const positionsPnl = portfolio.positions.reduce((sum, p) => sum + (p.pnl || 0), 0);

        return {
            totalValue: holdingsValue + positionsValue,
            totalPnl: holdingsPnl + positionsPnl,
            totalInvested: holdingsInvested,
        };
    };

    const totals = calculateTotals();
    const pnlPercentage = totals.totalInvested > 0 ? (totals.totalPnl / totals.totalInvested) * 100 : 0;

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <RefreshCw className="animate-spin text-indigo-400" size={32} />
            </div>
        );
    }

    const isEmpty = !portfolio || (portfolio.holdings.length === 0 && portfolio.positions.length === 0);

    return (
        <div className="space-y-6">
            {/* Header with Sync Button */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold gradient-text">Angel One Portfolio</h2>
                    {lastSync && (
                        <p className="text-sm text-slate-400 flex items-center gap-2 mt-1">
                            <Clock size={14} />
                            Last synced: {new Date(lastSync).toLocaleString()}
                        </p>
                    )}
                </div>
                <button
                    onClick={syncPortfolio}
                    disabled={syncing}
                    className="btn btn-primary"
                >
                    <RefreshCw size={18} className={syncing ? 'animate-spin' : ''} />
                    {syncing ? 'Syncing...' : 'Sync Now'}
                </button>
            </div>

            {error && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                    <p className="text-red-400">{error}</p>
                </div>
            )}

            {isEmpty ? (
                /* Empty State */
                <div className="glass-card text-center py-16">
                    <Building2 size={64} className="mx-auto text-slate-600 mb-4" />
                    <h3 className="text-xl font-semibold mb-2">No Angel One Data</h3>
                    <p className="text-slate-400 mb-6">
                        Click "Sync Now" to fetch your portfolio from Angel One broker account
                    </p>
                    <button
                        onClick={syncPortfolio}
                        disabled={syncing}
                        className="btn btn-primary"
                    >
                        <RefreshCw size={20} className={syncing ? 'animate-spin' : ''} />
                        {syncing ? 'Syncing...' : 'Sync Portfolio'}
                    </button>
                </div>
            ) : (
                <>
                    {/* Summary Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <WealthCard
                            title="Total Value"
                            value={totals.totalValue}
                            icon={Wallet}
                            gradient={true}
                            prefix="₹"
                        />
                        <WealthCard
                            title="Total Invested"
                            value={totals.totalInvested}
                            icon={IndianRupee}
                            prefix="₹"
                        />
                        <WealthCard
                            title="Total P&L"
                            value={totals.totalPnl}
                            change={pnlPercentage}
                            icon={totals.totalPnl >= 0 ? TrendingUp : TrendingDown}
                            prefix="₹"
                        />
                        {portfolio.funds && (
                            <WealthCard
                                title="Available Cash"
                                value={portfolio.funds.available_cash}
                                icon={IndianRupee}
                                prefix="₹"
                            />
                        )}
                    </div>

                    {/* Holdings Table */}
                    {portfolio.holdings.length > 0 && (
                        <div className="glass-card">
                            <h2 className="text-lg font-semibold mb-3">Holdings</h2>
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead>
                                        <tr className="border-b border-slate-700">
                                            <th className="text-left py-2 px-3 text-xs text-slate-300">Symbol</th>
                                            <th className="text-left py-2 px-3 text-xs text-slate-300">Exchange</th>
                                            <th className="text-right py-2 px-3 text-xs text-slate-300">Qty</th>
                                            <th className="text-right py-2 px-3 text-xs text-slate-300">Avg Price</th>
                                            <th className="text-right py-2 px-3 text-xs text-slate-300">LTP</th>
                                            <th className="text-right py-2 px-3 text-xs text-slate-300">Value</th>
                                            <th className="text-right py-2 px-3 text-xs text-slate-300">P&L</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {portfolio.holdings.map((holding, idx) => (
                                            <tr
                                                key={idx}
                                                className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors"
                                            >
                                                <td className="py-2 px-3 font-semibold text-sm">
                                                    {holding.trading_symbol}
                                                </td>
                                                <td className="py-2 px-3 text-sm text-slate-400">
                                                    {holding.exchange}
                                                </td>
                                                <td className="text-right py-2 px-3 text-sm">{holding.quantity}</td>
                                                <td className="text-right py-2 px-3 text-sm">
                                                    ₹{holding.avg_price.toFixed(2)}
                                                </td>
                                                <td className="text-right py-2 px-3 text-sm">
                                                    ₹{holding.ltp.toFixed(2)}
                                                </td>
                                                <td className="text-right py-2 px-3 text-sm font-semibold">
                                                    ₹{holding.current_value.toLocaleString(undefined, {
                                                        minimumFractionDigits: 2,
                                                        maximumFractionDigits: 2,
                                                    })}
                                                </td>
                                                <td
                                                    className={`text-right py-2 px-3 text-sm font-semibold ${holding.pnl >= 0 ? 'text-green-400' : 'text-red-400'
                                                        }`}
                                                >
                                                    {holding.pnl >= 0 ? '+' : ''}₹{holding.pnl.toFixed(2)}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}

                    {/* Positions Table */}
                    {portfolio.positions.length > 0 && (
                        <div className="glass-card">
                            <h2 className="text-lg font-semibold mb-3">Positions</h2>
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead>
                                        <tr className="border-b border-slate-700">
                                            <th className="text-left py-2 px-3 text-xs text-slate-300">Symbol</th>
                                            <th className="text-left py-2 px-3 text-xs text-slate-300">Type</th>
                                            <th className="text-right py-2 px-3 text-xs text-slate-300">Qty</th>
                                            <th className="text-right py-2 px-3 text-xs text-slate-300">Avg Price</th>
                                            <th className="text-right py-2 px-3 text-xs text-slate-300">LTP</th>
                                            <th className="text-right py-2 px-3 text-xs text-slate-300">P&L</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {portfolio.positions.map((position, idx) => (
                                            <tr
                                                key={idx}
                                                className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors"
                                            >
                                                <td className="py-2 px-3 font-semibold text-sm">
                                                    {position.trading_symbol}
                                                </td>
                                                <td className="py-2 px-3 text-xs">
                                                    <span className={`px-2 py-1 rounded ${position.product_type === 'INTRADAY'
                                                        ? 'bg-orange-500/20 text-orange-400'
                                                        : 'bg-blue-500/20 text-blue-400'
                                                        }`}>
                                                        {position.product_type}
                                                    </span>
                                                </td>
                                                <td className="text-right py-2 px-3 text-sm">{position.quantity}</td>
                                                <td className="text-right py-2 px-3 text-sm">
                                                    ₹{position.avg_price.toFixed(2)}
                                                </td>
                                                <td className="text-right py-2 px-3 text-sm">
                                                    ₹{position.ltp.toFixed(2)}
                                                </td>
                                                <td
                                                    className={`text-right py-2 px-3 text-sm font-semibold ${position.pnl >= 0 ? 'text-green-400' : 'text-red-400'
                                                        }`}
                                                >
                                                    {position.pnl >= 0 ? '+' : ''}₹{position.pnl.toFixed(2)}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}

                    {/* Funds Summary */}
                    {portfolio.funds && (
                        <div className="glass-card">
                            <h2 className="text-lg font-semibold mb-3">Funds & Margin</h2>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div className="bg-slate-800/50 rounded-lg p-4">
                                    <div className="text-sm text-slate-400 mb-1">Available Cash</div>
                                    <div className="text-2xl font-bold text-green-400">
                                        ₹{portfolio.funds.available_cash.toLocaleString()}
                                    </div>
                                </div>
                                <div className="bg-slate-800/50 rounded-lg p-4">
                                    <div className="text-sm text-slate-400 mb-1">Used Margin</div>
                                    <div className="text-2xl font-bold text-orange-400">
                                        ₹{portfolio.funds.used_margin.toLocaleString()}
                                    </div>
                                </div>
                                <div className="bg-slate-800/50 rounded-lg p-4">
                                    <div className="text-sm text-slate-400 mb-1">Available Margin</div>
                                    <div className="text-2xl font-bold text-blue-400">
                                        ₹{portfolio.funds.available_margin.toLocaleString()}
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default AngelOnePortfolioView;
