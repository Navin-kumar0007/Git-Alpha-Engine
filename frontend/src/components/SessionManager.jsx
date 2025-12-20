import React, { useState, useEffect } from 'react';
import { Monitor, X, AlertCircle, Trash2, LogOut } from 'lucide-react';

/**
 * Session Manager Component
 * Display and manage active user sessions
 */
const SessionManager = ({ user }) => {
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const fetchSessions = async () => {
        setLoading(true);
        setError('');
        try {
            const token = localStorage.getItem('git_alpha_token');
            const res = await fetch('http://127.0.0.1:8000/api/auth/sessions', {
                headers: { Authorization: `Bearer ${token}` }
            });

            if (res.ok) {
                const data = await res.json();
                setSessions(data.sessions || []);
            } else {
                setError('Failed to load sessions');
            }
        } catch (err) {
            setError('Network error');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (user) {
            fetchSessions();
        }
    }, [user]);

    const revokeSession = async (sessionId) => {
        try {
            const token = localStorage.getItem('git_alpha_token');
            const res = await fetch(`http://127.0.0.1:8000/api/auth/sessions/${sessionId}`, {
                method: 'DELETE',
                headers: { Authorization: `Bearer ${token}` }
            });

            if (res.ok) {
                fetchSessions(); // Refresh list
            } else {
                setError('Failed to revoke session');
            }
        } catch (err) {
            setError('Network error');
        }
    };

    const revokeAllOthers = async () => {
        if (!confirm('Sign out all other devices? This cannot be undone.')) return;

        try {
            const token = localStorage.getItem('git_alpha_token');
            const res = await fetch('http://127.0.0.1:8000/api/auth/sessions/all', {
                method: 'DELETE',
                headers: { Authorization: `Bearer ${token}` }
            });

            if (res.ok) {
                fetchSessions(); // Refresh list
            } else {
                setError('Failed to revoke sessions');
            }
        } catch (err) {
            setError('Network error');
        }
    };

    const formatDate = (dateStr) => {
        const date = new Date(dateStr);
        const now = new Date();
        const diff = Math.floor((now - date) / 1000); // seconds

        if (diff < 60) return 'Just now';
        if (diff < 3600) return `${Math.floor(diff / 60)} minutes ago`;
        if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`;
        return `${Math.floor(diff / 86400)} days ago`;
    };

    const parseDeviceInfo = (userAgent) => {
        if (!userAgent) return { browser: 'Unknown', os: 'Unknown', device: 'Desktop' };

        // Simple parsing (could be improved with a library)
        let browser = 'Unknown';
        if (userAgent.includes('Chrome')) browser = 'Chrome';
        else if (userAgent.includes('Firefox')) browser = 'Firefox';
        else if (userAgent.includes('Safari')) browser = 'Safari';
        else if (userAgent.includes('Edge')) browser = 'Edge';

        let os = 'Unknown';
        if (userAgent.includes('Windows')) os = 'Windows';
        else if (userAgent.includes('Mac')) os = 'macOS';
        else if (userAgent.includes('Linux')) os = 'Linux';
        else if (userAgent.includes('Android')) os = 'Android';
        else if (userAgent.includes('iOS')) os = 'iOS';

        let device = 'Desktop';
        if (userAgent.includes('Mobile')) device = 'Mobile';
        else if (userAgent.includes('Tablet')) device = 'Tablet';

        return { browser, os, device };
    };

    if (loading) {
        return (
            <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-400 mx-auto" />
                <p className="text-slate-400 mt-4 text-sm">Loading sessions...</p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Active Sessions</h3>
                {sessions.length > 1 && (
                    <button
                        onClick={revokeAllOthers}
                        className="text-sm text-red-400 hover:text-red-300 transition-colors flex items-center gap-1"
                    >
                        <LogOut size={16} />
                        Sign out all other devices
                    </button>
                )}
            </div>

            {error && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 flex items-start gap-2">
                    <AlertCircle size={18} className="text-red-400 flex-shrink-0 mt-0.5" />
                    <span className="text-sm text-red-300">{error}</span>
                </div>
            )}

            {/* Sessions List */}
            <div className="space-y-3">
                {sessions.length === 0 ? (
                    <p className="text-slate-400 text-sm text-center py-8">No active sessions</p>
                ) : (
                    sessions.map((session) => {
                        const deviceInfo = parseDeviceInfo(session.device_info);

                        return (
                            <div
                                key={session.id}
                                className={`glass-card ${session.is_current ? 'border-2 border-purple-500' : ''}`}
                            >
                                <div className="flex items-start gap-3">
                                    <Monitor
                                        className={session.is_current ? 'text-purple-400' : 'text-slate-400'}
                                        size={24}
                                    />

                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2 mb-1">
                                            <h4 className="font-semibold text-sm">
                                                {deviceInfo.browser} on {deviceInfo.os}
                                            </h4>
                                            {session.is_current && (
                                                <span className="px-2 py-0.5 bg-purple-500/20 text-purple-300 text-xs rounded-full">
                                                    Current
                                                </span>
                                            )}
                                        </div>

                                        <div className="text-xs text-slate-400 space-y-0.5">
                                            <div>IP: {session.ip_address || 'Unknown'}</div>
                                            <div>Last active: {formatDate(session.last_active)}</div>
                                            <div>Signed in: {formatDate(session.created_at)}</div>
                                        </div>
                                    </div>

                                    {!session.is_current && (
                                        <button
                                            onClick={() => revokeSession(session.id)}
                                            className="p-2 hover:bg-red-500/10 rounded-lg transition-colors text-slate-400 hover:text-red-400"
                                            title="Revoke this session"
                                        >
                                            <Trash2 size={18} />
                                        </button>
                                    )}
                                </div>
                            </div>
                        );
                    })
                )}
            </div>
        </div>
    );
};

export default SessionManager;
