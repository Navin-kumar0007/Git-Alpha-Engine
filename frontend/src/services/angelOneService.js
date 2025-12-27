/**
 * Angel One API Service
 * Client for interacting with Angel One backend endpoints
 */

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const getAuthHeaders = () => {
    const token = localStorage.getItem("git_alpha_token");
    return token ? { Authorization: `Bearer ${token}` } : {};
};

export const angelOneService = {
    /**
     * Get current status of Angel One service
     * @returns {Promise<{is_running: boolean, is_connected: boolean, subscribed_tokens: Array, last_update: string}>}
     */
    async getStatus() {
        const response = await fetch(`${API_URL}/api/angel-one/status`, {
            headers: {
                "Content-Type": "application/json",
                ...getAuthHeaders(),
            },
        });

        if (!response.ok) {
            throw new Error(`Failed to get status: ${response.statusText}`);
        }

        return response.json();
    },

    /**
     * Start Angel One WebSocket service
     * @param {Array} tokens - Token subscriptions [{exchangeType: number, tokens: string[]}]
     * @param {number} mode - Subscription mode (1=LTP, 3=Full Quote)
     * @returns {Promise<{success: boolean, message: string}>}
     */
    async startService(tokens, mode = 1) {
        const response = await fetch(`${API_URL}/api/angel-one/start`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...getAuthHeaders(),
            },
            body: JSON.stringify({ tokens, mode }),
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({
                detail: response.statusText,
            }));
            throw new Error(error.detail || "Failed to start service");
        }

        return response.json();
    },

    /**
     * Stop Angel One WebSocket service
     * @returns {Promise<{success: boolean, message: string}>}
     */
    async stopService() {
        const response = await fetch(`${API_URL}/api/angel-one/stop`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...getAuthHeaders(),
            },
        });

        if (!response.ok) {
            throw new Error(`Failed to stop service: ${response.statusText}`);
        }

        return response.json();
    },

    /**
     * Subscribe to additional tokens
     * @param {Array} tokens - Token subscriptions [{exchangeType: number, tokens: string[]}]
     * @param {number} mode - Subscription mode (1=LTP, 3=Full Quote)
     * @returns {Promise<{success: boolean, message: string}>}
     */
    async subscribe(tokens, mode = 1) {
        const response = await fetch(`${API_URL}/api/angel-one/subscribe`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...getAuthHeaders(),
            },
            body: JSON.stringify({ tokens, mode }),
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({
                detail: response.statusText,
            }));
            throw new Error(error.detail || "Failed to subscribe");
        }

        return response.json();
    },

    /**
     * Unsubscribe from tokens
     * @param {Array} tokens - Token subscriptions [{exchangeType: number, tokens: string[]}]
     * @param {number} mode - Subscription mode
     * @returns {Promise<{success: boolean, message: string}>}
     */
    async unsubscribe(tokens, mode = 1) {
        const response = await fetch(`${API_URL}/api/angel-one/unsubscribe`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...getAuthHeaders(),
            },
            body: JSON.stringify({ tokens, mode }),
        });

        if (!response.ok) {
            throw new Error(`Failed to unsubscribe: ${response.statusText}`);
        }

        return response.json();
    },

    /**
     * Get last cached tick for a token
     * @param {string} token - Token ID
     * @returns {Promise<{success: boolean, data: object}>}
     */
    async getLastTick(token) {
        const response = await fetch(`${API_URL}/api/angel-one/last-tick/${token}`, {
            headers: {
                "Content-Type": "application/json",
                ...getAuthHeaders(),
            },
        });

        if (!response.ok) {
            throw new Error(`Failed to get last tick: ${response.statusText}`);
        }

        return response.json();
    },
};

// Common token database for easy access
export const ANGEL_ONE_TOKENS = {
    indices: [
        { token: "26000", symbol: "NIFTY50", name: "NIFTY 50", exchangeType: 1 },
        { token: "26009", symbol: "BANKNIFTY", name: "NIFTY BANK", exchangeType: 1 },
        { token: "26017", symbol: "NIFTYIT", name: "NIFTY IT", exchangeType: 1 },
        { token: "26037", symbol: "NIFTYFIN", name: "NIFTY FIN SERVICE", exchangeType: 1 },
        { token: "26074", symbol: "MIDCAP100", name: "NIFTY MIDCAP 100", exchangeType: 1 },
    ],
    stocks: [
        { token: "1594", symbol: "RELIANCE", name: "Reliance Industries", exchangeType: 1 },
        { token: "3045", symbol: "SBIN", name: "State Bank of India", exchangeType: 1 },
        { token: "2885", symbol: "INFY", name: "Infosys", exchangeType: 1 },
        { token: "1660", symbol: "TATASTEEL", name: "Tata Steel", exchangeType: 1 },
        { token: "1333", symbol: "HDFCBANK", name: "HDFC Bank", exchangeType: 1 },
        { token: "4963", symbol: "ICICIBANK", name: "ICICI Bank", exchangeType: 1 },
        { token: "11536", symbol: "TCS", name: "TCS", exchangeType: 1 },
        { token: "3456", symbol: "ITC", name: "ITC Ltd", exchangeType: 1 },
    ],
};

export default angelOneService;
