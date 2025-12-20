import React, { useState } from 'react';
import { Shield, Copy, Check, X, AlertCircle } from 'lucide-react';

/**
 * Two-Factor Authentication Setup Modal
 * Guide user through 2FA setup with QR code and verification
 */
const TwoFactorSetup = ({ onClose, onComplete }) => {
    const [step, setStep] = useState(1); // 1: QR Code, 2: Verify
    const [secretData, setSecretData] = useState(null);
    const [verifyCode, setVerifyCode] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [copied, setCopied] = useState(false);

    // Fetch QR code and secret from API
    const fetchSetupData = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('git_alpha_token');
            const res = await fetch('http://127.0.0.1:8000/api/auth/2fa/setup', {
                headers: { Authorization: `Bearer ${token}` }
            });

            if (res.ok) {
                const data = await res.json();
                setSecretData(data);
            } else {
                const err = await res.json();
                setError(err.detail || 'Failed to setup 2FA');
            }
        } catch (err) {
            setError('Network error');
        } finally {
            setLoading(false);
        }
    };

    React.useEffect(() => {
        fetchSetupData();
    }, []);

    // Copy secret to clipboard
    const copySecret = () => {
        if (secretData?.secret) {
            navigator.clipboard.writeText(secretData.secret);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    // Verify 2FA code
    const handleVerify = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const token = localStorage.getItem('git_alpha_token');
            const res = await fetch('http://127.0.0.1:8000/api/auth/2fa/verify-setup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({ code: verifyCode })
            });

            if (res.ok) {
                onComplete?.();
            } else {
                const err = await res.json();
                setError(err.detail || 'Invalid verification code');
            }
        } catch (err) {
            setError('Network error');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="glass-card max-w-md w-full animate-scale-up">
                {/* Header */}
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                        <Shield className="text-purple-400" size={24} />
                        <h2 className="text-xl font-semibold">Enable Two-Factor Authentication</h2>
                    </div>
                    <button
                        onClick={onClose}
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

                {loading && !secretData ? (
                    <div className="text-center py-8">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400 mx-auto" />
                        <p className="text-slate-400 mt-4">Setting up 2FA...</p>
                    </div>
                ) : step === 1 ? (
                    /* Step 1: Show QR Code */
                    <div className="space-y-4">
                        <p className="text-slate-300 text-sm">
                            Scan this QR code with your authenticator app (Google Authenticator, Authy, etc.)
                        </p>

                        {/* QR Code */}
                        {secretData?.qr_code_url && (
                            <div className="bg-white p-4 rounded-lg mx-auto w-fit">
                                <img
                                    src={secretData.qr_code_url}
                                    alt="2FA QR Code"
                                    className="w-48 h-48"
                                />
                            </div>
                        )}

                        {/* Manual Entry */}
                        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-3">
                            <p className="text-xs text-slate-400 mb-2">Can't scan? Enter this code manually:</p>
                            <div className="flex items-center gap-2">
                                <code className="flex-1 text-sm font-mono text-purple-300 break-all">
                                    {secretData?.secret}
                                </code>
                                <button
                                    onClick={copySecret}
                                    className="p-2 hover:bg-slate-700 rounded transition-colors"
                                >
                                    {copied ? (
                                        <Check size={16} className="text-green-400" />
                                    ) : (
                                        <Copy size={16} className="text-slate-400" />
                                    )}
                                </button>
                            </div>
                        </div>

                        {/* Backup Codes */}
                        {secretData?.backup_codes && (
                            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3">
                                <p className="text-xs text-yellow-300 font-semibold mb-2">Backup Codes (save these!):</p>
                                <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                                    {secretData.backup_codes.map((code, idx) => (
                                        <div key={idx} className="text-yellow-200">{code}</div>
                                    ))}
                                </div>
                            </div>
                        )}

                        <button
                            onClick={() => setStep(2)}
                            className="w-full btn btn-primary"
                        >
                            Continue to Verification
                        </button>
                    </div>
                ) : (
                    /* Step 2: Verify Code */
                    <form onSubmit={handleVerify} className="space-y-4">
                        <p className="text-slate-300 text-sm">
                            Enter the 6-digit code from your authenticator app to verify setup
                        </p>

                        <div>
                            <label className="block text-sm text-slate-300 mb-2">Verification Code</label>
                            <input
                                type="text"
                                value={verifyCode}
                                onChange={(e) => setVerifyCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                                placeholder="000000"
                                className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-3 text-white text-center text-2xl font-mono tracking-widest focus:outline-none focus:border-purple-500"
                                maxLength={6}
                                autoFocus
                                required
                            />
                        </div>

                        <div className="flex gap-3">
                            <button
                                type="button"
                                onClick={() => setStep(1)}
                                className="flex-1 btn btn-ghost"
                                disabled={loading}
                            >
                                Back
                            </button>
                            <button
                                type="submit"
                                className="flex-1 btn btn-primary"
                                disabled={loading || verifyCode.length !== 6}
                            >
                                {loading ? 'Verifying...' : 'Enable 2FA'}
                            </button>
                        </div>
                    </form>
                )}
            </div>
        </div>
    );
};

export default TwoFactorSetup;
