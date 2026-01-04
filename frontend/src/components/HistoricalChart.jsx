import React, { useState, useEffect, useRef } from 'react';
import {
    Chart as ChartJS,
    TimeScale,
    LinearScale,
    Tooltip,
    Legend,
} from 'chart.js';
import { CandlestickController, CandlestickElement } from 'chartjs-chart-financial';
import 'chartjs-adapter-date-fns';  // Import the date adapter
import { Chart } from 'react-chartjs-2';
import { RefreshCw, Calendar, Clock, TrendingUp } from 'lucide-react';
import { useToast } from './Toast';

// Register Chart.js components
ChartJS.register(
    TimeScale,
    LinearScale,
    CandlestickController,
    CandlestickElement,
    Tooltip,
    Legend
);

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const getAuthHeaders = () => {
    const token = localStorage.getItem('git_alpha_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
};

/**
 * Historical Chart Component
 * Candlestick chart with timeframe and interval selection
 */
const HistoricalChart = ({ user, symbol, exchange = 'NSE' }) => {
    const chartRef = useRef(null);
    const [loading, setLoading] = useState(false);
    const [candles, setCandles] = useState([]);
    const [intervals, setIntervals] = useState([]);
    const [selectedInterval, setSelectedInterval] = useState('ONE_DAY');
    const [selectedRange, setSelectedRange] = useState('1M');
    const toast = useToast();

    // Timeframe options
    const rangeOptions = ['1D', '1W', '1M', '3M', '6M', '1Y', '5Y'];

    // Fetch available intervals on mount
    useEffect(() => {
        fetchIntervals();
    }, []);

    // Fetch candles when symbol/interval/range changes
    useEffect(() => {
        if (symbol && symbol.symboltoken) {
            fetchCandles();
        }
    }, [symbol, selectedInterval, selectedRange]);

    const fetchIntervals = async () => {
        try {
            const res = await fetch(`${API_URL}/api/angel-historical/intervals`, {
                headers: getAuthHeaders(),
            });

            if (res.ok) {
                const data = await res.json();
                setIntervals(data);
            }
        } catch (error) {
            console.error('Failed to fetch intervals:', error);
        }
    };

    const fetchCandles = async () => {
        if (!symbol || !symbol.symboltoken) return;

        setLoading(true);

        try {
            // Get date range
            const rangeRes = await fetch(
                `${API_URL}/api/angel-historical/quick-range/${selectedRange}`,
                { headers: getAuthHeaders() }
            );

            if (!rangeRes.ok) {
                throw new Error('Failed to get date range');
            }

            const rangeData = await rangeRes.json();

            // Fetch candles
            const params = new URLSearchParams({
                exchange: exchange,
                symboltoken: symbol.symboltoken,
                interval: selectedInterval,
                from_date: rangeData.from_date,
                to_date: rangeData.to_date,
                trading_symbol: symbol.name || ''
            });

            const res = await fetch(
                `${API_URL}/api/angel-historical/candles?${params}`,
                { headers: getAuthHeaders() }
            );

            const data = await res.json();

            if (data.success) {
                setCandles(data.data);
                if (data.cached) {
                    toast.success(`Loaded ${data.data.length} candles from cache`);
                } else {
                    toast.success(`Fetched ${data.data.length} candles`);
                }
            } else {
                toast.error(data.error || 'Failed to fetch candles');
            }
        } catch (error) {
            console.error('Error fetching candles:', error);
            toast.error('Failed to load chart data');
        } finally {
            setLoading(false);
        }
    };

    // Prepare chart data
    const chartData = {
        datasets: [
            {
                type: 'candlestick',  // Explicit type for the financial plugin
                label: symbol?.name || 'Price',
                data: candles.map(c => ({
                    x: new Date(c.timestamp).getTime(),  // Convert to milliseconds
                    o: c.open,
                    h: c.high,
                    l: c.low,
                    c: c.close,
                })),
                color: {
                    up: '#10b981',      // Green for bullish
                    down: '#ef4444',    // Red for bearish
                    unchanged: '#6b7280',
                },
                borderColor: {
                    up: '#10b981',
                    down: '#ef4444',
                    unchanged: '#6b7280',
                },
                borderWidth: 2,
            },
        ],
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                type: 'time',  // Use 'time' instead of 'timeseries'
                time: {
                    unit: selectedInterval === 'ONE_DAY' ? 'day' : selectedInterval.includes('MINUTE') ? 'hour' : 'day',
                    displayFormats: {
                        hour: 'MMM d, HH:mm',
                        day: 'MMM d',
                    }
                },
                grid: {
                    color: 'rgba(148, 163, 184, 0.1)',
                },
                ticks: {
                    color: '#94a3b8',
                    maxRotation: 0,
                    autoSkip: true,
                    maxTicksLimit: 10,
                },
            },
            y: {
                position: 'right',
                grid: {
                    color: 'rgba(148, 163, 184, 0.1)',
                },
                ticks: {
                    color: '#94a3b8',
                    callback: function (value) {
                        return '₹' + value.toLocaleString();
                    }
                },
            },
        },
        plugins: {
            legend: {
                display: false,
            },
            tooltip: {
                enabled: true,
                mode: 'index',
                intersect: false,
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                titleColor: '#fff',
                bodyColor: '#fff',
                borderColor: '#4f46e5',
                borderWidth: 1,
                padding: 12,
                displayColors: false,
                callbacks: {
                    title: (context) => {
                        const date = new Date(context[0].parsed.x);
                        return date.toLocaleString('en-US', {
                            month: 'short',
                            day: 'numeric',
                            year: 'numeric',
                            hour: selectedInterval.includes('MINUTE') || selectedInterval.includes('HOUR') ? 'numeric' : undefined,
                            minute: selectedInterval.includes('MINUTE') ? 'numeric' : undefined,
                        });
                    },
                    label: (context) => {
                        const point = context.raw;
                        return [
                            `Open: ₹${point.o.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
                            `High: ₹${point.h.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
                            `Low: ₹${point.l.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
                            `Close: ₹${point.c.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
                        ];
                    },
                },
            },
        },
    };

    if (!symbol) {
        return (
            <div className="glass-card flex items-center justify-center h-96">
                <div className="text-center">
                    <TrendingUp size={64} className="mx-auto text-slate-600 mb-4" />
                    <h3 className="text-xl font-semibold mb-2">No Symbol Selected</h3>
                    <p className="text-slate-400">Select a symbol to view historical price data</p>
                </div>
            </div>
        );
    }

    return (
        <div className="glass-card space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between flex-wrap gap-4">
                <div>
                    <h2 className="text-xl font-bold">{symbol.name}</h2>
                    <p className="text-sm text-slate-400">
                        {exchange} • Token: {symbol.symboltoken}
                    </p>
                </div>

                <button
                    onClick={fetchCandles}
                    disabled={loading}
                    className="btn btn-ghost"
                >
                    <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
                    Refresh
                </button>
            </div>

            {/* Controls */}
            <div className="flex items-center gap-4 flex-wrap">
                {/* Timeframe Selector */}
                <div className="flex items-center gap-2">
                    <Calendar size={16} className="text-slate-400" />
                    <div className="inline-flex bg-slate-800/50 rounded-lg p-1 gap-1">
                        {rangeOptions.map((range) => (
                            <button
                                key={range}
                                onClick={() => setSelectedRange(range)}
                                className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${selectedRange === range
                                    ? 'bg-indigo-600 text-white'
                                    : 'text-slate-300 hover:text-white'
                                    }`}
                            >
                                {range}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Interval Selector */}
                <div className="flex items-center gap-2">
                    <Clock size={16} className="text-slate-400" />
                    <select
                        value={selectedInterval}
                        onChange={(e) => setSelectedInterval(e.target.value)}
                        className="bg-slate-800/50 border border-slate-700 rounded-lg px-3 py-1 text-sm text-white focus:outline-none focus:border-indigo-500"
                    >
                        {intervals.map((int) => (
                            <option key={int.value} value={int.value}>
                                {int.display}
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Chart */}
            <div className="relative" style={{ height: '500px' }}>
                {loading ? (
                    <div className="absolute inset-0 flex items-center justify-center bg-slate-900/50 rounded-lg backdrop-blur-sm">
                        <RefreshCw size={32} className="animate-spin text-indigo-400" />
                    </div>
                ) : candles.length === 0 ? (
                    <div className="absolute inset-0 flex items-center justify-center">
                        <div className="text-center">
                            <TrendingUp size={48} className="mx-auto text-slate-600 mb-2" />
                            <p className="text-slate-400">No data available for this period</p>
                        </div>
                    </div>
                ) : (
                    <Chart
                        ref={chartRef}
                        type="candlestick"
                        data={chartData}
                        options={chartOptions}
                    />
                )}
            </div>

            {/* Stats */}
            {candles.length > 0 && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-slate-700">
                    <div>
                        <div className="text-xs text-slate-400 mb-1">Candles</div>
                        <div className="text-lg font-semibold">{candles.length}</div>
                    </div>
                    <div>
                        <div className="text-xs text-slate-400 mb-1">First</div>
                        <div className="text-lg font-semibold">
                            ₹{candles[0]?.close.toFixed(2)}
                        </div>
                    </div>
                    <div>
                        <div className="text-xs text-slate-400 mb-1">Latest</div>
                        <div className="text-lg font-semibold">
                            ₹{candles[candles.length - 1]?.close.toFixed(2)}
                        </div>
                    </div>
                    <div>
                        <div className="text-xs text-slate-400 mb-1">Change</div>
                        <div
                            className={`text-lg font-semibold ${candles[candles.length - 1]?.close >= candles[0]?.close
                                ? 'text-green-400'
                                : 'text-red-400'
                                }`}
                        >
                            {(
                                ((candles[candles.length - 1]?.close - candles[0]?.close) /
                                    candles[0]?.close) *
                                100
                            ).toFixed(2)}
                            %
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default HistoricalChart;
