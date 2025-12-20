import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

/**
 * ThemeToggle - Animated theme switcher button
 */
const ThemeToggle = () => {
    const { theme, toggleTheme } = useTheme();

    return (
        <button
            onClick={toggleTheme}
            className="relative w-16 h-8 rounded-full transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-purple-500"
            style={{
                background: theme === 'dark'
                    ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                    : 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
            }}
            aria-label="Toggle theme"
        >
            {/* Toggle indicator */}
            <div
                className={`absolute top-1 w-6 h-6 bg-white rounded-full shadow-lg transform transition-all duration-300 flex items-center justify-center ${theme === 'dark' ? 'translate-x-1' : 'translate-x-9'
                    }`}
            >
                {theme === 'dark' ? (
                    <Moon size={14} className="text-purple-600" />
                ) : (
                    <Sun size={14} className="text-orange-500" />
                )}
            </div>

            {/* Background icons */}
            <div className="absolute inset-0 flex items-center justify-between px-2">
                <Moon size={12} className={`text-white transition-opacity ${theme === 'dark' ? 'opacity-100' : 'opacity-30'}`} />
                <Sun size={12} className={`text-white transition-opacity ${theme === 'light' ? 'opacity-100' : 'opacity-30'}`} />
            </div>
        </button>
    );
};

export default ThemeToggle;
