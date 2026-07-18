import React, { useEffect, useState } from 'react';
import {
    Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer
} from 'recharts';
import {
    Shield, Leaf, Users, TrendingUp, AlertTriangle, CheckCircle, XCircle, ArrowUpRight
} from 'lucide-react';

const HeroScorecard = ({ score, summary }) => {
    const safeScore = (typeof score === 'number' && !isNaN(score)) ? score : 0;
    // Percentage for circle offset
    const radius = 70;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (safeScore / 100) * circumference;

    return (
        <div className="col-span-1 lg:col-span-3 bg-navy-800 border border-navy-700 rounded-3xl p-8 backdrop-blur-lg bg-opacity-40 flex items-center justify-between relative overflow-hidden group">
            {/* Background Accent */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/10 blur-[100px] -mr-32 -mt-32"></div>

            <div className="z-10 flex-1 pr-12">
                <div className="flex items-center space-x-3 mb-4">
                    <span className="bg-emerald-500/10 text-emerald-500 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">Alignment Score</span>
                </div>
                <h2 className="text-3xl font-bold text-white mb-4 leading-tight">Project Suitability Level</h2>
                <p className="text-gray-400 max-w-xl leading-relaxed italic">
                    "{summary}"
                </p>
            </div>

            {/* Circular Progress */}
            <div className="relative flex items-center justify-center w-48 h-48 z-10 transition-transform duration-500 group-hover:scale-105">
                <svg className="w-full h-full transform -rotate-90">
                    <circle
                        cx="96" cy="96" r={radius}
                        stroke="currentColor" strokeWidth="12"
                        className="text-navy-700" fill="transparent"
                    />
                    <circle
                        cx="96" cy="96" r={radius}
                        stroke="currentColor" strokeWidth="12"
                        strokeDasharray={circumference}
                        strokeDashoffset={offset}
                        strokeLinecap="round"
                        className="text-emerald-500 drop-shadow-[0_0_8px_rgba(16,185,129,0.5)]"
                        fill="transparent"
                    />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-4xl font-black text-white">{safeScore}</span>
                    <span className="text-[10px] uppercase tracking-tighter text-gray-500 font-bold">Points</span>
                </div>
            </div>
        </div>
    );
};

const MetricCard = ({ category, data }) => {
    const configs = {
        environmental: { icon: Leaf, color: 'emerald' },
        social: { icon: Users, color: 'blue' },
        governance: { icon: Shield, color: 'purple' },
        roi: { icon: TrendingUp, color: 'emerald' },
        risk: { icon: AlertTriangle, color: 'orange' },
    };
    const { icon: Icon, color } = configs[category] || { icon: Leaf, color: 'emerald' };

    return (
        <div className="bg-navy-800 border border-navy-700 rounded-2xl p-6 hover:border-emerald-500/50 transition-all cursor-default group">
            <div className="flex justify-between items-start mb-4">
                <div className={`p-3 rounded-xl bg-navy-700 text-emerald-400 group-hover:bg-emerald-500 group-hover:text-white transition-colors`}>
                    <Icon size={24} />
                </div>
                <span className="text-2xl font-black text-white">{data?.score || 0}</span>
            </div>
            <h3 className="text-sm font-bold text-gray-300 uppercase tracking-wide mb-2 capitalize">{category}</h3>
            <p className="text-xs text-gray-500 line-clamp-2">{data?.summary || 'No analysis available.'}</p>
        </div>
    );
};

const InsightsPanel = ({ analysis }) => {
    const [activeTab, setActiveTab] = useState('fixes');

    const sections = {
        strengths: {
            id: 'strengths', label: 'Core Strengths', icon: CheckCircle,
            color: 'text-emerald-500', bg: 'bg-emerald-500/10'
        },
        gaps: {
            id: 'gaps', label: 'Identified Gaps', icon: XCircle,
            color: 'text-red-400', bg: 'bg-red-400/10'
        },
        fixes: {
            id: 'fixes', label: 'Action Items', icon: ArrowUpRight,
            color: 'text-blue-400', bg: 'bg-blue-400/10'
        }
    };

    // Flatten all categories' data (filter out non-object values and nulls)
    const allInsights = {
        strengths: Object.values(analysis || {}).filter(v => v && typeof v === 'object').flatMap(v => v.strengths || []),
        gaps: Object.values(analysis || {}).filter(v => v && typeof v === 'object').flatMap(v => v.gaps || []),
        fixes: Object.values(analysis || {}).filter(v => v && typeof v === 'object').flatMap(v => v.action_items || [])
    };

    return (
        <div className="lg:col-span-2 bg-navy-800 border border-navy-700 rounded-2xl overflow-hidden flex flex-col">
            <div className="flex border-b border-navy-700 bg-navy-900/50">
                {Object.values(sections).map(s => (
                    <button
                        key={s.id}
                        onClick={() => setActiveTab(s.id)}
                        className={`px-6 py-4 flex items-center space-x-2 text-xs font-bold uppercase transition-all border-b-2 ${activeTab === s.id ? 'border-emerald-500 text-white' : 'border-transparent text-gray-500 hover:text-gray-300'
                            }`}
                    >
                        <s.icon size={14} />
                        <span>{s.label}</span>
                    </button>
                ))}
            </div>
            <div className="p-6 flex-1 max-h-96 overflow-y-auto space-y-3">
                {allInsights[activeTab]?.map((item, i) => (
                    <div key={i} className={`p-4 rounded-xl ${sections[activeTab].bg} border border-white/5 flex items-start space-x-3`}>
                        <div className={`mt-1 ${sections[activeTab].color}`}>
                            <ArrowUpRight size={14} />
                        </div>
                        <span className="text-sm text-gray-300 leading-relaxed font-medium">{item}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

const Dashboard = ({ data }) => {
    // Extensive Debug Logging
    useEffect(() => {
        console.group("Dashboard Data Analysis");
        console.log("Full Object:", data);
        console.groupEnd();
    }, [data]);

    if (!data || !data.analysis) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[400px] text-gray-500 space-y-4">
                <AlertTriangle size={48} className="text-orange-500" />
                <div className="text-center">
                    <p className="text-xl font-bold text-white">Analysis Data Unavailable</p>
                    <p className="text-sm">Please start a new analysis to generate insights for this project.</p>
                </div>
            </div>
        );
    }

    const analysis = data.analysis;

    // 1. Robust Mapping for Radar & Metrics (handle potentially missing domains)
    const getScore = (domain) => {
        const val = analysis?.[domain]?.score;
        return (typeof val === 'number' && !isNaN(val)) ? val : 0;
    };

    // 2. Formatted Summary (Combined from domains if executive summary is missing)
    const combinedSummary = analysis?.executive_summary ||
        analysis?.environmental?.summary ||
        analysis?.social?.summary ||
        "Analysis complete. Detailed metrics and domain breakdowns are available below.";

    const radarData = [
        { subject: 'Env', A: getScore('environmental'), fullMark: 100 },
        { subject: 'Soc', A: getScore('social'), fullMark: 100 },
        { subject: 'Gov', A: getScore('governance'), fullMark: 100 },
        { subject: 'ROI', A: getScore('roi'), fullMark: 100 },
        { subject: 'Risk', A: getScore('risk'), fullMark: 100 },
    ];

    return (
        <div className="space-y-8 pb-20">
            {/* Header Hero */}
            <HeroScorecard
                score={analysis?.final_weighted_score || 0}
                summary={combinedSummary}
            />

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Radar Chart */}
                <div className="bg-navy-800 border border-navy-700 rounded-3xl p-8 flex flex-col items-center justify-center min-h-[400px]">
                    <h3 className="text-xs font-black uppercase text-gray-500 tracking-widest mb-8">Risk/Value Balance</h3>
                    <div className="w-full h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                                <PolarGrid stroke="#1e293b" />
                                <PolarAngleAxis dataKey="subject" tick={{ fill: '#475569', fontSize: 10, fontWeight: 'bold' }} />
                                <Radar
                                    name="Project"
                                    dataKey="A"
                                    stroke="#10b981"
                                    fill="#10b981"
                                    fillOpacity={0.3}
                                />
                            </RadarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Insights Panel */}
                <InsightsPanel analysis={analysis} />
            </div>

            {/* Metric Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
                <MetricCard category="environmental" data={analysis?.environmental} />
                <MetricCard category="social" data={analysis?.social} />
                <MetricCard category="governance" data={analysis?.governance} />
                <MetricCard category="roi" data={analysis?.roi} />
                <MetricCard category="risk" data={analysis?.risk} />
            </div>
        </div>
    );
};

export default Dashboard;
