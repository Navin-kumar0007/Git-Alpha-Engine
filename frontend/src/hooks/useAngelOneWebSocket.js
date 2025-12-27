/**
 * useAngelOneWebSocket Hook
 * Manages WebSocket connection to receive live Angel One market data
 */

import { useState, useEffect, useRef, useCallback } from 'react';

const WS_URL = import.meta.env.VITE_API_URL?.replace('http', 'ws') || 'ws://127.0.0.1:8000';
const RECONNECT_DELAY = 3000; // 3 seconds
const MAX_RECONNECT_ATTEMPTS = 10;

export const useAngelOneWebSocket = () => {
    const [marketData, setMarketData] = useState({});
    const [isConnected, setIsConnected] = useState(false);
    const [error, setError] = useState(null);
    const [reconnectCount, setReconnectCount] = useState(0);

    const wsRef = useRef(null);
    const reconnectTimeoutRef = useRef(null);
    const isIntentionalClose = useRef(false);

    const connect = useCallback(() => {
        // Don't reconnect if intentionally closed or max attempts reached
        if (isIntentionalClose.current || reconnectCount >= MAX_RECONNECT_ATTEMPTS) {
            return;
        }

        try {
            // Get auth token
            const token = localStorage.getItem('git_alpha_token');
            if (!token) {
                setError('No authentication token found');
                return;
            }

            const wsUrl = `${WS_URL}/ws?token=${token}`;
            console.log('Connecting to Angel One WebSocket:', wsUrl);

            const ws = new WebSocket(wsUrl);
            wsRef.current = ws;

            ws.onopen = () => {
                console.log('✓ Angel One WebSocket connected');
                setIsConnected(true);
                setError(null);
                setReconnectCount(0);
            };

            ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);

                    // Handle different message types
                    if (message.type === 'MARKET_DATA') {
                        const tickData = message.data;
                        const token = tickData.token;

                        if (token) {
                            setMarketData((prev) => ({
                                ...prev,
                                [token]: {
                                    ...tickData,
                                    received_at: message.timestamp || new Date().toISOString(),
                                },
                            }));
                        }
                    } else if (message.type === 'CONNECTION') {
                        console.log('WebSocket:', message.message || message);
                    } else if (message.type === 'ERROR') {
                        console.error('WebSocket error message:', message.message);
                        setError(message.message);
                    }
                } catch (err) {
                    console.error('Error parsing WebSocket message:', err);
                }
            };

            ws.onerror = (err) => {
                console.warn('WebSocket error:', err);
                setError('WebSocket connection error');
            };

            ws.onclose = (event) => {
                console.log('WebSocket closed:', event.code, event.reason);
                setIsConnected(false);
                wsRef.current = null;

                // Attempt reconnection unless intentionally closed
                if (!isIntentionalClose.current && reconnectCount < MAX_RECONNECT_ATTEMPTS) {
                    setReconnectCount((prev) => prev + 1);
                    console.log(`Reconnecting in ${RECONNECT_DELAY / 1000}s... (attempt ${reconnectCount + 1}/${MAX_RECONNECT_ATTEMPTS})`);

                    reconnectTimeoutRef.current = setTimeout(() => {
                        connect();
                    }, RECONNECT_DELAY);
                } else if (reconnectCount >= MAX_RECONNECT_ATTEMPTS) {
                    setError('Max reconnection attempts reached. Please refresh the page.');
                }
            };
        } catch (err) {
            console.error('Failed to create WebSocket:', err);
            setError(`Failed to connect: ${err.message}`);
        }
    }, [reconnectCount]);

    const disconnect = useCallback(() => {
        isIntentionalClose.current = true;

        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
            reconnectTimeoutRef.current = null;
        }

        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }

        setIsConnected(false);
        setMarketData({});
        setReconnectCount(0);
    }, []);

    const reconnect = useCallback(() => {
        disconnect();
        isIntentionalClose.current = false;
        setReconnectCount(0);
        setTimeout(() => connect(), 500);
    }, [connect, disconnect]);

    // Auto-connect on mount
    useEffect(() => {
        isIntentionalClose.current = false;
        connect();

        // Cleanup on unmount
        return () => {
            isIntentionalClose.current = true;

            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }

            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, []); // Only run once on mount

    return {
        marketData,
        isConnected,
        error,
        reconnectCount,
        reconnect,
        disconnect,
    };
};

export default useAngelOneWebSocket;
