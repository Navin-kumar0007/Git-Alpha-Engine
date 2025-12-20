import React, { useState } from 'react';
import { Shield, X, AlertCircle } from 'lucide-react';

/**
 * Two-Factor Verification Component
 * For login 2FA code entry
 */
const TwoFactorVerify = ({ email, password, rememberMe, onSuccess, onCancel }) => {
    const [code, setCode] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const res = await fetch('http://127.0.0.1:8000/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email,
                    password,
                    remember_me: rememberMe,
                    totp_code: code
                })
            });

            const data = await res.json();

            if (res.ok && data.access_token) {
                localStorage.setItem('git_alpha_token', data.access_token);
                onSuccess?.(data.user);
            } else {
                setError(data.detail || 'Invalid 2FA code');
            }
        } catch (err) {
            setError('Network error');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="glass-card max-w-sm w-full animate-scale-up">
                {/* Header */}
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                        <Shield className="text-purple-400" size={24} />
                        <h2 className="text-xl font-semibold">Two-Factor Authentication</h2>
                    </div>
                    <button
                        onClick={onCancel}
                        className="text-slate-400 hover:text-white transition-colors"
                    >
                        <X size={24} />
                    </button>
                </div>

                {error && (
                    <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 mb-4 flex items-start gap-2">
                        <AlertCircle size={18} className="text-red-400 flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-red-300">{error}</span>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <p className="text-slate-300 text-sm">
                        Enter the 6-digit code from your authenticator app
                    </p>

                    <div>
                        <label className="block text-sm text-slate-300 mb-2">Verification Code</label>
                        <input
                            type="text"
                            value={code}
                            onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                            placeholder="000000"
                            className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-3 text-white text-center text-2xl font-mono tracking-widest focus:outline-none focus:border-purple-500"
                            maxLength={6}
                            autoFocus
                            required
                        />
                    </div>

                    <div className="text-xs text-slate-400">
                        <p>Don't have access to your device?</p>
                        <button
                            type="button"
                            className="text-purple-400 hover:text-purple-300 transition-colors"
                        >
                            Use a backup code
                        </button>
                    </div>

                    <div className="flex gap-3">
                        <button
                            type="button"
                            onClick={onCancel}
                            className="flex-1 btn btn-ghost"
                            disabled={loading}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="flex-1 btn btn-primary"
                            disabled={loading || code.length !== 6}
                        >
                            {loading ? 'Verifying...' : 'Verify'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default TwoFactorVerify;
