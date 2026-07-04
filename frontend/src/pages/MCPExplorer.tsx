import React, { useState, useEffect } from 'react';
import { Activity, Server, Zap, Shield, Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const MCPExplorer = () => {
  const navigate = useNavigate();
  const [toolsData, setToolsData] = useState<any>(null);
  
  useEffect(() => {
    // In a real app, this fetches from /api/tools
    // For this UI demo, we simulate the backend response:
    setTimeout(() => {
      setToolsData({
        "GitHub": {
          health: { status: "Online", latency_ms: 112 },
          tools: [
            { name: "create_repository", description: "Create a new GitHub repository" },
            { name: "create_issue", description: "Create an issue in a repository" },
            { name: "list_pull_requests", description: "List pull requests for a repository" }
          ]
        },
        "Filesystem": {
          health: { status: "Online", latency_ms: 45 },
          tools: [
            { name: "read_file", description: "Read content of a file" },
            { name: "write_file", description: "Write content to a file" }
          ]
        }
      });
    }, 500);
  }, []);

  return (
    <div className="min-h-screen bg-[#0b0f19] flex flex-col items-center py-12 px-4 selection:bg-indigo-500/30">
      
      <div className="w-full max-w-5xl mb-8 flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-gray-200 tracking-tight flex items-center gap-3">
            <Server className="text-indigo-400" size={28} /> MCP Explorer
          </h1>
          <p className="text-gray-400 mt-2">
            Real-time observability into discovered tools and capabilities across all connected remote MCP servers.
          </p>
        </div>
        <button 
          onClick={() => navigate('/command-center')}
          className="btn btn-primary"
        >
          Go to Command Center
        </button>
      </div>

      <div className="w-full max-w-5xl space-y-6">
        {!toolsData ? (
          <div className="text-center text-gray-500 py-12">Discovering tools...</div>
        ) : (
          Object.entries(toolsData).map(([provider, data]: [string, any]) => (
            <div key={provider} className="glass-panel p-6 border-white/5 animate-fade-in">
              <div className="flex justify-between items-center mb-6 pb-4 border-b border-white/5">
                <h2 className="text-xl font-semibold text-gray-200">{provider} MCP</h2>
                <div className="flex gap-4">
                  <span className="flex items-center gap-1.5 text-xs font-semibold bg-emerald-500/10 text-emerald-400 px-2.5 py-1 rounded">
                    <Activity size={14} /> {data.health.status}
                  </span>
                  <span className="flex items-center gap-1.5 text-xs font-semibold bg-indigo-500/10 text-indigo-300 px-2.5 py-1 rounded">
                    <Zap size={14} /> Latency: {data.health.latency_ms} ms
                  </span>
                  <span className="flex items-center gap-1.5 text-xs font-semibold bg-white/5 text-gray-300 px-2.5 py-1 rounded">
                    <Shield size={14} /> {data.tools.length} Tools Discovered
                  </span>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {data.tools.map((tool: any) => (
                  <div key={tool.name} className="bg-white/5 border border-white/5 p-4 rounded-lg hover:bg-white/10 transition-colors">
                    <h3 className="text-indigo-300 font-mono text-sm mb-2">{tool.name}</h3>
                    <p className="text-gray-400 text-xs leading-relaxed">{tool.description}</p>
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
      
    </div>
  );
};
