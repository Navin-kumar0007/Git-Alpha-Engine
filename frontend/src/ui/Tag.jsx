import React from "react";

const Tag = ({ children, color = "purple" }) => {
    const colors = {
        purple: "bg-[var(--color-purple)]/10 text-[var(--color-purple-light)] border-[var(--color-purple)]/30",
        cyan: "bg-[var(--color-cyan)]/10 text-[var(--color-cyan-light)] border-[var(--color-cyan)]/30",
        gold: "bg-[var(--color-gold)]/10 text-[var(--color-gold-light)] border-[var(--color-gold)]/30",
        pink: "bg-[var(--color-pink)]/10 text-[var(--color-pink-light)] border-[var(--color-pink)]/30",
    };

    return (
        <span className={`px-2 py-0.5 rounded-lg text-[10px] border transition-all ${colors[color]}`}>
            {children}
        </span>
    );
};

export default Tag;
