import React, { useState, useMemo } from 'react';
import {
    ComposedChart,
    Line,
    Area,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    ReferenceLine,
} from 'recharts';
import { format } from 'date-fns';
import { BarChart3, TrendingUp, Activity, Layers } from 'lucide-react';

// Calculate technical indicators
const calculateRSI = (data, period = 14) => {
    if (!data || data.length <= period) return data;

    const rsi = [];
    for (let i = period; i < data.length; i++) {
        let gains = 0;
        let losses = 0;

        for (let j = i - period; j < i; j++) {
            const change = data[j + 1].close - data[j].close;
            if (change > 0) gains += change;
            else losses -= change;
        }

        const avgGain = gains / period;
        const avgLoss = losses / period;
        const rs = avgGain / avgLoss;
        const rsiValue = 100 - (100 / (1 + rs));

        rsi.push({ ...data[i], rsi: rsiValue });
    }
    return rsi;
};

const calculateMACD = (data, fast = 12, slow = 26, signal = 9) => {
    // Return empty if data is insufficient
    if (!data || data.length < slow) return data;

    const calculateEMA = (data, period) => {
        if (!data || data.length === 0 || !data[0]) return [];

        const k = 2 / (period + 1);
        let ema = data[0].close;
        const result = [ema];

        for (let i = 1; i < data.length; i++) {
            if (data[i] && data[i].close !== undefined) {
                ema = data[i].close * k + ema * (1 - k);
                result.push(ema);
            }
        }
        return result;
    };

    const fastEMA = calculateEMA(data, fast);
    const slowEMA = calculateEMA(data, slow);

    if (fastEMA.length === 0 || slowEMA.length === 0) return data;

    const macdLine = fastEMA.map((val, i) => val - slowEMA[i]);
    const signalLine = calculateEMA(macdLine.map((val, i) => ({ close: val })), signal);

    return data.map((d, i) => ({
        ...d,
        macd: macdLine[i],
        signal: signalLine[i],
        histogram: macdLine[i] - signalLine[i],
    }));
};

const calculateBollingerBands = (data, period = 20, stdDev = 2) => {
    if (!data || data.length < period) return data;

    const result = [];

    for (let i = period - 1; i < data.length; i++) {
        const slice = data.slice(i - period + 1, i + 1);
        const avg = slice.reduce((sum, d) => sum + d.close, 0) / period;
        const variance = slice.reduce((sum, d) => sum + Math.pow(d.close - avg, 2), 0) / period;
        const standardDeviation = Math.sqrt(variance);

        result.push({
            ...data[i],
            middleBand: avg,
            upperBand: avg + stdDev * standardDeviation,
            lowerBand: avg - stdDev * standardDeviation,
        });
    }
    return result;
};

const calculateMovingAverage = (data, period) => {
    if (!data || data.length < period) return data;

    const result = [];
    for (let i = period - 1; i < data.length; i++) {
        const slice = data.slice(i - period + 1, i + 1);
        const avg = slice.reduce((sum, d) => sum + d.close, 0) / period;
        result.push({ ...data[i], [`ma${period}`]: avg });
    }
    return result;
};

const MultiChartDashboard = ({ asset, historicalData = [] }) => {
    const [chartType, setChartType] = useState('candlestick');
    const [indicators, setIndicators] = useState({
        rsi: false,
        macd: false,
        bollinger: false,
        ma20: true,
        ma50: true,
        ma200: false,
    });
    const [timeRange, setTimeRange] = useState('1M');

    // Process data with indicators
    const processedData = useMemo(() => {
        if (!historicalData || historicalData.length === 0) return [];

        let data = [...historicalData];

        // Add moving averages
        if (indicators.ma20) data = calculateMovingAverage(data, 20);
        if (indicators.ma50) data = calculateMovingAverage(data, 50);
        if (indicators.ma200) data = calculateMovingAverage(data, 200);

        // Add Bollinger Bands
        if (indicators.bollinger) data = calculateBollingerBands(data);

        // Add MACD
        if (indicators.macd) data = calculateMACD(data);

        // Add RSI
        if (indicators.rsi) data = calculateRSI(data);

        return data;
    }, [historicalData, indicators]);

    const toggleIndicator = (indicator) => {
        setIndicators(prev => ({ ...prev, [indicator]: !prev[indicator] }));
    };

    // Custom tooltip
    const CustomTooltip = ({ active, payload }) => {
        if (!active || !payload || !payload.length) return null;

        const data = payload[0].payload;

        return (
            <div className="glass-card p-3 text-xs">
                <div className="font-semibold text-[var(--color-purple-light)] mb-2">
                    {data.date && format(new Date(data.date), 'MMM dd, yyyy')}
                </div>
                {data.open && (
                    <div className="space-y-1">
                        <div className="flex justify-between gap-4">
                            <span className="text-slate-400">Open:</span>
                            <span className="font-mono">${data.open.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between gap-4">
                            <span className="text-slate-400">High:</span>
                            <span className="font-mono text-gain">${data.high.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between gap-4">
                            <span className="text-slate-400">Low:</span>
                            <span className="font-mono text-loss">${data.low.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between gap-4">
                            <span className="text-slate-400">Close:</span>
                            <span className="font-mono font-semibold">${data.close.toFixed(2)}</span>
                        </div>
                        {data.volume && (
                            <div className="flex justify-between gap-4">
                                <span className="text-slate-400">Volume:</span>
                                <span className="font-mono text-xs">{(data.volume / 1000000).toFixed(2)}M</span>
                            </div>
                        )}
                    </div>
                )}
                {indicators.rsi && data.rsi && (
                    <div className="flex justify-between gap-4 mt-2 pt-2 border-t border-[var(--glass-border)]">
                        <span className="text-[var(--color-purple-light)]">RSI:</span>
                        <span className="font-mono">{data.rsi.toFixed(2)}</span>
                    </div>
                )}
                {indicators.macd && data.macd && (
                    <div className="mt-2 pt-2 border-t border-[var(--glass-border)] space-y-1">
                        <div className="flex justify-between gap-4">
                            <span className="text-[var(--color-cyan-light)]">MACD:</span>
                            <span className="font-mono">{data.macd.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between gap-4">
                            <span className="text-[var(--color-orange-light)]">Signal:</span>
                            <span className="font-mono">{data.signal.toFixed(2)}</span>
                        </div>
                    </div>
                )}
            </div>
        );
    };

    // Candlestick shape
    const Candlestick = (props) => {
        const { x, y, width, height, low, high, open, close } = props;
        const isGain = close > open;
        const color = isGain ? 'var(--color-gain)' : 'var(--color-loss)';
        const ratio = Math.abs(height / (open - close));

        return (
            <g stroke={color} fill="none" strokeWidth="2">
                <path d={`M ${x},${y} L ${x},${y + height}`} />
                <path
                    d={`M ${x},${isGain ? y + height : y} L ${x + width},${isGain ? y + height : y} L ${x + width},${isGain ? y : y + height} L ${x},${isGain ? y : y + height} Z`}
                    fill={color}
                    fillOpacity="0.8"
                />
            </g>
        );
    };

    return (
        <div className="space-y-4">
            {/* Controls */}
            <div className="glass-card p-4">
                <div className="flex flex-wrap items-center justify-between gap-4">
                    {/* Chart Type */}
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => setChartType('candlestick')}
                            className={`px-3 py-1.5 rounded-lg text-xs flex items-center gap-2 transition-all ${chartType === 'candlestick'
                                ? 'bg-[image:var(--gradient-primary)] text-white shadow-[var(--shadow-glow)]'
                                : 'hover:bg-[var(--color-purple)]/10 text-slate-300'
                                }`}
                        >
                            <BarChart3 size={14} /> Candlestick
                        </button>
                        <button
                            onClick={() => setChartType('line')}
                            className={`px-3 py-1.5 rounded-lg text-xs flex items-center gap-2 transition-all ${chartType === 'line'
                                ? 'bg-[image:var(--gradient-primary)] text-white shadow-[var(--shadow-glow)]'
                                : 'hover:bg-[var(--color-cyan)]/10 text-slate-300'
                                }`}
                        >
                            <TrendingUp size={14} /> Line
                        </button>
                        <button
                            onClick={() => setChartType('area')}
                            className={`px-3 py-1.5 rounded-lg text-xs flex items-center gap-2 transition-all ${chartType === 'area'
                                ? 'bg-[image:var(--gradient-primary)] text-white shadow-[var(--shadow-glow)]'
                                : 'hover:bg-[var(--color-emerald)]/10 text-slate-300'
                                }`}
                        >
                            <Activity size={14} /> Area
                        </button>
                    </div>

                    {/* Indicators */}
                    <div className="flex flex-wrap items-center gap-2">
                        <button
                            onClick={() => toggleIndicator('ma20')}
                            className={`px-2 py-1 rounded text-[10px] border transition-all ${indicators.ma20
                                ? 'border-[var(--color-cyan)] bg-[var(--color-cyan)]/20 text-[var(--color-cyan-light)]'
                                : 'border-slate-600 text-slate-400 hover:border-slate-500'
                                }`}
                        >
                            MA20
                        </button>
                        <button
                            onClick={() => toggleIndicator('ma50')}
                            className={`px-2 py-1 rounded text-[10px] border transition-all ${indicators.ma50
                                ? 'border-[var(--color-purple)] bg-[var(--color-purple)]/20 text-[var(--color-purple-light)]'
                                : 'border-slate-600 text-slate-400 hover:border-slate-500'
                                }`}
                        >
                            MA50
                        </button>
                        <button
                            onClick={() => toggleIndicator('bollinger')}
                            className={`px-2 py-1 rounded text-[10px] border transition-all ${indicators.bollinger
                                ? 'border-[var(--color-gold)] bg-[var(--color-gold)]/20 text-[var(--color-gold-light)]'
                                : 'border-slate-600 text-slate-400 hover:border-slate-500'
                                }`}
                        >
                            BB
                        </button>
                        <button
                            onClick={() => toggleIndicator('rsi')}
                            className={`px-2 py-1 rounded text-[10px] border transition-all ${indicators.rsi
                                ? 'border-[var(--color-pink)] bg-[var(--color-pink)]/20 text-[var(--color-pink-light)]'
                                : 'border-slate-600 text-slate-400 hover:border-slate-500'
                                }`}
                        >
                            RSI
                        </button>
                        <button
                            onClick={() => toggleIndicator('macd')}
                            className={`px-2 py-1 rounded text-[10px] border transition-all ${indicators.macd
                                ? 'border-[var(--color-orange)] bg-[var(--color-orange)]/20 text-[var(--color-orange-light)]'
                                : 'border-slate-600 text-slate-400 hover:border-slate-500'
                                }`}
                        >
                            MACD
                        </button>
                    </div>
                </div>
            </div>

            {/* Main Price Chart */}
            <div className="glass-card p-4">
                <div className="text-sm font-semibold mb-4 flex items-center gap-2">
                    <Layers size={16} className="text-[var(--color-purple-light)]" />
                    {asset?.name || 'Asset'} Price Chart
                </div>

                <ResponsiveContainer width="100%" height={400}>
                    <ComposedChart data={processedData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                        <defs>
                            <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="var(--color-purple)" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="var(--color-purple)" stopOpacity={0} />
                            </linearGradient>
                        </defs>

                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(139, 92, 246, 0.1)" />
                        <XAxis
                            dataKey="date"
                            tickFormatter={(date) => format(new Date(date), 'MMM dd')}
                            stroke="var(--color-text-muted)"
                            style={{ fontSize: '10px' }}
                        />
                        <YAxis
                            stroke="var(--color-text-muted)"
                            style={{ fontSize: '10px' }}
                            domain={['dataMin - 5', 'dataMax + 5']}
                        />
                        <YAxis
                            yAxisId="volume"
                            orientation="right"
                            stroke="var(--color-text-muted)"
                            style={{ fontSize: '10px' }}
                            tickFormatter={(value) => `${(value / 1000000).toFixed(1)}M`}
                        />
                        <Tooltip content={<CustomTooltip />} />

                        {/* Bollinger Bands */}
                        {indicators.bollinger && (
                            <>
                                <Line type="monotone" dataKey="upperBand" stroke="var(--color-rose)" strokeWidth={1} dot={false} strokeDasharray="3 3" />
                                <Line type="monotone" dataKey="middleBand" stroke="var(--color-gold)" strokeWidth={1.5} dot={false} />
                                <Line type="monotone" dataKey="lowerBand" stroke="var(--color-emerald)" strokeWidth={1} dot={false} strokeDasharray="3 3" />
                            </>
                        )}

                        {/* Moving Averages */}
                        {indicators.ma20 && <Line type="monotone" dataKey="ma20" stroke="var(--color-cyan)" strokeWidth={1.5} dot={false} />}
                        {indicators.ma50 && <Line type="monotone" dataKey="ma50" stroke="var(--color-purple)" strokeWidth={1.5} dot={false} />}
                        {indicators.ma200 && <Line type="monotone" dataKey="ma200" stroke="var(--color-gold)" strokeWidth={2} dot={false} />}

                        {/* Main Price Line/Area */}
                        {chartType === 'line' && (
                            <Line type="monotone" dataKey="close" stroke="var(--color-purple)" strokeWidth={2} dot={false} />
                        )}
                        {chartType === 'area' && (
                            <Area type="monotone" dataKey="close" stroke="var(--color-purple)" fillOpacity={1} fill="url(#colorPrice)" />
                        )}

                        {/* Volume Bars */}
                        <Bar dataKey="volume" fill="var(--color-cyan)" fillOpacity={0.3} yAxisId="volume" />
                    </ComposedChart>
                </ResponsiveContainer>
            </div>

            {/* RSI Indicator */}
            {indicators.rsi && processedData.some(d => d.rsi) && (
                <div className="glass-card p-4">
                    <div className="text-sm font-semibold mb-4 text-[var(--color-pink-light)]">RSI (14)</div>
                    <ResponsiveContainer width="100%" height={150}>
                        <ComposedChart data={processedData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(139, 92, 246, 0.1)" />
                            <XAxis dataKey="date" hide />
                            <YAxis domain={[0, 100]} stroke="var(--color-text-muted)" style={{ fontSize: '10px' }} />
                            <Tooltip />
                            <ReferenceLine y={70} stroke="var(--color-loss)" strokeDasharray="3 3" />
                            <ReferenceLine y={30} stroke="var(--color-gain)" strokeDasharray="3 3" />
                            <Line type="monotone" dataKey="rsi" stroke="var(--color-pink)" strokeWidth={2} dot={false} />
                        </ComposedChart>
                    </ResponsiveContainer>
                </div>
            )}

            {/* MACD Indicator */}
            {indicators.macd && processedData.some(d => d.macd) && (
                <div className="glass-card p-4">
                    <div className="text-sm font-semibold mb-4 text-[var(--color-orange-light)]">MACD (12, 26, 9)</div>
                    <ResponsiveContainer width="100%" height={150}>
                        <ComposedChart data={processedData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(139, 92, 246, 0.1)" />
                            <XAxis dataKey="date" hide />
                            <YAxis stroke="var(--color-text-muted)" style={{ fontSize: '10px' }} />
                            <Tooltip />
                            <ReferenceLine y={0} stroke="var(--color-text-muted)" />
                            <Bar dataKey="histogram" fill="var(--color-cyan)" fillOpacity={0.6} />
                            <Line type="monotone" dataKey="macd" stroke="var(--color-cyan)" strokeWidth={2} dot={false} />
                            <Line type="monotone" dataKey="signal" stroke="var(--color-orange)" strokeWidth={2} dot={false} />
                        </ComposedChart>
                    </ResponsiveContainer>
                </div>
            )}
        </div>
    );
};

export default MultiChartDashboard;
