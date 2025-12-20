import React from "react";

const Pill = ({ children, variant = "default" }) => {
    const variants = {
        default: "bg-slate-900/80 border-slate-700/80 text-slate-300",
        primary: "bg-[var(--color-purple)]/20 border-[var(--color-purple)]/40 text-[var(--color-purple-light)]",
        success: "bg-[var(--color-emerald)]/20 border-[var(--color-emerald)]/40 text-[var(--color-emerald-light)]",
        info: "bg-[var(--color-cyan)]/20 border-[var(--color-cyan)]/40 text-[var(--color-cyan-light)]",
    };

    return (
        <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full border text-[10px] uppercase tracking-wide transition-all ${variants[variant]}`}>
            {children}
        </span>
    );
};

export default Pill;
