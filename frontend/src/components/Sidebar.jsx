import React from 'react';
import {
    LayoutDashboard,
    FileSearch,
    History,
    ChevronLeft,
    ChevronRight,
    Leaf,
    Settings,
    LogOut
} from 'lucide-react';

const Sidebar = ({ isCollapsed, setIsCollapsed, activeTab, onTabSelect }) => {
    const navItems = [
        { id: 'initiator', label: 'Project Initiator', icon: FileSearch },
        { id: 'overview', label: 'Project Overview', icon: LayoutDashboard },
        { id: 'history', label: 'History', icon: History },
    ];

    return (
        <aside
            className={`bg-navy-900 border-r border-navy-700 transition-all duration-300 flex flex-col ${isCollapsed ? 'w-20' : 'w-64'
                } h-screen fixed left-0 top-0 z-50`}
        >
            {/* Logo Section */}
            <div className="p-6 flex items-center justify-between border-b border-navy-700">
                {!isCollapsed && (
                    <div className="flex items-center space-x-2">
                        <div className="bg-emerald-500 p-1.5 rounded-lg">
                            <Leaf size={20} className="text-white" />
                        </div>
                        <span className="text-xl font-bold text-white tracking-tight">EcoAlign</span>
                    </div>
                )}
                {isCollapsed && (
                    <div className="bg-emerald-500 p-1.5 rounded-lg mx-auto">
                        <Leaf size={20} className="text-white" />
                    </div>
                )}
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-4 py-6 space-y-2">
                {navItems.map((item) => (
                    <button
                        key={item.id}
                        onClick={() => onTabSelect(item.id)}
                        className={`w-full flex items-center p-3 rounded-xl transition-all group ${activeTab === item.id
                                ? 'bg-emerald-500/10 text-emerald-500 font-bold border border-emerald-500/20'
                                : 'text-gray-400 hover:text-white hover:bg-navy-800'
                            }`}
                    >
                        <item.icon size={22} className="min-w-[22px]" />
                        {!isCollapsed && (
                            <span className="ml-4 font-medium">{item.label}</span>
                        )}
                    </button>
                ))}
            </nav>

            {/* Footer / Collapse Trigger */}
            <div className="p-4 border-t border-navy-700">
                <button
                    onClick={() => setIsCollapsed(!isCollapsed)}
                    className="w-full flex items-center justify-center p-2 rounded-lg bg-navy-800 text-gray-400 hover:text-white transition-all"
                >
                    {isCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
                </button>
            </div>
        </aside>
    );
};

export default Sidebar;
