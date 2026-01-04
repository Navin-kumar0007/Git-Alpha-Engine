import React, { useState, useEffect } from 'react';
import {
  Wallet,
  TrendingUp,
  TrendingDown,
  Plus,
  ArrowUpDown,
  DollarSign,
  Percent,
  BarChart3,
  RefreshCw,
  X,
  Building2,
} from 'lucide-react';
import Chart from './Chart';
import WealthCard from './WealthCard';
import AngelOnePortfolioView from './AngelOnePortfolioView';
import { useToast } from './Toast';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const getAuthHeaders = () => {
  const token = localStorage.getItem('git_alpha_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

/**
 * Portfolio Page Component - 25% More Compact
 * Complete portfolio management with transactions and analytics
 * Supports both manual portfolio and Angel One live sync
 */
const Portfolio = ({ user }) => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [portfolioView, setPortfolioView] = useState('manual'); // 'manual' or 'angelone'
  const [showTransactionModal, setShowTransactionModal] = useState(false);
  const [transactionForm, setTransactionForm] = useState({
    asset_id: '',
    transaction_type: 'buy',
    amount: '',
    price: '',
    notes: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const toast = useToast();

  // Fetch portfolio summary
  const fetchPortfolio = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_URL}/api/portfolio/summary`, {
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        const data = await res.json();
        setSummary(data);
      }
    } catch (error) {
      console.error('Failed to fetch portfolio:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchPortfolio();
    }
  }, [user]);

  // Handle transaction submission
  const handleSubmitTransaction = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const res = await fetch(`${API_URL}/api/portfolio/transaction`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
        body: JSON.stringify({
          asset_id: transactionForm.asset_id,
          transaction_type: transactionForm.transaction_type,
          amount: parseFloat(transactionForm.amount),
          price: parseFloat(transactionForm.price),
          notes: transactionForm.notes || null,
        }),
      });

      if (res.ok) {
        toast.success(`${transactionForm.transaction_type.toUpperCase()} transaction added!`);
        setShowTransactionModal(false);
        setTransactionForm({
          asset_id: '',
          transaction_type: 'buy',
          amount: '',
          price: '',
          notes: '',
        });
        fetchPortfolio();
      } else {
        const error = await res.json();
        toast.error(error.detail || 'Failed to add transaction');
      }
    } catch (error) {
      toast.error('Network error');
    } finally {
      setSubmitting(false);
    }
  };

  if (!user) {
    return (
      <div className="flex items-center justify-center h-96">
        <p className="text-slate-400">Please login to view your portfolio</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <RefreshCw className="animate-spin text-indigo-400" size={32} />
      </div>
    );
  }

  const isEmpty = !summary || summary.holdings.length === 0;

  // If Angel One view is selected, show that component
  if (portfolioView === 'angelone') {
    return (
      <div className="space-y-6 animate-fade-in">
        {/* Toggle Buttons */}
        <div className="flex items-center justify-between">
          <div className="inline-flex bg-slate-800/50 rounded-lg p-1 gap-1">
            <button
              onClick={() => setPortfolioView('manual')}
              className="px-4 py-2 rounded-md text-sm font-medium transition-all text-slate-300 hover:text-white"
            >
              <Wallet size={16} className="inline mr-2" />
              Manual Portfolio
            </button>
            <button
              onClick={() => setPortfolioView('angelone')}
              className="px-4 py-2 rounded-md text-sm font-medium transition-all bg-indigo-600 text-white shadow-lg"
            >
              <Building2 size={16} className="inline mr-2" />
              Angel One Portfolio
            </button>
          </div>
        </div>

        {/* Angel One Portfolio View */}
        <AngelOnePortfolioView user={user} />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Toggle Buttons + Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="inline-flex bg-slate-800/50 rounded-lg p-1 gap-1">
          <button
            onClick={() => setPortfolioView('manual')}
            className="px-4 py-2 rounded-md text-sm font-medium transition-all bg-indigo-600 text-white shadow-lg"
          >
            <Wallet size={16} className="inline mr-2" />
            Manual Portfolio
          </button>
          <button
            onClick={() => setPortfolioView('angelone')}
            className="px-4 py-2 rounded-md text-sm font-medium transition-all text-slate-300 hover:text-white"
          >
            <Building2 size={16} className="inline mr-2" />
            Angel One Portfolio
          </button>
        </div>
        <button
          onClick={() => setShowTransactionModal(true)}
          className="btn btn-primary"
        >
          <Plus size={18} />
          Add Transaction
        </button>
      </div>

      {isEmpty ? (
        /* Empty State */
        <div className="glass-card text-center py-16">
          <Wallet size={64} className="mx-auto text-slate-600 mb-4" />
          <h3 className="text-xl font-semibold mb-2">No Holdings Yet</h3>
          <p className="text-slate-400 mb-6">
            Start building your portfolio by adding your first transaction
          </p>
          <button
            onClick={() => setShowTransactionModal(true)}
            className="btn btn-primary"
          >
            <Plus size={20} />
            Add First Transaction
          </button>
        </div>
      ) : (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <WealthCard
              title="Total Value"
              value={summary.total_value}
              icon={Wallet}
              gradient={true}
            />
            <WealthCard
              title="Total Cost"
              value={summary.total_cost}
              icon={DollarSign}
            />
            <WealthCard
              title="Total P&L"
              value={summary.total_pnl}
              change={summary.total_pnl_percentage}
              icon={summary.total_pnl >= 0 ? TrendingUp : TrendingDown}
            />
            <WealthCard
              title="ROI"
              value={summary.total_pnl_percentage}
              suffix="%"
              prefix=""
              icon={Percent}
            />
          </div>

          {/* Holdings Table */}
          <div className="glass-card">
            <h2 className="text-lg font-semibold mb-3">Holdings</h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-2 px-3 text-xs text-slate-300">Asset</th>
                    <th className="text-right py-2 px-3 text-xs text-slate-300">Amount</th>
                    <th className="text-right py-2 px-3 text-xs text-slate-300">Avg Entry</th>
                    <th className="text-right py-2 px-3 text-xs text-slate-300">Current Price</th>
                    <th className="text-right py-2 px-3 text-xs text-slate-300">Value</th>
                    <th className="text-right py-2 px-3 text-xs text-slate-300">P&L</th>
                    <th className="text-right py-2 px-3 text-xs text-slate-300">P&L %</th>
                  </tr>
                </thead>
                <tbody>
                  {summary.holdings.map((holding) => (
                    <tr
                      key={holding.asset_id}
                      className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors"
                    >
                      <td className="py-2 px-3">
                        <div>
                          <div className="font-semibold text-sm">{holding.name}</div>
                          <div className="text-xs text-slate-400">{holding.symbol}</div>
                        </div>
                      </td>
                      <td className="text-right py-2 px-3 text-sm">{holding.amount.toFixed(4)}</td>
                      <td className="text-right py-2 px-3 text-sm">
                        ${holding.avg_entry_price.toLocaleString(undefined, {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}
                      </td>
                      <td className="text-right py-2 px-3 text-sm">
                        ${holding.current_price.toLocaleString(undefined, {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}
                      </td>
                      <td className="text-right py-2 px-3 text-sm font-semibold">
                        ${holding.current_value.toLocaleString(undefined, {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}
                      </td>
                      <td
                        className={`text-right py-2 px-3 text-sm font-semibold ${holding.pnl >= 0 ? 'text-green-400' : 'text-red-400'
                          }`}
                      >
                        {holding.pnl >= 0 ? '+' : ''}
                        ${holding.pnl.toLocaleString(undefined, {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}
                      </td>
                      <td
                        className={`text-right py-2 px-3 text-sm font-semibold ${holding.pnl_percentage >= 0 ? 'text-green-400' : 'text-red-400'
                          }`}
                      >
                        {holding.pnl_percentage >= 0 ? '+' : ''}
                        {holding.pnl_percentage.toFixed(2)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Top/Worst Performers */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {summary.top_performers.length > 0 && (
              <div className="glass-card">
                <h3 className="text-base font-semibold mb-2 flex items-center gap-2">
                  <TrendingUp className="text-green-400" size={18} />
                  Top Performers
                </h3>
                <div className="space-y-2">
                  {summary.top_performers.map((holding) => (
                    <div
                      key={holding.asset_id}
                      className="flex items-center justify-between p-2 bg-green-500/10 rounded-lg text-sm"
                    >
                      <div>
                        <div className="font-semibold">{holding.name}</div>
                        <div className="text-xs text-slate-400">{holding.symbol}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-green-400 font-semibold">
                          +{holding.pnl_percentage.toFixed(2)}%
                        </div>
                        <div className="text-xs text-slate-400">
                          ${holding.pnl.toFixed(2)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {summary.worst_performers.length > 0 && (
              <div className="glass-card">
                <h3 className="text-base font-semibold mb-2 flex items-center gap-2">
                  <TrendingDown className="text-red-400" size={18} />
                  Worst Performers
                </h3>
                <div className="space-y-2">
                  {summary.worst_performers.map((holding) => (
                    <div
                      key={holding.asset_id}
                      className="flex items-center justify-between p-2 bg-red-500/10 rounded-lg text-sm"
                    >
                      <div>
                        <div className="font-semibold">{holding.name}</div>
                        <div className="text-xs text-slate-400">{holding.symbol}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-red-400 font-semibold">
                          {holding.pnl_percentage.toFixed(2)}%
                        </div>
                        <div className="text-xs text-slate-400">
                          ${holding.pnl.toFixed(2)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </>
      )}

      {/* Transaction Modal */}
      {showTransactionModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="glass-card max-w-md w-full animate-scale-up">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Add Transaction</h2>
              <button
                onClick={() => setShowTransactionModal(false)}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <X size={24} />
              </button>
            </div>

            <form onSubmit={handleSubmitTransaction} className="space-y-4">
              <div>
                <label className="block text-sm text-slate-300 mb-2">Asset ID</label>
                <input
                  type="text"
                  value={transactionForm.asset_id}
                  onChange={(e) =>
                    setTransactionForm({ ...transactionForm, asset_id: e.target.value })
                  }
                  placeholder="bitcoin, ethereum, solana..."
                  className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm text-slate-300 mb-2">Type</label>
                <select
                  value={transactionForm.transaction_type}
                  onChange={(e) =>
                    setTransactionForm({ ...transactionForm, transaction_type: e.target.value })
                  }
                  className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="buy">Buy</option>
                  <option value="sell">Sell</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-slate-300 mb-2">Amount</label>
                  <input
                    type="number"
                    step="any"
                    value={transactionForm.amount}
                    onChange={(e) =>
                      setTransactionForm({ ...transactionForm, amount: e.target.value })
                    }
                    placeholder="0.5"
                    className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm text-slate-300 mb-2">Price ($)</label>
                  <input
                    type="number"
                    step="any"
                    value={transactionForm.price}
                    onChange={(e) =>
                      setTransactionForm({ ...transactionForm, price: e.target.value })
                    }
                    placeholder="50000"
                    className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm text-slate-300 mb-2">Notes (Optional)</label>
                <textarea
                  value={transactionForm.notes}
                  onChange={(e) =>
                    setTransactionForm({ ...transactionForm, notes: e.target.value })
                  }
                  placeholder="Long-term hold..."
                  className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500 resize-none"
                  rows={3}
                />
              </div>

              {transactionForm.amount && transactionForm.price && (
                <div className="bg-indigo-500/10 border border-indigo-500/30 rounded-lg p-3">
                  <div className="text-sm text-slate-300">Total Value</div>
                  <div className="text-xl font-bold text-indigo-400">
                    $
                    {(parseFloat(transactionForm.amount) * parseFloat(transactionForm.price)).toLocaleString(
                      undefined,
                      { minimumFractionDigits: 2, maximumFractionDigits: 2 }
                    )}
                  </div>
                </div>
              )}

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowTransactionModal(false)}
                  className="flex-1 btn btn-ghost"
                  disabled={submitting}
                >
                  Cancel
                </button>
                <button type="submit" className="flex-1 btn btn-primary" disabled={submitting}>
                  {submitting ? 'Adding...' : 'Add Transaction'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Portfolio;
