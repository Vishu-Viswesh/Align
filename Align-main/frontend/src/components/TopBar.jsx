import React from 'react';
import { ChevronRight, Database, Server, Share2, User } from 'lucide-react';

const TopBar = ({ projects = [], currentProjectId, onProjectSelect }) => {
    return (
        <header className="h-16 bg-navy-900 border-b border-navy-700 fixed top-0 right-0 left-0 z-40 flex items-center justify-between px-8 ml-0 lg:ml-auto">
            {/* Breadcrumbs */}
            <div className="flex items-center space-x-3 text-sm font-medium">
                <div className="flex items-center text-gray-500 hover:text-gray-300 cursor-pointer">
                    <Database size={16} className="mr-2" />
                    <span>Cluster0</span>
                </div>
                <ChevronRight size={14} className="text-gray-600" />
                <div className="flex items-center text-gray-500 hover:text-gray-300 cursor-pointer">
                    <Server size={16} className="mr-2" />
                    <span>ecoalign</span>
                </div>
                <ChevronRight size={14} className="text-gray-600" />
                <div className="flex items-center text-emerald-500">
                    <Share2 size={16} className="mr-2" />
                    <span>vectors</span>
                </div>
            </div>

            {/* Actions / User */}
            <div className="flex items-center space-x-6">
                <select
                    value={currentProjectId || ''}
                    onChange={(e) => onProjectSelect(e.target.value)}
                    className="bg-navy-800 border-navy-700 text-gray-300 text-xs rounded-lg p-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none min-w-[150px]"
                >
                    <option value="" disabled>Select Project</option>
                    {projects.map(p => (
                        <option key={p.project_id} value={p.project_id}>
                            {p.project_title}
                        </option>
                    ))}
                    {projects.length === 0 && <option disabled>No projects found</option>}
                </select>

                <div className="flex items-center space-x-3 border-l border-navy-700 pl-6">
                    <div className="text-right">
                        <p className="text-xs font-bold text-white">Guest Expert</p>
                        <p className="text-[10px] text-gray-500">Tier 1 License</p>
                    </div>
                    <div className="bg-navy-800 p-2 rounded-full border border-navy-700 text-emerald-500">
                        <User size={18} />
                    </div>
                </div>
            </div>
        </header>
    );
};

export default TopBar;
