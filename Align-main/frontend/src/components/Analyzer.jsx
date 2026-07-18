import React, { useState, useEffect, useRef } from 'react';
import { Send, Loader2, AlertCircle, Info, Sparkles } from 'lucide-react';

const Analyzer = ({ onAnalysisComplete }) => {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [loading, setLoading] = useState(false);
    const [logs, setLogs] = useState([]);
    const [error, setError] = useState(null);
    const logEndRef = useRef(null);

    useEffect(() => {
        logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [logs]);

    const startAnalysis = async (e) => {
        e.preventDefault();
        if (!title || !description) return;

        setLoading(true);
        setLogs(['Initializing WebSocket connection...']);
        setError(null);

        const ws = new WebSocket('ws://127.0.0.1:8000/ws/status');

        ws.onmessage = (event) => {
            setLogs((prev) => [...prev, event.data]);
        };

        ws.onopen = () => {
            setLogs((prev) => [...prev, 'Connected to Analysis Engine. Sending request...']);

            fetch('http://localhost:8000/projects/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, description })
            })
                .then(async res => {
                    if (!res.ok) throw new Error(await res.text());
                    return res.json();
                })
                .then(data => {
                    setLogs((prev) => [...prev, '✓ Analysis Result Received. Redirecting...']);
                    setTimeout(() => {
                        onAnalysisComplete(data);
                        setLoading(false);
                        ws.close();
                    }, 1500);
                })
                .catch(err => {
                    setError(err.message);
                    setLoading(false);
                    ws.close();
                });
        };

        ws.onerror = () => {
            setError("WebSocket connection failed. Ensure backend is running.");
            setLoading(false);
        };
    };

    return (
        <div className="max-w-2xl mx-auto py-12">
            <div className="bg-navy-800 border border-navy-700 rounded-3xl overflow-hidden backdrop-blur-lg bg-opacity-40 shadow-2xl">

                {/* Header */}
                <div className="p-8 border-b border-navy-700 bg-navy-900/50">
                    <div className="flex items-center space-x-3 mb-2">
                        <div className="bg-emerald-500/20 text-emerald-500 p-2 rounded-lg">
                            <Sparkles size={20} />
                        </div>
                        <h2 className="text-2xl font-bold text-white">Project Initiator</h2>
                    </div>
                    <p className="text-gray-400 text-sm">Deploy the 5-Agent Aligned Crew to evaluate your infrastructure project.</p>
                </div>

                <div className="p-8">
                    {!loading ? (
                        <form onSubmit={startAnalysis} className="space-y-6">
                            <div className="space-y-2">
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-widest pl-1">Project Title</label>
                                <input
                                    type="text"
                                    value={title}
                                    onChange={(e) => setTitle(e.target.value)}
                                    className="w-full bg-navy-900 border border-navy-700 text-white px-5 py-4 rounded-2xl focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 outline-none transition-all placeholder-gray-600"
                                    placeholder="e.g. Green Horizon Solar Farm"
                                    required
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-widest pl-1">Description & Context</label>
                                <textarea
                                    value={description}
                                    onChange={(e) => setDescription(e.target.value)}
                                    className="w-full bg-navy-900 border border-navy-700 text-white px-5 py-4 rounded-2xl focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 outline-none transition-all h-40 resize-none placeholder-gray-600"
                                    placeholder="Details on location, capacity, social commitment, financial goals..."
                                    required
                                />
                            </div>

                            {error && (
                                <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-2xl flex items-center space-x-3 text-red-400 text-sm">
                                    <AlertCircle size={18} />
                                    <span>{error}</span>
                                </div>
                            )}

                            <button
                                type="submit"
                                className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-5 rounded-2xl flex items-center justify-center space-x-3 transition-all transform hover:scale-[1.01] active:scale-[0.98] shadow-lg shadow-emerald-900/20"
                            >
                                <span className="uppercase tracking-widest text-sm">Kickoff Analysis</span>
                                <Send size={18} />
                            </button>
                        </form>
                    ) : (
                        <div className="space-y-8 py-4">
                            <div className="flex flex-col items-center justify-center">
                                <div className="relative mb-6">
                                    <Loader2 className="animate-spin text-emerald-500" size={56} />
                                    <div className="absolute inset-0 bg-emerald-500/20 blur-xl rounded-full"></div>
                                </div>
                                <h3 className="text-xl font-bold text-white mb-2 tracking-tight">Agents are Scrutinizing...</h3>
                                <p className="text-gray-500 text-sm text-center max-w-xs">
                                    Performing multi-domain weighted analysis. CO2 impact, Labor standards, and ROI predicted.
                                </p>
                            </div>

                            {/* Progress Logs */}
                            <div className="bg-navy-900 rounded-2xl p-6 font-mono text-[10px] h-64 overflow-y-auto border border-navy-700 shadow-inner custom-scrollbar">
                                {logs.map((log, i) => (
                                    <div key={i} className="mb-2 flex items-start space-x-3 group">
                                        <span className="text-navy-500 shrink-0">[{new Date().toLocaleTimeString([], { hour12: false })}]</span>
                                        <span className={`${log.includes('ERROR') ? 'text-red-400' :
                                                log.includes('COMPLETED') ? 'text-emerald-400 font-bold' :
                                                    'text-emerald-500/70'
                                            }`}>
                                            {log}
                                        </span>
                                    </div>
                                ))}
                                <div ref={logEndRef} />
                            </div>

                            <div className="flex items-center space-x-3 text-emerald-400 bg-emerald-500/5 px-5 py-4 rounded-2xl border border-emerald-500/10 text-xs">
                                <Info size={16} />
                                <p className="leading-relaxed">The 5-agent Aligned Crew ensures your projects are perfectly placed for long-term sustainability.</p>
                            </div>
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
};

export default Analyzer;
