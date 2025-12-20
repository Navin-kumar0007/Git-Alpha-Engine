import React, { useState, useRef, useEffect } from 'react';
import { Bot, Minimize2, Maximize2, X, Move } from 'lucide-react';

/**
 * FloatingAIWidget - Draggable, resizable AI assistant widget
 * Features: Drag, minimize/maximize, docking positions, smooth animations
 */
const FloatingAIWidget = ({ children, onClose }) => {
    // Widget states
    const [isMinimized, setIsMinimized] = useState(false);
    const [isFullScreen, setIsFullScreen] = useState(false);
    const [isDragging, setIsDragging] = useState(false);
    const [position, setPosition] = useState({
        x: Math.max(20, window.innerWidth - 520), // 500px width + 20px margin, min 20px from left
        y: Math.max(20, window.innerHeight - 650)  // Position at bottom with margin (use smaller value to ensure visibility)
    });
    const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

    const widgetRef = useRef(null);

    // Drag handlers
    const handleMouseDown = (e) => {
        if (isFullScreen || isMinimized) return;

        setIsDragging(true);
        const rect = widgetRef.current.getBoundingClientRect();
        setDragOffset({
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        });
    };

    const handleMouseMove = (e) => {
        if (!isDragging) return;

        const newX = e.clientX - dragOffset.x;
        const newY = e.clientY - dragOffset.y;

        // Boundary constraints
        const maxX = window.innerWidth - 400;
        const maxY = window.innerHeight - 100;

        setPosition({
            x: Math.max(0, Math.min(newX, maxX)),
            y: Math.max(0, Math.min(newY, maxY))
        });
    };

    const handleMouseUp = () => {
        setIsDragging(false);
    };

    useEffect(() => {
        if (isDragging) {
            document.addEventListener('mousemove', handleMouseMove);
            document.addEventListener('mouseup', handleMouseUp);
            return () => {
                document.removeEventListener('mousemove', handleMouseMove);
                document.removeEventListener('mouseup', handleMouseUp);
            };
        }
    }, [isDragging, dragOffset]);

    // Docking positions
    const dockBottomRight = () => {
        setPosition({
            x: Math.max(20, window.innerWidth - 520),  // 500px width + 20px margin
            y: Math.max(20, window.innerHeight - 650)   // Position at bottom with margin
        });
    };

    const toggleFullScreen = () => {
        setIsFullScreen(!isFullScreen);
        if (!isFullScreen) {
            setIsMinimized(false);
        }
    };

    const toggleMinimize = () => {
        setIsMinimized(!isMinimized);
        if (!isMinimized) {
            setIsFullScreen(false);
        }
    };

    // Widget styles based on state
    const getWidgetStyle = () => {
        if (isFullScreen) {
            return {
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                width: '100%',
                height: '100%',
                zIndex: 9999
            };
        }

        if (isMinimized) {
            return {
                position: 'fixed',
                bottom: '20px',
                right: '20px',
                width: '60px',
                height: '60px',
                zIndex: 9999
            };
        }

        return {
            position: 'fixed',
            left: `${position.x}px`,
            top: `${position.y}px`,
            width: 'min(95vw, 500px)',
            maxWidth: '500px',
            minWidth: '380px',
            height: 'min(90vh, 750px)',
            maxHeight: '750px',
            minHeight: '550px',
            zIndex: 9999
        };
    };

    return (
        <>
            {/* Minimized state - Floating button */}
            {isMinimized && (
                <div
                    style={getWidgetStyle()}
                    className="glass-card rounded-full flex items-center justify-center cursor-pointer hover-lift group shadow-xl"
                    onClick={toggleMinimize}
                >
                    <Bot className="text-purple-400 group-hover:scale-110 transition-transform" size={28} />
                    <div className="absolute -top-1 -right-1 w-3 h-3 bg-purple-500 rounded-full animate-pulse" />
                </div>
            )}

            {/* Normal/Fullscreen state */}
            {!isMinimized && (
                <div
                    ref={widgetRef}
                    style={getWidgetStyle()}
                    className={`glass-card flex flex-col overflow-hidden shadow-2xl transition-all duration-300 ${isDragging ? 'cursor-grabbing' : ''
                        } ${isFullScreen ? 'rounded-none' : 'rounded-2xl'}`}
                >
                    {/* Header with controls */}
                    <div
                        className={`flex items-center justify-between px-4 py-3 border-b border-slate-700/50 bg-gradient-to-r from-purple-900/20 to-cyan-900/20 ${!isFullScreen && !isMinimized ? 'cursor-grab' : ''
                            }`}
                        onMouseDown={handleMouseDown}
                    >
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-cyan-500 flex items-center justify-center">
                                <Bot size={18} className="text-white" />
                            </div>
                            <div>
                                <h3 className="text-sm font-semibold text-slate-100 break-words">AI Assistant</h3>
                                <p className="text-xs text-slate-400 break-words">Powered by Git-Alpha</p>
                            </div>
                        </div>

                        <div className="flex items-center gap-2">
                            {/* Dock to corner button */}
                            {!isFullScreen && !isMinimized && (
                                <button
                                    onClick={dockBottomRight}
                                    className="p-1.5 rounded-lg hover:bg-slate-700/50 transition-colors"
                                    title="Dock to bottom-right"
                                >
                                    <Move size={16} className="text-slate-400" />
                                </button>
                            )}

                            {/* Minimize */}
                            <button
                                onClick={toggleMinimize}
                                className="p-1.5 rounded-lg hover:bg-slate-700/50 transition-colors"
                                title="Minimize"
                            >
                                <Minimize2 size={16} className="text-slate-400" />
                            </button>

                            {/* Fullscreen toggle */}
                            <button
                                onClick={toggleFullScreen}
                                className="p-1.5 rounded-lg hover:bg-slate-700/50 transition-colors"
                                title={isFullScreen ? 'Exit fullscreen' : 'Fullscreen'}
                            >
                                {isFullScreen ? (
                                    <Minimize2 size={16} className="text-slate-400" />
                                ) : (
                                    <Maximize2 size={16} className="text-slate-400" />
                                )}
                            </button>

                            {/* Close */}
                            {onClose && (
                                <button
                                    onClick={onClose}
                                    className="p-1.5 rounded-lg hover:bg-red-500/20 hover:text-red-400 transition-colors"
                                    title="Close"
                                >
                                    <X size={16} className="text-slate-400" />
                                </button>
                            )}
                        </div>
                    </div>

                    {/* Content area */}
                    <div className="flex-1 overflow-y-auto overflow-x-hidden">
                        {children}
                    </div>
                </div>
            )}
        </>
    );
};

export default FloatingAIWidget;
