import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

/**
 * OAuth Callback Handler
 * Handles the OAuth redirect callback and stores the token
 */
const OAuthCallback = ({ onLoginSuccess }) => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();

    useEffect(() => {
        const token = searchParams.get('token');
        const provider = searchParams.get('provider');

        if (token) {
            // Store token
            localStorage.setItem('git_alpha_token', token);

            // Fetch user data
            fetch('http://127.0.0.1:8000/api/me', {
                headers: { Authorization: `Bearer ${token}` }
            })
                .then(res => res.json())
                .then(user => {
                    if (onLoginSuccess) {
                        onLoginSuccess(user);
                    }
                    navigate('/', { replace: true });
                })
                .catch(err => {
                    console.error('Error fetching user:', err);
                    navigate('/login', { replace: true });
                });
        } else {
            // No token, redirect to login
            navigate('/login', { replace: true });
        }
    }, [searchParams, navigate, onLoginSuccess]);

    return (
        <div className="flex items-center justify-center min-h-screen">
            <div className="text-center">
                <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-400 mx-auto mb-4" />
                <p className="text-slate-300 text-lg">Completing sign-in...</p>
            </div>
        </div>
    );
};

export default OAuthCallback;
