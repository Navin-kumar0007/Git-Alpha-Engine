import React, { useState, useEffect } from "react";
import { Settings, X, Loader2 } from "lucide-react";

const PreferencesDialog = ({
    open,
    onClose,
    value,
    loading,
    error,
    onChange,
}) => {
    const [local, setLocal] = useState(
        value || {
            theme: "system",
            default_tab: "Dashboard",
            risk_profile: "balanced",
        }
    );

    useEffect(() => {
        if (value) setLocal(value);
    }, [value?.theme, value?.default_tab, value?.risk_profile]);

    const updateField = (key, val) => {
        const next = { ...local, [key]: val };
        setLocal(next);
        onChange(next);
    };

    if (!open) return null;

    return (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-40">
            <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-md p-6 shadow-xl text-sm">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-lg font-semibold flex items-center gap-2">
                        <Settings size={18} /> Preferences
                    </h2>
                    <button onClick={onClose} className="p-1 rounded hover:bg-slate-800">
                        <X size={16} />
                    </button>
                </div>

                {error && (
                    <div className="text-xs text-red-400 mb-2">{error}</div>
                )}

                <div className="space-y-4">
                    <div>
                        <div className="text-slate-400 mb-1">Theme</div>
                        <select
                            value={local.theme}
                            onChange={(e) => updateField("theme", e.target.value)}
                            className="w-full bg-slate-800 border border-[var(--color-purple)]/30 rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:border-[var(--color-purple)] focus:ring-1 focus:ring-[var(--color-purple)]/50 transition-all"
                        >
                            <option value="system">System</option>
                            <option value="light">Light</option>
                            <option value="dark">Dark</option>
                        </select>
                    </div>

                    <div>
                        <div className="text-slate-400 mb-1">Default Tab</div>
                        <select
                            value={local.default_tab}
                            onChange={(e) => updateField("default_tab", e.target.value)}
                            className="w-full bg-slate-800 border border-[var(--color-cyan)]/30 rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:border-[var(--color-cyan)] focus:ring-1 focus:ring-[var(--color-cyan)]/50 transition-all"
                        >
                            <option value="Dashboard">Dashboard</option>
                            <option value="Signals">Signals</option>
                            <option value="Watchlist">Watchlist</option>
                        </select>
                    </div>

                    <div>
                        <div className="text-slate-400 mb-1">Risk Profile</div>
                        <select
                            value={local.risk_profile}
                            onChange={(e) => updateField("risk_profile", e.target.value)}
                            className="w-full bg-slate-800 border border-[var(--color-gold)]/30 rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:border-[var(--color-gold)] focus:ring-1 focus:ring-[var(--color-gold)]/50 transition-all"
                        >
                            <option value="conservative">Conservative</option>
                            <option value="balanced">Balanced</option>
                            <option value="aggressive">Aggressive</option>
                        </select>
                    </div>
                </div>

                <div className="flex justify-end gap-2 mt-6">
                    <button
                        onClick={onClose}
                        className="px-3 py-1.5 text-xs rounded-lg border border-slate-600 hover:bg-slate-800"
                    >
                        Close
                    </button>
                    {loading && (
                        <div className="flex items-center gap-1 text-xs text-slate-300">
                            <Loader2 className="animate-spin" size={14} /> Saving...
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

// Wrap with React.memo for performance optimization
export default React.memo(PreferencesDialog);
