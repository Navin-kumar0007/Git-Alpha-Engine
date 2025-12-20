import React from 'react';
import { Card } from '../ui/card';

/**
 * ColorShowcase Component
 * Demonstrates all the new vibrant colors, gradients, glows, and animations
 * from the Phase 1 enhancement.
 */
export default function ColorShowcase() {
    const colors = [
        { name: 'Cyan', class: 'hover-glow-cyan', bg: 'bg-[var(--color-cyan)]', text: 'text-cyan-500' },
        { name: 'Purple', class: 'hover-glow', bg: 'bg-[var(--color-purple)]', text: 'text-purple-500' },
        { name: 'Gold', class: 'hover-glow-gold', bg: 'bg-[var(--color-gold)]', text: 'text-yellow-500' },
        { name: 'Emerald', class: 'hover-glow-emerald', bg: 'bg-[var(--color-emerald)]', text: 'text-emerald-500' },
        { name: 'Pink', class: 'hover-glow-pink', bg: 'bg-[var(--color-pink)]', text: 'text-pink-500' },
        { name: 'Orange', class: 'hover-glow-orange', bg: 'bg-[var(--color-orange)]', text: 'text-orange-500' },
        { name: 'Blue', class: 'hover-glow-blue', bg: 'bg-[var(--color-blue)]', text: 'text-blue-500' },
        { name: 'Rose', class: 'hover-glow', bg: 'bg-[var(--color-rose)]', text: 'text-rose-500' },
    ];

    const gradients = [
        { name: 'Primary', class: 'bg-[image:var(--gradient-primary)]' },
        { name: 'Secondary', class: 'bg-[image:var(--gradient-secondary)]' },
        { name: 'Tertiary', class: 'bg-[image:var(--gradient-tertiary)]' },
        { name: 'Rainbow', class: 'bg-[image:var(--gradient-rainbow)]' },
        { name: 'Holographic', class: 'bg-[image:var(--gradient-holographic)]' },
        { name: 'Vibrant', class: 'bg-[image:var(--gradient-vibrant)]' },
    ];

    const markets = [
        { name: 'India 🇮🇳', class: 'market-badge-india' },
        { name: 'USA 🇺🇸', class: 'market-badge-usa' },
        { name: 'UK 🇬🇧', class: 'market-badge-uk' },
        { name: 'Japan 🇯🇵', class: 'market-badge-japan' },
        { name: 'Singapore 🇸🇬', class: 'market-badge-singapore' },
    ];

    const animations = [
        { name: 'Glow Pulse', class: 'animate-glow-pulse' },
        { name: 'Shimmer Flow', class: 'animate-shimmer-flow' },
        { name: 'Neon Border', class: 'animate-neon-border border-2' },
        { name: 'Fade In', class: 'animate-fade-in' },
        { name: 'Scale Up', class: 'animate-scale-up' },
    ];

    return (
        <div className="p-8 space-y-8 max-w-7xl mx-auto">
            {/* Header */}
            <div className="text-center space-y-4">
                <h1 className="text-5xl font-bold gradient-text">
                    Phase 1: Color System Showcase
                </h1>
                <p className="text-xl text-[var(--color-text-secondary)]">
                    Vibrant colors, stunning gradients, and smooth animations
                </p>
            </div>

            {/* Color Palette */}
            <Card className="p-8">
                <h2 className="text-3xl font-bold mb-6 text-gradient-secondary">
                    Vibrant Color Palette
                </h2>
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
                    {colors.map((color) => (
                        <div
                            key={color.name}
                            className={`${color.class} hover-lift cursor-pointer group`}
                        >
                            <div
                                className={`${color.bg} h-24 rounded-xl transition-all duration-300 group-hover:scale-110`}
                            />
                            <p className="text-center mt-2 font-semibold text-[var(--color-text-primary)]">
                                {color.name}
                            </p>
                        </div>
                    ))}
                </div>
            </Card>

            {/* Gradient Showcase */}
            <Card className="p-8">
                <h2 className="text-3xl font-bold mb-6 text-gradient-primary">
                    Enhanced Gradients
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {gradients.map((gradient) => (
                        <div
                            key={gradient.name}
                            className="hover-lift cursor-pointer group"
                        >
                            <div
                                className={`${gradient.class} h-32 rounded-2xl transition-all duration-300 group-hover:shadow-2xl flex items-center justify-center`}
                            >
                                <span className="text-white font-bold text-xl drop-shadow-lg">
                                    {gradient.name}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            </Card>

            {/* Market Badges */}
            <Card className="p-8">
                <h2 className="text-3xl font-bold mb-6" style={{ background: 'var(--gradient-vibrant)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                    Market Badges
                </h2>
                <div className="flex flex-wrap gap-4">
                    {markets.map((market) => (
                        <div
                            key={market.name}
                            className={`market-badge ${market.class} cursor-pointer`}
                        >
                            {market.name}
                        </div>
                    ))}
                </div>
            </Card>

            {/* Market Indicators */}
            <Card className="p-8">
                <h2 className="text-3xl font-bold mb-6 text-gradient-gain">
                    Market Indicators
                </h2>
                <div className="flex gap-8 items-center flex-wrap">
                    <div className="flex items-center gap-3">
                        <div className="market-indicator market-indicator-positive" />
                        <span className="text-gain font-semibold">Positive</span>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="market-indicator market-indicator-negative" />
                        <span className="text-loss font-semibold">Negative</span>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="market-indicator market-indicator-neutral" />
                        <span className="text-[var(--color-neutral)] font-semibold">Neutral</span>
                    </div>
                </div>
            </Card>

            {/* Animations */}
            <Card className="p-8">
                <h2 className="text-3xl font-bold mb-6 text-gradient-loss">
                    Advanced Animations
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                    {animations.map((anim) => (
                        <Card
                            key={anim.name}
                            className={`p-6 ${anim.class} cursor-pointer text-center`}
                        >
                            <p className="font-semibold text-[var(--color-text-primary)]">
                                {anim.name}
                            </p>
                        </Card>
                    ))}
                </div>
            </Card>

            {/* Glow Effects */}
            <Card className="p-8 bg-[var(--color-bg-tertiary)]">
                <h2 className="text-3xl font-bold mb-6 text-white">
                    Glow Intensity Levels
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <div className="text-center">
                        <div className="w-24 h-24 mx-auto rounded-full bg-[var(--color-purple)] shadow-[var(--glow-subtle)_var(--color-purple-glow)] mb-3" />
                        <p className="text-[var(--color-text-secondary)]">Subtle</p>
                    </div>
                    <div className="text-center">
                        <div className="w-24 h-24 mx-auto rounded-full bg-[var(--color-cyan)] shadow-[var(--glow-medium)_var(--color-cyan-glow)] mb-3" />
                        <p className="text-[var(--color-text-secondary)]">Medium</p>
                    </div>
                    <div className="text-center">
                        <div className="w-24 h-24 mx-auto rounded-full bg-[var(--color-gold)] shadow-[var(--glow-strong)_var(--color-gold-glow)] mb-3" />
                        <p className="text-[var(--color-text-secondary)]">Strong</p>
                    </div>
                    <div className="text-center">
                        <div className="w-24 h-24 mx-auto rounded-full bg-[var(--color-emerald)] shadow-[var(--glow-intense)_var(--color-emerald-glow)] mb-3" />
                        <p className="text-[var(--color-text-secondary)]">Intense</p>
                    </div>
                </div>
            </Card>

            {/* Glass Effects */}
            <Card className="p-8">
                <h2 className="text-3xl font-bold mb-6 text-gradient-primary">
                    Glass Morphism Variants
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="p-6 rounded-2xl" style={{
                        background: 'var(--glass-bg-light)',
                        backdropFilter: 'blur(20px)',
                        border: '1px solid var(--glass-border-light)'
                    }}>
                        <h3 className="font-bold text-lg mb-2">Light</h3>
                        <p className="text-[var(--color-text-tertiary)]">Subtle transparency</p>
                    </div>
                    <div className="glass-card">
                        <h3 className="font-bold text-lg mb-2">Standard</h3>
                        <p className="text-[var(--color-text-tertiary)]">Default glass effect</p>
                    </div>
                    <div className="p-6 rounded-2xl" style={{
                        background: 'var(--glass-bg-strong)',
                        backdropFilter: 'blur(20px)',
                        border: '1px solid var(--glass-border-strong)'
                    }}>
                        <h3 className="font-bold text-lg mb-2">Strong</h3>
                        <p className="text-[var(--color-text-tertiary)]">Enhanced visibility</p>
                    </div>
                </div>
            </Card>

            {/* Buttons */}
            <Card className="p-8">
                <h2 className="text-3xl font-bold mb-6 text-gradient-secondary">
                    Button Variants
                </h2>
                <div className="flex flex-wrap gap-4">
                    <button className="btn btn-primary">Primary Button</button>
                    <button className="btn btn-secondary">Secondary Button</button>
                    <button className="btn btn-ghost">Ghost Button</button>
                    <button className="btn" style={{ background: 'var(--gradient-tertiary)', color: 'white' }}>
                        Tertiary Gradient
                    </button>
                    <button className="btn" style={{ background: 'var(--gradient-rainbow)', color: 'white' }}>
                        Rainbow Gradient
                    </button>
                </div>
            </Card>

            {/* Color Scale Example */}
            <Card className="p-8">
                <h2 className="text-3xl font-bold mb-6" style={{ color: 'var(--color-purple)' }}>
                    Color Scale (Purple Example)
                </h2>
                <div className="grid grid-cols-5 md:grid-cols-10 gap-2">
                    {[50, 100, 200, 300, 400, 500, 600, 700, 800, 900].map((shade) => (
                        <div key={shade} className="text-center">
                            <div
                                className="h-16 rounded-lg mb-2"
                                style={{ backgroundColor: `var(--color-purple-${shade})` }}
                            />
                            <p className="text-xs text-[var(--color-text-muted)]">{shade}</p>
                        </div>
                    ))}
                </div>
            </Card>

            {/* Footer */}
            <div className="text-center py-8">
                <p className="text-[var(--color-text-tertiary)] text-lg">
                    🎨 Phase 1 Complete - Ready for Advanced Charting! 🚀
                </p>
            </div>
        </div>
    );
}
