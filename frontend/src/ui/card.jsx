export const Card = ({ children, className = "" }) => (
    <div
        className={`bg-[#050816] border border-slate-800/70 rounded-2xl shadow-[0_0_40px_rgba(15,23,42,0.7)] ${className}`}
    >
        {children}
    </div>
);
