/**
 * CandlestickChart Component
 * Professional candlestick chart using lightweight-charts
 */

import React, { useEffect, useRef, useState } from 'react';
import { createChart } from 'lightweight-charts';
import { Loader2, AlertCircle } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const CandlestickChart = ({
    symbol,
    period = '3mo',
    interval = '1d',
    height = 400,
    showVolume = true
}) => {
    const chartContainerRef = useRef(null);
    const chartRef = useRef(null);
    const candlestickSeriesRef = useRef(null);
    const volumeSeriesRef = useRef(null);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [chartData, setChartData] = useState(null);

    // Fetch historical data
    useEffect(() => {
        if (!symbol) return;

        const fetchData = async () => {
            try {
                setLoading(true);
                setError(null);

                const response = await fetch(
                    `${API_URL}/api/markets/index/${symbol}/historical?period=${period}&interval=${interval}`
                );

                if (!response.ok) {
                    throw new Error('Failed to fetch chart data');
                }

                const data = await response.json();
                setChartData(data);
            } catch (err) {
                setError(err.message);
                console.error('Error fetching chart data:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [symbol, period, interval]);

    // Create and update chart
    useEffect(() => {
        if (!chartContainerRef.current || !chartData || loading) return;

        // Create chart instance
        const chart = createChart(chartContainerRef.current, {
            layout: {
                background: { color: 'transparent' },
                textColor: '#94a3b8',
            },
            grid: {
                vertLines: { color: 'rgba(148, 163, 184, 0.1)' },
                horzLines: { color: 'rgba(148, 163, 184, 0.1)' },
            },
            width: chartContainerRef.current.clientWidth,
            height: height,
            timeScale: {
                borderColor: '#334155',
                timeVisible: true,
            },
            rightPriceScale: {
                borderColor: '#334155',
            },
            crosshair: {
                mode: 1,
                vertLine: {
                    color: '#06b6d4',
                    width: 1,
                    style: 2,
                    labelBackgroundColor: '#06b6d4',
                },
                horzLine: {
                    color: '#06b6d4',
                    width: 1,
                    style: 2,
                    labelBackgroundColor: '#06b6d4',
                },
            },
        });

        chartRef.current = chart;

        // Add candlestick series
        const candlestickSeries = chart.addCandlestickSeries({
            upColor: '#10b981',
            downColor: '#ef4444',
            borderUpColor: '#10b981',
            borderDownColor: '#ef4444',
            wickUpColor: '#10b981',
            wickDownColor: '#ef4444',
        });

        candlestickSeriesRef.current = candlestickSeries;

        // Transform and set candlestick data
        const candlestickData = chartData.data.map(item => ({
            time: new Date(item.date).getTime() / 1000,
            open: item.open_price,
            high: item.high,
            low: item.low,
            close: item.close,
        }));

        candlestickSeries.setData(candlestickData);

        // Add volume series if enabled
        if (showVolume) {
            const volumeSeries = chart.addHistogramSeries({
                color: '#26a69a',
                priceFormat: {
                    type: 'volume',
                },
                priceScaleId: '',
                scaleMargins: {
                    top: 0.8,
                    bottom: 0,
                },
            });

            volumeSeriesRef.current = volumeSeries;

            const volumeData = chartData.data.map(item => ({
                time: new Date(item.date).getTime() / 1000,
                value: item.volume,
                color: item.close >= item.open_price ? 'rgba(16, 185, 129, 0.5)' : 'rgba(239, 68, 68, 0.5)',
            }));

            volumeSeries.setData(volumeData);
        }

        // Fit content
        chart.timeScale().fitContent();

        // Handle resize
        const handleResize = () => {
            if (chartContainerRef.current && chartRef.current) {
                chartRef.current.applyOptions({
                    width: chartContainerRef.current.clientWidth,
                });
            }
        };

        window.addEventListener('resize', handleResize);

        // Cleanup
        return () => {
            window.removeEventListener('resize', handleResize);
            if (chartRef.current) {
                chartRef.current.remove();
                chartRef.current = null;
            }
        };
    }, [chartData, height, showVolume, loading]);

    if (loading) {
        return (
            <div className="flex items-center justify-center" style={{ height }}>
                <div className="text-center">
                    <Loader2 className="w-8 h-8 animate-spin text-cyan-400 mx-auto mb-2" />
                    <p className="text-sm text-slate-400">Loading chart...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center" style={{ height }}>
                <div className="text-center">
                    <AlertCircle className="w-10 h-10 text-red-400 mx-auto mb-2" />
                    <p className="text-sm text-slate-300 mb-1">Failed to load chart</p>
                    <p className="text-xs text-slate-500">{error}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="relative">
            <div ref={chartContainerRef} className="rounded-lg overflow-hidden" />
        </div>
    );
};

export default CandlestickChart;
