import React from "react";
import { User, X, RefreshCw, Loader2 } from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const ProfilePanel = ({ open, onClose, profile, loading, error, onRefresh }) => {
    if (!open) return null;
    return (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-40">
            <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-md p-6 shadow-xl">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-lg font-semibold flex items-center gap-2">
                        <User size={18} /> Profile
                    </h2>
                    <button onClick={onClose} className="p-1 rounded hover:bg-slate-800">
                        <X size={16} />
                    </button>
                </div>

                {loading && (
                    <div className="flex items-center gap-2 text-sm text-slate-300">
                        <Loader2 className="animate-spin" size={16} /> Loading profile...
                    </div>
                )}

                {error && !loading && (
                    <div className="text-sm text-red-400 mb-3">{error}</div>
                )}

                {profile && !loading && (
                    <div className="space-y-3 text-sm">
                        <div>
                            <span className="text-slate-400">Name: </span>
                            <span className="font-medium">{profile.name}</span>
                        </div>
                        <div>
                            <span className="text-slate-400">Email: </span>
                            <span className="font-mono text-xs">{profile.email}</span>
                        </div>
                        <div>
                            <span className="text-slate-400">Joined: </span>
                            <span>
                                {profile.created_at
                                    ? new Date(profile.created_at).toLocaleString()
                                    : "—"}
                            </span>
                        </div>
                        {profile.avatar_url && (
                            <div className="mt-3">
                                <span className="text-slate-400 block mb-1">Avatar:</span>
                                <img
                                    src={`${API_URL}${profile.avatar_url}`}
                                    alt="Avatar"
                                    className="w-16 h-16 rounded-full border border-slate-700"
                                />
                            </div>
                        )}
                    </div>
                )}

                <div className="flex justify-end gap-2 mt-6">
                    <button
                        onClick={onRefresh}
                        className="px-3 py-1.5 text-xs rounded-lg border border-[var(--color-cyan)]/40 hover:bg-[var(--color-cyan)]/10 hover-glow-cyan text-[var(--color-cyan-light)] flex items-center gap-1 transition-all"
                    >
                        <RefreshCw size={12} /> Refresh
                    </button>
                    <button
                        onClick={onClose}
                        className="px-3 py-1.5 text-xs rounded-lg bg-[image:var(--gradient-primary)] hover:shadow-[var(--shadow-glow)] text-white transition-all"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
};

// Wrap with React.memo for performance optimization
export default React.memo(ProfilePanel);
