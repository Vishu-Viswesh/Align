import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import Analyzer from './components/Analyzer';
import Layout from './components/Layout';
import { solarProjectMock } from './mockData';

function App() {
  const [report, setReport] = useState(null);
  const [projects, setProjects] = useState([]);
  const [activeTab, setActiveTab] = useState('initiator');
  const [currentProjectId, setCurrentProjectId] = useState(null);

  // 1. Fetch project list on mount
  useEffect(() => {
    fetchProjects();
  }, []);

  // Log state changes for debugging
  useEffect(() => {
    console.log("State changed: report", report);
  }, [report]);

  useEffect(() => {
    console.log("State changed: projects", projects);
  }, [projects]);

  useEffect(() => {
    console.log("State changed: activeTab", activeTab);
  }, [activeTab]);

  useEffect(() => {
    console.log("State changed: currentProjectId", currentProjectId);
  }, [currentProjectId]);

  const parseProjectData = (data) => {
    if (!data) return data;
    let parsedAnalysis = data.analysis;

    const extractAndParseJSON = (str) => {
      if (!str || typeof str !== 'string') return null;
      try {
        let cleanStr = str.trim();
        // Handle markdown blocks
        if (cleanStr.includes('```json')) {
          cleanStr = cleanStr.split('```json')[1].split('```')[0].trim();
        } else if (cleanStr.includes('```')) {
          cleanStr = cleanStr.split('```')[1].split('```')[0].trim();
        }

        // Find { and } boundaries if not already a clean JSON
        const start = cleanStr.indexOf('{');
        const end = cleanStr.lastIndexOf('}');

        if (start !== -1 && end !== -1) {
          const jsonOnly = cleanStr.substring(start, end + 1);
          return JSON.parse(jsonOnly);
        }

        return JSON.parse(cleanStr); // Try parsing the whole thing if no { } found (unlikely)
      } catch (e) {
        return null;
      }
    };

    // Case 1: Analysis is a direct string
    if (typeof parsedAnalysis === 'string') {
      const parsed = extractAndParseJSON(parsedAnalysis);
      if (parsed) parsedAnalysis = parsed;
    }
    // Case 2: Analysis is an object but executive_summary contains the real JSON (Backend fallback case)
    else if (parsedAnalysis && typeof parsedAnalysis === 'object' && parsedAnalysis.executive_summary) {
      const nested = extractAndParseJSON(parsedAnalysis.executive_summary);
      if (nested && typeof nested === 'object') {
        parsedAnalysis = { ...parsedAnalysis, ...nested };
      }
    }

    return { ...data, analysis: parsedAnalysis };
  };


  const fetchProjects = async () => {
    try {
      const res = await fetch('http://localhost:8000/projects');
      const data = await res.json();
      setProjects(data);
    } catch (err) {
      console.error("Failed to fetch projects:", err);
    }
  };

  const handleAnalysisComplete = (rawData) => {
    const data = parseProjectData(rawData);
    setReport(data);
    setActiveTab('overview');
    setCurrentProjectId(data.project_id);

    // Optimistic update of the projects list
    setProjects(prev => {
      const exists = prev.find(p => p.project_id === data.project_id);
      if (exists) return prev;
      return [...prev, { project_id: data.project_id, project_title: data.project_title }];
    });

    fetchProjects(); // Also refresh from server
  };

  const handleProjectSelect = async (projectId) => {
    try {
      const res = await fetch(`http://localhost:8000/projects/${projectId}`);
      if (!res.ok) throw new Error("Failed to fetch project");
      const rawData = await res.json();
      const data = parseProjectData(rawData);
      setReport(data);
      setCurrentProjectId(projectId);
      setActiveTab('overview');
    } catch (err) {
      console.error(err);
    }
  };

  const handleTabSelect = (tabId) => {
    if (tabId === 'initiator') {
      setReport(null);
      setCurrentProjectId(null);
    }
    setActiveTab(tabId);
  };

  return (
    <Layout
      projects={projects}
      currentProjectId={currentProjectId}
      onProjectSelect={handleProjectSelect}
      activeTab={activeTab}
      onTabSelect={handleTabSelect}
    >
      <div className="absolute top-4 right-4 z-[100]">
        <button
          onClick={() => handleAnalysisComplete(solarProjectMock)}
          className="bg-navy-700 hover:bg-navy-600 border border-navy-500 text-[10px] text-gray-500 px-2 py-1 rounded transition-all"
        >
          DEBUG: LOAD MOCK
        </button>
      </div>

      {activeTab === 'initiator' ? (
        <Analyzer onAnalysisComplete={handleAnalysisComplete} />
      ) : activeTab === 'overview' && report ? (
        <Dashboard data={report} />
      ) : (
        <div className="flex flex-col items-center justify-center h-full text-gray-500 space-y-4">
          <p>Please select a project from the top bar or start a new analysis.</p>
          <button
            onClick={() => setActiveTab('initiator')}
            className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-lg text-sm font-bold transition-all"
          >
            Go to Initiator
          </button>
        </div>
      )}
    </Layout>
  );
}

export default App;
