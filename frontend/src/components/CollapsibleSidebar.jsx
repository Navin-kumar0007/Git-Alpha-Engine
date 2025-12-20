import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

/**
 * CollapsibleSidebar - Expandable/collapsible sidebar with smooth animations
 */
const CollapsibleSidebar = ({
    isCollapsed,
    onToggle,
    children,
    className = ''
}) => {
    return (
        <>
            {/* Sidebar */}
            <div
                className={`
          fixed left-0 top-0 h-full bg-gradient-to-b from-[#050816] to-[#020617] border-r border-slate-800/70
          transition-all duration-300 ease-in-out z-30
          ${isCollapsed ? 'w-16' : 'w-60'}
          ${className}
        `}
            >
                {/* Toggle button */}
                <button
                    onClick={onToggle}
                    className="absolute -right-3 top-20 w-6 h-6 rounded-full bg-purple-600 hover:bg-purple-500 flex items-center justify-center shadow-lg transition-all hover:scale-110 z-40"
                    aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                >
                    {isCollapsed ? (
                        <ChevronRight size={14} className="text-white" />
                    ) : (
                        <ChevronLeft size={14} className="text-white" />
                    )}
                </button>

                {/* Sidebar content */}
                <div className="h-full overflow-y-auto overflow-x-hidden">
                    {typeof children === 'function' ? children({ isCollapsed }) : children}
                </div>
            </div>

            {/* Overlay for mobile */}
            {!isCollapsed && (
                <div
                    className="fixed inset-0 bg-black/50 md:hidden z-20"
                    onClick={onToggle}
                />
            )}
        </>
    );
};

export default CollapsibleSidebar;
