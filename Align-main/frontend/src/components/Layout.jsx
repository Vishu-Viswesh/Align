import React, { useState } from 'react';
import Sidebar from './Sidebar';
import TopBar from './TopBar';

const Layout = ({ children, projects, currentProjectId, onProjectSelect, activeTab, onTabSelect }) => {
    const [isCollapsed, setIsCollapsed] = useState(false);

    return (
        <div className="min-h-screen bg-navy-900 text-gray-100 flex overflow-hidden">
            <Sidebar
                isCollapsed={isCollapsed}
                setIsCollapsed={setIsCollapsed}
                activeTab={activeTab}
                onTabSelect={onTabSelect}
            />

            <div
                className={`flex-1 flex flex-col transition-all duration-300 ${isCollapsed ? 'ml-20' : 'ml-64'
                    }`}
            >
                <TopBar
                    projects={projects}
                    currentProjectId={currentProjectId}
                    onProjectSelect={onProjectSelect}
                />
                <main className="flex-1 mt-16 p-8 overflow-y-auto">
                    {children}
                </main>
            </div>
        </div>
    );
};

export default Layout;
