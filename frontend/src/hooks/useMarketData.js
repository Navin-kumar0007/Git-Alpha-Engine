/**
 * Custom hook for managing multi-market data
 * Provides utilities for fetching markets, indices, and live data
 */

import { useState, useEffect, useCallback } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

/**
 * Hook to fetch all available markets
 */
export const useMarkets = () => {
    const [markets, setMarkets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchMarkets = useCallback(async () => {
        try {
            setLoading(true);
            const response = await fetch(`${API_URL}/api/markets/`);

            if (!response.ok) {
                throw new Error('Failed to fetch markets');
            }

            const data = await response.json();
            setMarkets(data);
            setError(null);
        } catch (err) {
            setError(err.message);
            console.error('Error fetching markets:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchMarkets();
    }, [fetchMarkets]);

    return { markets, loading, error, refetch: fetchMarkets };
};

/**
 * Hook to fetch indices for a specific market
 */
export const useMarketIndices = (marketCode) => {
    const [indices, setIndices] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchIndices = useCallback(async () => {
        if (!marketCode) {
            setIndices([]);
            return;
        }

        try {
            setLoading(true);
            const response = await fetch(`${API_URL}/api/markets/${marketCode}/indices`);

            if (!response.ok) {
                throw new Error(`Failed to fetch indices for ${marketCode}`);
            }

            const data = await response.json();
            setIndices(data);
            setError(null);
        } catch (err) {
            setError(err.message);
            console.error('Error fetching indices:', err);
        } finally {
            setLoading(false);
        }
    }, [marketCode]);

    useEffect(() => {
        fetchIndices();
    }, [fetchIndices]);

    return { indices, loading, error, refetch: fetchIndices };
};

/**
 * Hook to fetch live data for a specific index
 */
export const useLiveData = (symbol, refreshInterval = 300000) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchLiveData = useCallback(async (forceRefresh = false) => {
        if (!symbol) return;

        try {
            setLoading(true);
            const url = forceRefresh
                ? `${API_URL}/api/markets/index/${symbol}/live?force_refresh=true`
                : `${API_URL}/api/markets/index/${symbol}/live`;

            const response = await fetch(url);

            if (!response.ok) {
                throw new Error(`Failed to fetch live data for ${symbol}`);
            }

            const liveData = await response.json();
            setData(liveData);
            setError(null);
        } catch (err) {
            setError(err.message);
            console.error('Error fetching live data:', err);
        } finally {
            setLoading(false);
        }
    }, [symbol]);

    useEffect(() => {
        fetchLiveData();

        // Set up auto-refresh
        const interval = setInterval(() => {
            fetchLiveData();
        }, refreshInterval);

        return () => clearInterval(interval);
    }, [fetchLiveData, refreshInterval]);

    return { data, loading, error, refetch: () => fetchLiveData(true) };
};

/**
 * Hook to fetch all indices from all markets with live data
 */
export const useAllMarketData = (refreshInterval = 300000) => {
    const [marketData, setMarketData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchAllData = useCallback(async () => {
        try {
            setLoading(true);

            // Fetch all markets first
            const marketsResponse = await fetch(`${API_URL}/api/markets/`);
            if (!marketsResponse.ok) throw new Error('Failed to fetch markets');
            const markets = await marketsResponse.json();

            // Fetch indices for each market
            const allIndices = [];
            for (const market of markets) {
                const indicesResponse = await fetch(`${API_URL}/api/markets/${market.code}/indices`);
                if (indicesResponse.ok) {
                    const indices = await indicesResponse.json();
                    allIndices.push(...indices.map(idx => ({
                        ...idx,
                        market_name: market.name,
                        market_code: market.code,
                        currency: market.currency
                    })));
                }
            }

            // Fetch live data for all indices
            const dataPromises = allIndices.map(async (index) => {
                try {
                    const liveResponse = await fetch(`${API_URL}/api/markets/index/${index.symbol}/live`);
                    if (liveResponse.ok) {
                        const liveData = await liveResponse.json();
                        return {
                            ...index,
                            ...liveData
                        };
                    }
                } catch (err) {
                    console.error(`Failed to fetch live data for ${index.symbol}:`, err);
                }
                return index;
            });

            const data = await Promise.all(dataPromises);
            setMarketData(data);
            setError(null);
        } catch (err) {
            setError(err.message);
            console.error('Error fetching all market data:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchAllData();

        // Set up auto-refresh
        const interval = setInterval(() => {
            fetchAllData();
        }, refreshInterval);

        return () => clearInterval(interval);
    }, [fetchAllData, refreshInterval]);

    return { marketData, loading, error, refetch: fetchAllData };
};
