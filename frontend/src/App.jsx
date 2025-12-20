import React, { useState, useEffect, useRef, useMemo, useCallback } from "react";
import {
  Github,
  TrendingUp,
  Activity,
  Code,
  Terminal,
  Search,
  Bell,
  User,
  Menu,
  LogOut,
  Cpu,
  Zap,
  Lock,
  Mail,
  GitCommit,
  ArrowLeft,
  Command,
  Layers,
  Users,
  MessageSquare,
  AlertCircle,
  CheckCircle,
  X,
  RefreshCw,
  Radio,
  Heart,
  Camera,
  Loader2,
  ChevronRight,
  BarChart3,
  Globe,
  MoreHorizontal,
  ArrowUpRight,
  ArrowDownRight,
  Settings,
  Shield,
  Wallet,
  Sliders,
  Bot,
  Newspaper,
} from "lucide-react";
import Portfolio from "./components/Portfolio";
import AIAssistant from "./components/AIAssistant";
import ColorShowcase from "./components/ColorShowcase";
import ChartsView from "./components/ChartsView";
import MultiChartDashboard from "./components/charts/MultiChartDashboard";
import MarketHeatmap from "./components/charts/MarketHeatmap";
import { ToastContainer, useToast } from "./components/Toast";
import MarketDashboard from "./components/MarketDashboard";
import { OAuthButton, GoogleIcon, GitHubIcon } from './components/OAuthButtons';
import FloatingAIWidget from './components/FloatingAIWidget';
import CollapsibleSidebar from './components/CollapsibleSidebar';
import ThemeToggle from './components/ThemeToggle';
import NewsHub from './components/NewsHub';
import { Card } from './ui/card';
import Pill from './ui/Pill';
import Tag from './ui/Tag';
import ProfilePanel from './components/ProfilePanel';
import PreferencesDialog from './components/PreferencesDialog';


/* ------------------------------
   CONFIG
------------------------------ */

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const getAuthToken = () => {
  try {
    return localStorage.getItem("git_alpha_token") || null;
  } catch {
    return null;
  }
};

const getAuthHeaders = () => {
  const token = getAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const formatCurrency = (val, symbol) => {
  const safeSymbol = symbol || "USD";
  const currency = ["NIFTY", "SENSEX", "BANKNIFTY", "RELIANCE", "TCS"].includes(
    safeSymbol
  )
    ? "INR"
    : "USD";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(val);
};

// local demo data fallback
const getMockAssets = () => [
  {
    id: "btc",
    name: "Bitcoin",
    symbol: "BTC",
    price: 64200,
    change24h: 2.4,
    alphaScore: 87,
    repo: "bitcoin/bitcoin",
    velocity: 121,
    sentiment: "Bullish",
    keywords: ["halving", "etf", "whales"],
    description: "Flagship cryptocurrency with strong developer activity.",
    history: Array.from({ length: 30 }, (_, i) => ({
      day: `D${i}`,
      price: 60000 * (1 + Math.random() * 0.1),
      commits: 50,
    })),
  },
  {
    id: "eth",
    name: "Ethereum",
    symbol: "ETH",
    price: 3450,
    change24h: 1.2,
    alphaScore: 79,
    repo: "ethereum/go-ethereum",
    velocity: 98,
    sentiment: "Neutral",
    keywords: ["defi", "rollups", "l2"],
    description: "Programmable money backbone with high L2 activity.",
    history: Array.from({ length: 30 }, (_, i) => ({
      day: `D${i}`,
      price: 3200 * (1 + Math.random() * 0.1),
      commits: 60,
    })),
  },
  {
    id: "nifty",
    name: "NIFTY 50",
    symbol: "NIFTY",
    price: 22500,
    change24h: 0.7,
    alphaScore: 65,
    repo: "indian-stock-market/nifty",
    velocity: 45,
    sentiment: "Bullish",
    keywords: ["india", "large-cap", "index"],
    description: "Benchmark Indian equity index of top 50 companies.",
    history: Array.from({ length: 30 }, (_, i) => ({
      day: `D${i}`,
      price: 22000 * (1 + Math.random() * 0.05),
      commits: 30,
    })),
  },
  {
    id: "sol",
    name: "Solana",
    symbol: "SOL",
    price: 145,
    change24h: -3.1,
    alphaScore: 73,
    repo: "solana-labs/solana",
    velocity: 132,
    sentiment: "Bearish",
    keywords: ["tps", "monolithic", "defi"],
    description: "High-throughput L1 focused on speed and UX.",
    history: Array.from({ length: 30 }, (_, i) => ({
      day: `D${i}`,
      price: 130 * (1 + Math.random() * 0.2),
      commits: 90,
    })),
  },
  {
    id: "binancecoin",
    name: "BNB",
    symbol: "BNB",
    price: 580,
    change24h: 1.5,
    alphaScore: 82,
    repo: "bnb-chain/bsc",
    velocity: 85,
    sentiment: "Bullish",
    keywords: ["exchange", "bsc", "burn"],
    description: "Utility token of the production Binance ecosystem.",
    history: Array.from({ length: 30 }, (_, i) => ({
      day: `D${i}`,
      price: 550 * (1 + Math.random() * 0.1),
      commits: 40,
    })),
  },
  {
    id: "cardano",
    name: "Cardano",
    symbol: "ADA",
    price: 0.45,
    change24h: -0.5,
    alphaScore: 70,
    repo: "input-output-hk/cardano-node",
    velocity: 110,
    sentiment: "Neutral",
    keywords: ["research", "haskell", "staking"],
    description: "Proof-of-stake blockchain platform based on peer-reviewed research.",
    history: Array.from({ length: 30 }, (_, i) => ({
      day: `D${i}`,
      price: 0.4 * (1 + Math.random() * 0.2),
      commits: 75,
    })),
  },
  {
    id: "ripple",
    name: "XRP",
    symbol: "XRP",
    price: 0.62,
    change24h: 3.2,
    alphaScore: 68,
    repo: "ripple/rippled",
    velocity: 55,
    sentiment: "Bullish",
    keywords: ["payments", "banking", "remittance"],
    description: "Digital asset built for global payments.",
    history: Array.from({ length: 30 }, (_, i) => ({
      day: `D${i}`,
      price: 0.55 * (1 + Math.random() * 0.15),
      commits: 35,
    })),
  },
  {
    id: "polkadot",
    name: "Polkadot",
    symbol: "DOT",
    price: 7.20,
    change24h: -1.2,
    alphaScore: 76,
    repo: "paritytech/polkadot",
    velocity: 140,
    sentiment: "Neutral",
    keywords: ["interoperability", "parachains", "substrate"],
    description: "Sharded protocol that enables blockchain networks to operate together.",
    history: Array.from({ length: 30 }, (_, i) => ({
      day: `D${i}`,
      price: 7.0 * (1 + Math.random() * 0.1),
      commits: 100,
    })),
  },
  {
    id: "near",
    name: "Near Protocol",
    symbol: "NEAR",
    price: 6.50,
    change24h: 4.5,
    alphaScore: 81,
    repo: "near/nearcore",
    velocity: 95,
    sentiment: "Bullish",
    keywords: ["sharding", "usability", "account-abstraction"],
    description: "Cloud computing platform designed to host decentralized applications.",
    history: Array.from({ length: 30 }, (_, i) => ({
      day: `D${i}`,
      price: 6.0 * (1 + Math.random() * 0.2),
      commits: 60,
    })),
  },
];

// Generate historical data for charts
const generateHistoricalData = (asset, days = 30) => {
  const data = [];
  const basePrice = asset?.price || 100;
  let price = basePrice;

  for (let i = days; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);

    const change = (Math.random() - 0.5) * (basePrice * 0.05);
    price = Math.max(basePrice * 0.7, Math.min(basePrice * 1.3, price + change));

    const open = price;
    const close = price + (Math.random() - 0.5) * (basePrice * 0.03);
    const high = Math.max(open, close) + Math.random() * (basePrice * 0.02);
    const low = Math.min(open, close) - Math.random() * (basePrice * 0.02);
    const volume = Math.floor(Math.random() * 10000000) + 1000000;

    data.push({
      date: date.toISOString().split('T')[0],
      open: parseFloat(open.toFixed(2)),
      high: parseFloat(high.toFixed(2)),
      low: parseFloat(low.toFixed(2)),
      close: parseFloat(close.toFixed(2)),
      volume,
    });

    price = close;
  }

  return data;
};

/* ------------------------------
   REUSABLE UI
------------------------------ */

// Card, Pill, and Tag components moved to separate files in /ui folder

/* ------------------------------
   PROFILE PANEL
------------------------------ */

// ProfilePanel component moved to /components/ProfilePanel.jsx with React.memo

/* ------------------------------
   PREFERENCES DIALOG
------------------------------ */

// PreferencesDialog component moved to /components/PreferencesDialog.jsx with React.memo

/* ------------------------------
   MAIN APP
------------------------------ */

const App = () => {
  // core app state
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("git_alpha_user"));
    } catch {
      return null;
    }
  });

  const [assets, setAssets] = useState([]);
  const [watchlist, setWatchlist] = useState([]);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [activeTab, setActiveTab] = useState("Dashboard");

  // auth
  const [isLoginView, setIsLoginView] = useState(true);
  const [authData, setAuthData] = useState({
    email: "",
    password: "",
    name: "",
  });
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState("");

  // profile
  const [profileOpen, setProfileOpen] = useState(false);
  const [profileData, setProfileData] = useState(null);
  const [profileLoading, setProfileLoading] = useState(false);
  const [profileError, setProfileError] = useState("");

  // preferences
  const [preferencesOpen, setPreferencesOpen] = useState(false);
  const [preferences, setPreferences] = useState(null);
  const [preferencesLoading, setPreferencesLoading] = useState(false);
  const [preferencesError, setPreferencesError] = useState("");

  // watchlist rule editor
  const [ruleTarget, setRuleTarget] = useState("");
  const [ruleDirection, setRuleDirection] = useState("above");
  const [ruleSaving, setRuleSaving] = useState(false);
  const [ruleSaved, setRuleSaved] = useState(false);

  // live alerts
  const [alerts, setAlerts] = useState([]);
  const wsRef = useRef(null);

  // UI enhancements
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [showFloatingAI, setShowFloatingAI] = useState(false);

  /* ---------- AUTH HANDLER (JWT) ---------- */

  const handleAuth = async (e) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError("");

    try {
      const res = await fetch(`${API_URL}/api/${isLoginView ? "login" : "register"}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(authData),
      });

      let data;
      try {
        data = await res.json();
      } catch {
        data = {};
      }

      if (!res.ok) throw new Error(data.detail || "Authentication failed");

      if (data.user) {
        setUser(data.user);
        localStorage.setItem("git_alpha_user", JSON.stringify(data.user));
      }

      if (data.access_token) {
        localStorage.setItem("git_alpha_token", data.access_token);
      }
    } catch (err) {
      setAuthError(err.message);
    } finally {
      setAuthLoading(false);
    }
  };

  /* ---------- BACKEND DATA LOADING ---------- */

  useEffect(() => {
    if (!user) return;

    const fetchData = async () => {
      try {
        const res = await fetch(`${API_URL}/api/assets`);

        if (!res.ok) {
          throw new Error(`Backend /api/assets error: ${res.status}`);
        }

        const data = await res.json();
        console.log("Loaded assets from backend:", data.length);
        setAssets(data);
        if (!selectedAsset && data.length > 0) {
          setSelectedAsset(data[0]);
        }
      } catch (e) {
        console.error("Switching to Demo Mode Error:", e);
        const mocks = getMockAssets();
        setAssets(mocks);
        if (!selectedAsset && mocks.length > 0) {
          setSelectedAsset(mocks[0]);
        }
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 60000); // Changed from 15000ms (15s) to 60000ms (60s)
    return () => clearInterval(interval);
  }, [user?.id]); // Fixed dependency: only re-run when user.id changes



  useEffect(() => {
    if (user?.id && assets.length > 0) {
      fetch(`${API_URL}/api/watchlist/${user.id}`)
        .then((res) => (res.ok ? res.json() : []))
        .then((ids) => setWatchlist(ids))
        .catch(() => { });
    }
  }, [user, assets]);

  /* ---------- WEBSOCKET ALERTS ---------- */

  // WebSocket disabled - endpoint not implemented in backend
  // Uncomment when WebSocket endpoint is added
  /*
  useEffect(() => {
    if (!user) return;
    if (wsRef.current) return;

    const wsUrl = `${API_URL.replace("http", "ws")}/ws`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connected successfully");
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "ALERT") {
          setAlerts((prev) => [data, ...prev].slice(0, 5));
        } else if (data.type === "CONNECTION") {
          console.log("WebSocket:", data.message);
        }
      } catch {
        // ignore parse errors
      }
    };

    ws.onerror = (error) => {
      console.warn("WebSocket error (non-critical):", error);
    };

    ws.onclose = () => {
      console.log("WebSocket closed");
      wsRef.current = null;
    };

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [user]);
  */


  useEffect(() => {
    if (preferences?.default_tab) {
      setActiveTab(preferences.default_tab);
    }
  }, [preferences?.default_tab]);

  /* ---------- OAUTH CALLBACK HANDLER ---------- */

  useEffect(() => {
    // Handle OAuth callback
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');
    const provider = params.get('provider');

    if (token && window.location.search.includes('token=')) {
      // Store token
      localStorage.setItem('git_alpha_token', token);

      // Fetch user data
      fetch(`${API_URL}/api/me`, {
        headers: { Authorization: `Bearer ${token}` }
      })
        .then(res => res.json())
        .then(userData => {
          setUser(userData);
          localStorage.setItem('git_alpha_user', JSON.stringify(userData));
          // Clear URL params and redirect to home
          window.history.replaceState({}, '', '/');
        })
        .catch(err => {
          console.error('OAuth login error:', err);
          setAuthError('OAuth login failed. Please try again.');
        });
    }
  }, []);

  /* ---------- PROFILE / PREFERENCES API ---------- */

  const fetchProfile = async () => {
    setProfileLoading(true);
    setProfileError("");
    try {
      const res = await fetch(`${API_URL}/api/profile`, {
        headers: {
          "Content-Type": "application/json",
          ...getAuthHeaders(),
        },
      });
      let data;
      try {
        data = await res.json();
      } catch {
        data = {};
      }
      if (!res.ok) {
        throw new Error(data.detail || "Failed to load profile");
      }
      setProfileData(data);
    } catch (e) {
      setProfileError(e.message);
    } finally {
      setProfileLoading(false);
    }
  };

  const fetchPreferences = async () => {
    setPreferencesLoading(true);
    setPreferencesError("");
    try {
      const res = await fetch(`${API_URL}/api/preferences`, {
        headers: {
          "Content-Type": "application/json",
          ...getAuthHeaders(),
        },
      });
      let data;
      try {
        data = await res.json();
      } catch {
        data = {};
      }
      if (!res.ok) {
        throw new Error(data.detail || "Failed to load preferences");
      }
      setPreferences(data);
    } catch (e) {
      setPreferencesError(e.message);
    } finally {
      setPreferencesLoading(false);
    }
  };

  const savePreferences = async (next) => {
    setPreferencesLoading(true);
    setPreferencesError("");
    try {
      const res = await fetch(`${API_URL}/api/preferences`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          ...getAuthHeaders(),
        },
        body: JSON.stringify(next),
      });
      let data;
      try {
        data = await res.json();
      } catch {
        data = {};
      }
      if (!res.ok) {
        throw new Error(data.detail || "Failed to save preferences");
      }
      setPreferences(data);
    } catch (e) {
      setPreferencesError(e.message);
    } finally {
      setPreferencesLoading(false);
    }
  };

  /* ---------- WATCHLIST ---------- */

  const toggleWatchlist = useCallback(async (assetId, e) => {
    if (e) e.stopPropagation();
    if (!user) return;

    const isWatching = watchlist.includes(assetId);
    setWatchlist(
      isWatching ? watchlist.filter((id) => id !== assetId) : [...watchlist, assetId]
    );

    if (!isWatching) {
      fetch(`${API_URL}/api/watchlist`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: user.id,
          asset_id: assetId,
          target_price: null,
          direction: null,
        }),
      }).catch(() => { });
    }
  }, [user, watchlist]);

  const saveWatchlistRule = async () => {
    if (!user || !selectedAsset) return;
    setRuleSaving(true);
    setRuleSaved(false);
    try {
      const res = await fetch(`${API_URL}/api/watchlist`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: user.id,
          asset_id: selectedAsset.id,
          target_price: ruleTarget ? Number(ruleTarget) : null,
          direction: ruleDirection || null,
        }),
      });
      if (res.ok) {
        setRuleSaved(true);
        setTimeout(() => setRuleSaved(false), 2000);
      }
    } catch (e) {
      console.error("Failed to save rule", e);
    } finally {
      setRuleSaving(false);
    }
  };

  /* ---------- LOGOUT ---------- */

  const handleLogout = () => {
    setUser(null);
    setAssets([]);
    setWatchlist([]);
    setSelectedAsset(null);
    setAlerts([]);
    try {
      localStorage.removeItem("git_alpha_user");
      localStorage.removeItem("git_alpha_token");
    } catch {
      // ignore
    }
  };

  /* ---------- AUTH CHECK / LOGIN SCREEN ---------- */

  if (!user) {
    return (
      <div className="min-h-screen bg-[#020410] text-slate-100 flex items-center justify-center">
        <div className="w-full max-w-md px-4">
          <Card className="p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center border border-indigo-400/40">
                <Cpu className="text-indigo-400" size={20} />
              </div>
              <div>
                <div className="text-xs text-slate-400">AI Market Engine</div>
                <div className="text-sm font-semibold tracking-tight">
                  Git Alpha
                </div>
              </div>
            </div>

            <p className="text-xs text-slate-400 mb-4">
              Login or register to access your AI-powered market dashboard.
            </p>

            <form onSubmit={handleAuth} className="space-y-3 text-sm">
              {/* OAuth Buttons */}
              <div className="space-y-2">
                <OAuthButton
                  provider="google"
                  icon={GoogleIcon}
                  onClick={() => window.location.href = `${API_URL}/api/auth/oauth/google`}
                />

                <OAuthButton
                  provider="github"
                  icon={GitHubIcon}
                  onClick={() => window.location.href = `${API_URL}/api/auth/oauth/github`}
                />
              </div>

              {/* Divider */}
              <div className="flex items-center gap-3 my-4">
                <div className="flex-1 border-t border-slate-700"></div>
                <span className="text-slate-400 text-xs">or continue with email</span>
                <div className="flex-1 border-t border-slate-700"></div>
              </div>

              {!isLoginView && (
                <div>
                  <label className="block text-xs text-slate-300 mb-1">
                    Name
                  </label>
                  <input
                    type="text"
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    value={authData.name}
                    onChange={(e) =>
                      setAuthData((d) => ({ ...d, name: e.target.value }))
                    }
                    required={!isLoginView}
                  />
                </div>
              )}

              <div>
                <label className="block text-xs text-slate-300 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  value={authData.email}
                  onChange={(e) =>
                    setAuthData((d) => ({ ...d, email: e.target.value }))
                  }
                  required
                />
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">
                  Password
                </label>
                <input
                  type="password"
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  value={authData.password}
                  onChange={(e) =>
                    setAuthData((d) => ({ ...d, password: e.target.value }))
                  }
                  required
                />
              </div>

              {authError && (
                <div className="text-xs text-red-400">{authError}</div>
              )}

              <button
                type="submit"
                disabled={authLoading}
                className="w-full mt-2 flex items-center justify-center gap-2 bg-[image:var(--gradient-primary)] hover:shadow-[var(--shadow-glow)] text-white text-xs font-semibold py-2 rounded-lg transition-all disabled:bg-slate-700 disabled:opacity-50"
              >
                {authLoading ? (
                  <>
                    <Loader2 className="animate-spin" size={14} /> Please wait
                  </>
                ) : (
                  <>
                    {isLoginView ? <Lock size={14} /> : <User size={14} />}
                    {isLoginView ? "Login" : "Create account"}
                  </>
                )}
              </button>
            </form>

            <button
              onClick={() => setIsLoginView((v) => !v)}
              className="mt-4 w-full text-[11px] text-slate-300 hover:text-indigo-300 flex items-center justify-center gap-2"
            >
              {isLoginView
                ? "New here? Create an account"
                : "Already have an account? Login"}
            </button>
          </Card>
        </div>
      </div>
    );
  }

  /* ---------- MAIN APP LAYOUT ---------- */

  const filteredAssets =
    activeTab === "Watchlist"
      ? assets.filter((a) => watchlist.includes(a.id))
      : assets;



  return (
    <div className="min-h-screen bg-[#020410] text-slate-100 flex overflow-x-hidden max-w-full">
      {/* Collapsible Sidebar */}
      <CollapsibleSidebar
        isCollapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        className="hidden md:flex"
      >
        {({ isCollapsed }) => (
          <>
            {/* Logo/Header */}
            <div className="px-4 py-4 flex items-center gap-2 border-b border-slate-800/80">
              <div className="w-8 h-8 rounded-xl bg-indigo-500/10 flex items-center justify-center border border-indigo-400/40">
                <Cpu className="text-indigo-400" size={18} />
              </div>
              {!isCollapsed && (
                <div>
                  <div className="text-xs text-slate-400">AI Market Engine</div>
                  <div className="text-sm font-semibold tracking-tight">
                    Git Alpha
                  </div>
                </div>
              )}
            </div>

            {/* Navigation Buttons */}
            <div className="flex-1 px-3 py-4 space-y-1 text-xs">
              <button
                onClick={() => setActiveTab("Dashboard")}
                className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-all ${activeTab === "Dashboard"
                  ? "bg-[image:var(--gradient-primary)] text-white shadow-[var(--shadow-glow)]"
                  : "hover:bg-[var(--color-purple)]/10 text-slate-300 hover:text-[var(--color-purple-light)]"
                  }`}
                title="Dashboard"
              >
                <TrendingUp size={14} />
                {!isCollapsed && <span>Dashboard</span>}
              </button>
              <button
                onClick={() => setActiveTab("Signals")}
                className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-all ${activeTab === "Signals"
                  ? "bg-[image:var(--gradient-primary)] text-white shadow-[var(--shadow-glow)]"
                  : "hover:bg-[var(--color-cyan)]/10 text-slate-300 hover:text-[var(--color-cyan-light)]"
                  }`}
                title="Signals"
              >
                <Radio size={14} />
                {!isCollapsed && <span>Signals</span>}
              </button>
              <button
                onClick={() => setActiveTab("Watchlist")}
                className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-all ${activeTab === "Watchlist"
                  ? "bg-[image:var(--gradient-primary)] text-white shadow-[var(--shadow-glow)]"
                  : "hover:bg-[var(--color-emerald)]/10 text-slate-300 hover:text-[var(--color-emerald-light)]"
                  }`}
                title="Watchlist"
              >
                <Heart size={14} />
                {!isCollapsed && <span>Watchlist</span>}
              </button>
              <button
                onClick={() => setActiveTab("Portfolio")}
                className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-all ${activeTab === "Portfolio"
                  ? "bg-[image:var(--gradient-primary)] text-white shadow-[var(--shadow-glow)]"
                  : "hover:bg-[var(--color-gold)]/10 text-slate-300 hover:text-[var(--color-gold-light)]"
                  }`}
                title="Portfolio"
              >
                <Wallet size={14} />
                {!isCollapsed && <span>Portfolio</span>}
              </button>
              <button
                onClick={() => setActiveTab("Markets")}
                className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-all ${activeTab === "Markets"
                  ? "bg-[image:var(--gradient-primary)] text-white shadow-[var(--shadow-glow)]"
                  : "hover:bg-[var(--color-cyan)]/10 text-slate-300 hover:text-[var(--color-cyan-light)]"
                  }`}
                title="Markets"
              >
                <Globe size={14} />
                {!isCollapsed && <span>Markets</span>}
              </button>

              <button
                onClick={() => setActiveTab("Charts")}
                className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-all ${activeTab === "Charts"
                  ? "bg-[image:var(--gradient-primary)] text-white shadow-[var(--shadow-glow)]"
                  : "hover:bg-[var(--color-cyan)]/10 text-slate-300 hover:text-[var(--color-cyan-light)]"
                  }`}
                title="Charts"
              >
                <BarChart3 size={14} />
                {!isCollapsed && <span>Charts</span>}
              </button>

              <button
                onClick={() => setActiveTab("News")}
                className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-all ${activeTab === "News"
                  ? "bg-[image:var(--gradient-primary)] text-white shadow-[var(--shadow-glow)]"
                  : "hover:bg-[var(--color-cyan)]/10 text-slate-300 hover:text-[var(--color-cyan-light)]"
                  }`}
                title="News Hub"
              >
                <Newspaper size={14} />
                {!isCollapsed && <span>News Hub</span>}
              </button>
            </div>

            {/* Bottom Buttons */}
            {!isCollapsed && (
              <>
                <button
                  onClick={() => {
                    setProfileOpen(true);
                    fetchProfile();
                  }}
                  className="w-full flex items-center justify-between px-3 py-1.5 rounded-lg bg-[var(--color-purple)]/10 hover:bg-[var(--color-purple)]/20 border border-[var(--color-purple)]/30 hover:border-[var(--color-purple)]/50 transition-all"
                >
                  <span className="flex items-center gap-2">
                    <User size={12} /> Profile
                  </span>
                  <ChevronRight size={12} />
                </button>
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center justify-center gap-2 px-3 py-1.5 rounded-lg bg-[var(--color-rose)]/10 text-[var(--color-rose-light)] hover:bg-[var(--color-rose)]/20 border border-[var(--color-rose)]/40 hover:border-[var(--color-rose)]/60 transition-all"
                >
                  <LogOut size={12} /> Logout
                </button>
              </>
            )}
            {isCollapsed && (
              <>
                <button
                  onClick={() => {
                    setProfileOpen(true);
                    fetchProfile();
                  }}
                  className="w-full flex items-center justify-center p-3 rounded-lg bg-[var(--color-purple)]/10 hover:bg-[var(--color-purple)]/20 border border-[var(--color-purple)]/30 hover:border-[var(--color-purple)]/50 transition-all"
                  title="Profile"
                >
                  <User size={14} />
                </button>
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center justify-center p-3 rounded-lg bg-[var(--color-rose)]/10 text-[var(--color-rose-light)] hover:bg-[var(--color-rose)]/20 border border-[var(--color-rose)]/40 hover:border-[var(--color-rose)]/60 transition-all"
                  title="Logout"
                >
                  <LogOut size={14} />
                </button>
              </>
            )}
          </>
        )}
      </CollapsibleSidebar>

      {/* Main content */}
      <div
        className="flex-1 flex flex-col transition-all duration-300"
        style={{
          marginLeft: sidebarCollapsed ? '64px' : '240px'
        }}
      >
        {/* Top bar */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800/70 bg-[#050816]/90 backdrop-blur">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <Pill variant="success">
              <Shield size={12} /> Authenticated
            </Pill>
          </div>

          {/* Theme Toggle */}
          <div className="flex items-center gap-3">
            <ThemeToggle />
          </div>
        </div>

        {/* Main content grid */}
        <div className="flex-1 overflow-y-auto overflow-x-hidden p-4 max-w-full">
          {/* Portfolio Tab */}
          {activeTab === "Portfolio" && (
            <Portfolio user={user} />
          )}

          {/* Markets Tab */}
          {activeTab === "Markets" && (
            <MarketDashboard />
          )}



          {/* Charts Tab */}
          {activeTab === "Charts" && (
            <ChartsView
              assets={filteredAssets}
              selectedAsset={selectedAsset}
              onAssetSelect={(asset) => setSelectedAsset(asset)}
            />
          )}

          {/* News Hub Tab */}
          {activeTab === "News" && (
            <NewsHub user={user} />
          )}

          {/* Dashboard, Signals, and Watchlist Tabs */}
          {(activeTab === "Dashboard" || activeTab === "Signals" || activeTab === "Watchlist") && (
            <div className="grid lg:grid-cols-2 gap-4 max-w-full overflow-hidden w-full">
              {/* Left: asset cards */}
              <Card className="p-4">
                <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-2 text-xs">
                  {filteredAssets.map((asset) => {
                    const isWatching = watchlist.includes(asset.id);
                    const isSelected = selectedAsset?.id === asset.id;
                    return (
                      <div
                        key={asset.id}
                        onClick={() => setSelectedAsset(asset)}
                        className={`text-left rounded-xl px-3 py-2 border text-xs transition-all cursor-pointer overflow-hidden ${isSelected
                          ? "border-indigo-500/70 bg-indigo-500/10"
                          : "border-slate-800/80 bg-slate-900/60 hover:bg-slate-900"
                          }`}
                      >
                        <div className="flex justify-between items-center mb-1">
                          <div className="flex-1 min-w-0 pr-2">
                            <div className="flex items-center gap-1">
                              <span className="font-semibold text-[11px] truncate">
                                {asset.name}
                              </span>
                              <span className="text-[10px] text-slate-400 flex-shrink-0">
                                {asset.symbol}
                              </span>
                            </div>
                            <div className="text-[10px] text-slate-400 flex items-center gap-1 truncate">
                              <GitCommit size={10} className="flex-shrink-0" />
                              <span className="truncate">{asset.repo}</span>
                            </div>
                          </div>
                          <button
                            onClick={(e) => toggleWatchlist(asset.id, e)}
                            className={`p-1 rounded-full border transition-all flex-shrink-0 ${isWatching
                              ? "border-[var(--color-emerald)]/70 bg-[var(--color-emerald)]/10 hover-glow-emerald"
                              : "border-slate-700/70 hover:bg-[var(--color-purple)]/10 hover:border-[var(--color-purple)]/30"
                              }`}
                          >
                            <Heart
                              size={11}
                              className={isWatching ? "fill-[var(--color-emerald-light)] text-[var(--color-emerald-light)]" : ""}
                            />
                          </button>
                        </div>

                        <div className="flex items-end justify-between">
                          <div className="flex-1 min-w-0 pr-2">
                            <div className="text-[11px] font-mono truncate">
                              {formatCurrency(asset.price, asset.symbol)}
                            </div>
                            <div
                              className={`text-[10px] flex items-center gap-1 font-semibold ${asset.change24h >= 0
                                ? "text-gain"
                                : "text-loss"
                                }`}
                            >
                              {asset.change24h >= 0 ? (
                                <ArrowUpRight size={10} className="flex-shrink-0" />
                              ) : (
                                <ArrowDownRight size={10} className="flex-shrink-0" />
                              )}
                              <span className="truncate">{asset.change24h}%</span>
                            </div>
                          </div>
                          <div className="text-right text-[10px] flex-shrink-0">
                            <div className="text-slate-400">Alpha Score</div>
                            <div className="font-semibold text-gradient-primary">
                              {asset.alphaScore}
                            </div>
                            <div className="text-slate-500 truncate">
                              v{asset.velocity} commits
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </Card>

              {/* Right: selected asset + alerts */}
              <div className="space-y-4">
                <Card className="p-4">
                  {selectedAsset ? (
                    <>
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-semibold">
                              {selectedAsset.name}
                            </span>
                            <span className="text-xs text-slate-400">
                              {selectedAsset.symbol}
                            </span>
                          </div>
                          <div className="text-[11px] text-slate-400 flex items-center gap-1">
                            <Code size={11} /> {selectedAsset.repo}
                          </div>
                        </div>
                        <div className="text-right text-xs">
                          <div className="font-mono">
                            {formatCurrency(
                              selectedAsset.price,
                              selectedAsset.symbol
                            )}
                          </div>
                          <div
                            className={`flex items-center justify-end gap-1 text-[10px] ${selectedAsset.change24h >= 0
                              ? "text-emerald-400"
                              : "text-red-400"
                              }`}
                          >
                            {selectedAsset.change24h >= 0 ? (
                              <ArrowUpRight size={10} />
                            ) : (
                              <ArrowDownRight size={10} />
                            )}
                            {selectedAsset.change24h}%
                          </div>
                        </div>
                      </div>

                      <div className="flex flex-wrap gap-1 mb-3">
                        <Tag>Sentiment: {selectedAsset.sentiment}</Tag>
                        <Tag>Alpha: {selectedAsset.alphaScore}</Tag>
                        <Tag>Velocity: {selectedAsset.velocity}</Tag>
                        {selectedAsset.keywords?.slice(0, 3).map((k) => (
                          <Tag key={k}>{k}</Tag>
                        ))}
                      </div>

                      <p className="text-[11px] text-slate-300 mb-3">
                        {selectedAsset.description}
                      </p>

                      {/* Watchlist alert rule editor */}
                      <div className="mt-4 p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-semibold text-slate-300 flex items-center gap-1">
                            <Bell size={14} /> Alert Rule
                          </span>
                        </div>

                        <div className="grid grid-cols-2 gap-2 mb-2">
                          <input
                            type="number"
                            value={ruleTarget}
                            onChange={(e) => setRuleTarget(e.target.value)}
                            placeholder="Target price"
                            className="text-xs px-2 py-1.5 rounded-lg bg-slate-950 border border-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                          />
                          <select
                            value={ruleDirection}
                            onChange={(e) => setRuleDirection(e.target.value)}
                            className="text-xs px-2 py-1.5 rounded-lg bg-slate-950 border border-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                          >
                            <option value="above">Alert when above</option>
                            <option value="below">Alert when below</option>
                          </select>
                        </div>

                        <button
                          onClick={saveWatchlistRule}
                          disabled={
                            ruleSaving || !watchlist.includes(selectedAsset.id)
                          }
                          className="w-full text-[11px] px-3 py-1.5 rounded-lg bg-indigo-500 hover:bg-indigo-600 disabled:bg-slate-700 flex items-center justify-center gap-1"
                        >
                          {ruleSaving ? (
                            <>
                              <Loader2 className="animate-spin" size={12} /> Saving...
                            </>
                          ) : (
                            <>
                              <CheckCircle size={12} /> Save alert rule
                            </>
                          )}
                        </button>
                        {!watchlist.includes(selectedAsset.id) && (
                          <p className="mt-1 text-[10px] text-slate-400">
                            Add to watchlist first to attach an alert.
                          </p>
                        )}
                        {ruleSaved && (
                          <p className="mt-1 text-[10px] text-emerald-400 flex items-center gap-1">
                            <CheckCircle size={10} /> Alert rule saved
                          </p>
                        )}
                      </div>
                    </>
                  ) : (
                    <div className="text-xs text-slate-400">
                      Select an asset from the left to see details.
                    </div>
                  )}
                </Card>

                {/* Alerts list */}
                <Card className="p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Bell size={14} className="text-indigo-400" />
                    <span className="text-xs font-semibold">Live Alerts</span>
                  </div>
                  {alerts.length > 0 ? (
                    <div className="space-y-2">
                      {alerts.map((alert, i) => (
                        <div key={i} className="p-2 rounded-lg bg-slate-900/60 border border-slate-800">
                          <div className="flex items-center justify-between mb-1">
                            <div className="flex items-center gap-2">
                              <AlertCircle
                                size={12}
                                className={
                                  alert.sentiment === "positive"
                                    ? "text-emerald-400"
                                    : alert.sentiment === "negative"
                                      ? "text-red-400"
                                      : "text-slate-400"
                                }
                              />
                              <span className="font-medium text-[11px]">
                                {alert.title}
                              </span>
                            </div>
                          </div>
                          <div className="text-[11px] text-slate-300">
                            {alert.message}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-xs text-slate-400">
                      No alerts yet. Watchlist rules will trigger alerts here.
                    </div>
                  )}
                </Card>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Portals */}
      <ProfilePanel
        open={profileOpen}
        onClose={() => setProfileOpen(false)}
        profile={profileData}
        loading={profileLoading}
        error={profileError}
        onRefresh={fetchProfile}
      />

      <PreferencesDialog
        open={preferencesOpen}
        onClose={() => setPreferencesOpen(false)}
        value={preferences}
        loading={preferencesLoading}
        error={preferencesError}
        onChange={savePreferences}
      />

      {/* Floating AI Widget with Toggle */}
      {showFloatingAI ? (
        <FloatingAIWidget onClose={() => setShowFloatingAI(false)}>
          <AIAssistant />
        </FloatingAIWidget>
      ) : (
        <button
          onClick={() => setShowFloatingAI(true)}
          className="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-gradient-to-br from-purple-600 to-cyan-600 hover:from-purple-500 hover:to-cyan-500 flex items-center justify-center text-white shadow-2xl hover:shadow-purple-500/50 transition-all hover:scale-110 z-[9999] group"
          title="Open AI Assistant"
        >
          <Bot size={24} className="group-hover:scale-110 transition-transform" />
          <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-slate-900 animate-pulse" />
        </button>
      )}
    </div>
  );
};

export default App;
