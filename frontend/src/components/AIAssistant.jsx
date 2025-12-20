import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader, Search, Upload } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const AIAssistant = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [includeContext, setIncludeContext] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const sendMessage = async (messageText = input) => {
        if (!messageText.trim() || isLoading) return;

        const userMessage = { role: 'user', content: messageText };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const token = localStorage.getItem('git_alpha_token');
            const response = await fetch('http://localhost:8000/api/ai-agent/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    message: messageText,
                    stream: false,
                    include_context: includeContext
                })
            });

            if (!response.ok) {
                throw new Error('Failed to get response from AI agent');
            }

            const data = await response.json();
            const aiMessage = { role: 'assistant', content: data.response };
            setMessages(prev => [...prev, aiMessage]);
        } catch (error) {
            console.error('Error:', error);
            const errorMessage = {
                role: 'assistant',
                content: '❌ Sorry, I encountered an error. Please make sure the backend is running and try again.'
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        sendMessage();
    };

    return (
        <div className="h-full w-full flex flex-col bg-[#0a0f1e]">
            {/* Chat Messages Area */}
            <div className="flex-1 overflow-y-auto px-4 py-6 custom-scrollbar">
                {messages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center">
                        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-600 to-cyan-600 flex items-center justify-center mb-6 shadow-xl">
                            <Bot className="w-8 h-8 text-white" />
                        </div>
                        <h2 className="text-2xl font-semibold text-white mb-2">
                            How can I help you today?
                        </h2>
                        <p className="text-slate-400 text-sm max-w-md">
                            Ask me about stocks, market analysis, financial insights, or any trading questions
                        </p>
                    </div>
                ) : (
                    <div className="max-w-4xl mx-auto space-y-6">
                        {messages.map((message, index) => (
                            <div
                                key={index}
                                className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                {message.role === 'assistant' && (
                                    <div className="flex-shrink-0">
                                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-600 to-cyan-600 flex items-center justify-center">
                                            <Bot className="w-5 h-5 text-white" />
                                        </div>
                                    </div>
                                )}

                                <div
                                    className={`max-w-[80%] rounded-2xl px-4 py-3 ${message.role === 'user'
                                        ? 'bg-purple-600 text-white'
                                        : 'bg-slate-800 text-slate-100'
                                        }`}
                                >
                                    {message.role === 'assistant' ? (
                                        <div className="prose prose-invert prose-sm max-w-none prose-p:text-slate-100 prose-headings:text-white prose-code:text-cyan-300 prose-code:bg-black/30 prose-code:px-2 prose-code:py-1 prose-code:rounded">
                                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                                {message.content}
                                            </ReactMarkdown>
                                        </div>
                                    ) : (
                                        <p className="text-sm">{message.content}</p>
                                    )}
                                </div>

                                {message.role === 'user' && (
                                    <div className="flex-shrink-0">
                                        <div className="w-8 h-8 rounded-lg bg-slate-700 flex items-center justify-center">
                                            <User className="w-5 h-5 text-slate-300" />
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}

                        {isLoading && (
                            <div className="flex gap-3 justify-start">
                                <div className="flex-shrink-0">
                                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-600 to-cyan-600 flex items-center justify-center">
                                        <Bot className="w-5 h-5 text-white" />
                                    </div>
                                </div>
                                <div className="bg-slate-800 rounded-2xl px-4 py-3">
                                    <div className="flex items-center gap-2">
                                        <Loader className="w-4 h-4 animate-spin text-cyan-400" />
                                        <div className="flex gap-1">
                                            <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
                                            <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                                            <span className="w-2 h-2 bg-pink-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>
                )}
            </div>

            {/* Input Area */}
            <div className="border-t border-slate-700 bg-[#0a0f1e] p-4">
                <div className="max-w-4xl mx-auto">
                    {/* Context Toggle */}
                    <div className="flex items-center justify-between mb-3">
                        <label className="flex items-center gap-2 text-sm text-slate-400 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={includeContext}
                                onChange={(e) => setIncludeContext(e.target.checked)}
                                className="w-4 h-4 rounded border-slate-600 bg-slate-800 text-purple-600 focus:ring-purple-500 focus:ring-offset-slate-900"
                            />
                            Include Context
                        </label>
                        <div className="flex items-center gap-2">
                            <button
                                className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-300 transition-colors"
                                title="Search"
                            >
                                <Search className="w-4 h-4" />
                            </button>
                            <button
                                className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-300 transition-colors"
                                title="Upload"
                            >
                                <Upload className="w-4 h-4" />
                            </button>
                        </div>
                    </div>

                    {/* Message Input */}
                    <form onSubmit={handleSubmit} className="relative">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Message AI Assistant"
                            className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 pr-12 text-white placeholder-slate-400 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-all"
                            disabled={isLoading}
                        />
                        <button
                            type="submit"
                            disabled={!input.trim() || isLoading}
                            className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-lg bg-purple-600 hover:bg-purple-500 disabled:bg-slate-700 disabled:cursor-not-allowed flex items-center justify-center text-white transition-colors"
                        >
                            <Send className="w-4 h-4" />
                        </button>
                    </form>
                </div>
            </div>

            <style>{`
                .custom-scrollbar::-webkit-scrollbar {
                    width: 6px;
                }
                
                .custom-scrollbar::-webkit-scrollbar-track {
                    background: transparent;
                }
                
                .custom-scrollbar::-webkit-scrollbar-thumb {
                    background: rgba(100, 100, 100, 0.5);
                    border-radius: 10px;
                }
                
                .custom-scrollbar::-webkit-scrollbar-thumb:hover {
                    background: rgba(100, 100, 100, 0.7);
                }

                /* Responsive table styles for AI Assistant */
                .prose table {
                    display: block;
                    max-width: 100%;
                    overflow-x: auto;
                    -webkit-overflow-scrolling: touch;
                    border-collapse: collapse;
                    margin: 1em 0;
                }

                .prose th,
                .prose td {
                    padding: 0.5rem;
                    border: 1px solid rgba(148, 163, 184, 0.3);
                    font-size: 0.75rem;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    max-width: 120px;
                }

                .prose th {
                    background: rgba(100, 100, 100, 0.2);
                    font-weight: 600;
                }

                /* Allow wrapping on smaller screens */
                @media (max-width: 500px) {
                    .prose th,
                    .prose td {
                        white-space: normal;
                        max-width: 80px;
                        font-size: 0.7rem;
                    }
                }

                /* Ensure markdown content doesn't overflow */
                .prose {
                    max-width: 100%;
                    overflow-wrap: break-word;
                    word-wrap: break-word;
                }

                .prose pre {
                    max-width: 100%;
                    overflow-x: auto;
                }
            `}</style>
        </div>
    );
};

export default AIAssistant;
