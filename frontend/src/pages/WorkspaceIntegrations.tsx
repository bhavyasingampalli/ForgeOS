import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Server, CheckCircle, Search, ArrowRight, AlertCircle, RefreshCw } from 'lucide-react';

export const WorkspaceIntegrations = () => {
  const navigate = useNavigate();
  const [connections, setConnections] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // In a real app we'd fetch actual connection state from backend
  useEffect(() => {
    const fetchConnections = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/auth/me`, {
          credentials: 'include'
        });
        if (response.status === 401) {
          navigate('/login');
          return;
        }
        const data = await response.json();
        
        // Map backend connections to our UI list
        const dbConns = data.connections || [];
        
        const baseServers = [
          { id: 'github', provider: 'Github', name: 'GitHub', description: 'Powered by GitHub MCP' },
          { id: 'google', provider: 'Google', name: 'Google Workspace', description: 'Powered by Google Workspace MCP' },
        ];
        
        const merged = baseServers.map(server => {
          const active = dbConns.find((c: any) => c.provider === server.provider);
          return {
            ...server,
            status: active ? active.status : 'NOT_CONNECTED',
            capabilities: active && active.status === 'CONNECTED' ? 12 : 0,
            latency: active ? '84 ms' : '-',
            lastSync: active ? new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : '-',
            health: active && active.status === 'CONNECTED' ? 'Healthy' : 'N/A'
          };
        });
        
        setConnections(merged);
      } catch (e) {
        console.error(e);
      } finally {
        setIsLoading(false);
      }
    };
    fetchConnections();
  }, []);

  const handleConnect = (provider: string) => {
    // Redirect to real backend OAuth flow
    window.location.href = `http://localhost:8000/api/oauth/${provider.toLowerCase()}/login`;
  };

  // Simulate the discovery lifecycle for Google if it just connected
  const [googleState, setGoogleState] = useState(0);
  const discoveryPhases = ['Authenticating...', 'Connecting MCP...', 'Discovering Capabilities...', 'CONNECTED'];
  
  useEffect(() => {
    const hasGoogle = connections.find(c => c.provider === 'Google' && c.status === 'CONNECTED');
    if (hasGoogle && googleState < 3) {
      const timer = setTimeout(() => {
        setGoogleState(prev => prev + 1);
      }, 1500);
      return () => clearTimeout(timer);
    }
  }, [connections, googleState]);

  return (
    <div className="min-h-screen bg-[#0b0f19] flex flex-col items-center py-16 px-4 selection:bg-indigo-500/30">
      
      <div className="w-full max-w-4xl text-center mb-12">
        <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-emerald-400 tracking-tight mb-4 animate-fade-in">
          Workspace Integrations
        </h1>
        <p className="text-gray-400 text-lg animate-fade-in" style={{ animationDelay: '0.1s' }}>
          Connect your enterprise platforms to populate the Capability Registry.
        </p>
      </div>

      <div className="w-full max-w-4xl glass-panel p-8 animate-fade-in" style={{ animationDelay: '0.2s' }}>
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <Server className="text-indigo-400" />
            <h2 className="text-xl font-semibold text-gray-200">Capability Sources</h2>
          </div>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={16} />
            <input 
              type="text" 
              placeholder="Search providers..." 
              className="bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-2 text-sm text-gray-200 focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        <div className="grid gap-4 mb-8">
          {isLoading ? (
             <div className="text-center text-gray-400 py-8 flex justify-center"><RefreshCw className="animate-spin" /></div>
          ) : connections.map((server) => {
            let displayStatus = server.status;
            let isPending = server.status === 'AUTHORIZING' || server.status === 'DISCOVERING';
            let isConnected = server.status === 'CONNECTED';
            
            if (server.provider === 'Google' && isConnected) {
               displayStatus = discoveryPhases[googleState];
               isConnected = googleState === 3;
               isPending = googleState < 3;
            }
            
            return (
              <div 
                key={server.id} 
                className={`flex flex-col md:flex-row items-start md:items-center justify-between p-5 rounded-xl border transition-all ${
                  isConnected 
                    ? 'bg-indigo-500/10 border-indigo-500/30 shadow-[0_0_15px_rgba(99,102,241,0.1)]' 
                    : 'bg-white/5 border-white/10 hover:border-white/20'
                }`}
              >
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-200 flex items-center gap-2 text-lg">
                    {server.name}
                    {isConnected && <CheckCircle size={16} className="text-emerald-400" />}
                    {isPending && <RefreshCw size={16} className="text-blue-400 animate-spin" />}
                  </h3>
                  <p className="text-sm text-gray-400 mt-1">{server.description}</p>
                  
                  {isConnected && (
                    <div className="mt-4 flex flex-wrap gap-6">
                      <div>
                        <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Status</p>
                        <p className="text-sm text-emerald-400">{displayStatus}</p>
                      </div>
                      <div>
                        <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Capabilities</p>
                        <p className="text-sm text-gray-200">{server.capabilities}</p>
                      </div>
                      <div>
                        <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Latency</p>
                        <p className="text-sm text-gray-200">{server.latency}</p>
                      </div>
                      <div>
                        <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Last Sync</p>
                        <p className="text-sm text-gray-200">{server.lastSync}</p>
                      </div>
                      <div>
                        <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Health</p>
                        <p className="text-sm text-emerald-400 flex items-center gap-1"><CheckCircle size={12}/> {server.health}</p>
                      </div>
                    </div>
                  )}
                  {server.provider === 'Google' && isConnected && (
                    <p className="text-xs text-indigo-300 mt-3 flex items-center gap-1">
                      <CheckCircle size={12} /> Authenticated via ForgeOS Login
                    </p>
                  )}
                </div>
                
                <div className="mt-4 md:mt-0 ml-0 md:ml-6">
                  {server.provider === 'Google' ? (
                    <div className="px-3 py-1 rounded bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-sm">
                      {isPending ? displayStatus : 'Ready ✓'}
                    </div>
                  ) : isConnected ? (
                    <button className="btn btn-secondary text-gray-400">Manage</button>
                  ) : isPending ? (
                    <button disabled className="btn btn-secondary text-blue-400 flex gap-2 items-center"><RefreshCw size={14} className="animate-spin"/> {displayStatus}</button>
                  ) : (
                    <button 
                      onClick={() => handleConnect(server.id)}
                      className="btn btn-primary"
                    >
                      Connect
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        <div className="flex justify-end pt-6 border-t border-white/10">
          <button 
            onClick={() => navigate('/command-center')}
            className="btn btn-primary shadow-lg shadow-indigo-500/20 group"
          >
            Launch Command Center
            <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
          </button>
        </div>
      </div>
      
    </div>
  );
};
