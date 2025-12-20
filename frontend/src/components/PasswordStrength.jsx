import React from 'react';
import { Check, X, Lock, Shield } from 'lucide-react';

/**
 * Password Strength Meter Component
 * Real-time password strength analysis with visual feedback
 */
const PasswordStrength = ({ password = '' }) => {
    // Calculate password strength
    const calculateStrength = (pwd) => {
        let score = 0;
        const feedback = [];

        // Individual checks
        const has_length = pwd.length >= 8;
        const has_uppercase = /[A-Z]/.test(pwd);
        const has_lowercase = /[a-z]/.test(pwd);
        const has_numbers = /\d/.test(pwd);
        const has_special = /[!@#$%^&*(),.?":{}|<>]/.test(pwd);

        // Calculate score
        if (has_length) score++; else feedback.push("Use at least 8 characters");
        if (has_uppercase) score++; else feedback.push("Add uppercase letters");
        if (has_lowercase) score++; else feedback.push("Add lowercase letters");
        if (has_numbers) score++; else feedback.push("Add numbers");
        if (has_special) score++; else feedback.push("Add special characters");

        // Bonus for longer passwords
        if (pwd.length >= 12) score = Math.min(score + 0.5, 5);
        if (pwd.length >= 16) score = Math.min(score + 0.5, 5);

        // Normalize to 0-4
        score = Math.min(Math.floor(score), 4);

        // Determine strength text
        const strength_levels = {
            0: 'Very Weak',
            1: 'Weak',
            2: 'Fair',
            3: 'Strong',
            4: 'Very Strong'
        };
        const strength_text = strength_levels[score] || 'Unknown';

        // Positive feedback for strong passwords
        if (score >= 4) {
            return { score, strength_text, feedback: ['Excellent password strength!'], has_length, has_uppercase, has_lowercase, has_numbers, has_special };
        } else if (score === 3) {
            return { score, strength_text, feedback: ['Good password strength'], has_length, has_uppercase, has_lowercase, has_numbers, has_special };
        }

        return { score, strength_text, feedback, has_length, has_uppercase, has_lowercase, has_numbers, has_special };
    };

    const strength = password ? calculateStrength(password) : null;

    // Don't show anything if no password
    if (!password) return null;

    // Color based on strength
    const getColor = (score) => {
        if (score <= 1) return 'bg-red-500';
        if (score === 2) return 'bg-yellow-500';
        if (score === 3) return 'bg-blue-500';
        return 'bg-green-500';
    };

    const getTextColor = (score) => {
        if (score <= 1) return 'text-red-400';
        if (score === 2) return 'text-yellow-400';
        if (score === 3) return 'text-blue-400';
        return 'text-green-400';
    };

    return (
        <div className="space-y-2 animate-fade-in">
            {/* Strength Bar */}
            <div className="flex items-center gap-2">
                <Shield size={16} className={getTextColor(strength.score)} />
                <div className="flex-1 h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div
                        className={`h-full transition-all duration-300 ${getColor(strength.score)}`}
                        style={{ width: `${(strength.score / 4) * 100}%` }}
                    />
                </div>
                <span className={`text-sm font-semibold ${getTextColor(strength.score)}`}>
                    {strength.strength_text}
                </span>
            </div>

            {/* Requirements Checklist */}
            <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="flex items-center gap-1">
                    {strength.has_length ? (
                        <Check size={14} className="text-green-400" />
                    ) : (
                        <X size={14} className="text-slate-600" />
                    )}
                    <span className={strength.has_length ? 'text-slate-300' : 'text-slate-500'}>
                        8+ characters
                    </span>
                </div>

                <div className="flex items-center gap-1">
                    {strength.has_uppercase ? (
                        <Check size={14} className="text-green-400" />
                    ) : (
                        <X size={14} className="text-slate-600" />
                    )}
                    <span className={strength.has_uppercase ? 'text-slate-300' : 'text-slate-500'}>
                        Uppercase (A-Z)
                    </span>
                </div>

                <div className="flex items-center gap-1">
                    {strength.has_lowercase ? (
                        <Check size={14} className="text-green-400" />
                    ) : (
                        <X size={14} className="text-slate-600" />
                    )}
                    <span className={strength.has_lowercase ? 'text-slate-300' : 'text-slate-500'}>
                        Lowercase (a-z)
                    </span>
                </div>

                <div className="flex items-center gap-1">
                    {strength.has_numbers ? (
                        <Check size={14} className="text-green-400" />
                    ) : (
                        <X size={14} className="text-slate-600" />
                    )}
                    <span className={strength.has_numbers ? 'text-slate-300' : 'text-slate-500'}>
                        Numbers (0-9)
                    </span>
                </div>

                <div className="flex items-center gap-1 col-span-2">
                    {strength.has_special ? (
                        <Check size={14} className="text-green-400" />
                    ) : (
                        <X size={14} className="text-slate-600" />
                    )}
                    <span className={strength.has_special ? 'text-slate-300' : 'text-slate-500'}>
                        Special characters (!@#$%^&*)
                    </span>
                </div>
            </div>

            {/* Feedback Messages */}
            {strength.feedback.length > 0 && (
                <div className="text-xs text-slate-400 space-y-1">
                    {strength.feedback.map((msg, idx) => (
                        <div key={idx} className="flex items-start gap-1">
                            <span className="text-purple-400">•</span>
                            <span>{msg}</span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default PasswordStrength;
