import React, { useState, useEffect } from 'react';
import { 
  Server, MessageSquare, TerminalSquare, Activity, 
  Settings, LogOut, CheckCircle, Clock, PlayCircle, BarChart, ShieldCheck, Box, XCircle
} from 'lucide-react';

export const CommandCenter = () => {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [isPlanning, setIsPlanning] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState('');
  const [executionGoal, setExecutionGoal] = useState('');
  const [dependencies, setDependencies] = useState<string[]>([]);
  const [confidence, setConfidence] = useState(0);
  const [estimatedDuration, setEstimatedDuration] = useState('');
  const [hasStartedChat, setHasStartedChat] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  
  const connectedPlatforms = [
    { name: 'Google Workspace', status: 'Connected', icon: 'Box' },
    { name: 'GitHub', status: 'Connected', icon: 'Box' }
  ];
  
  const [executionPlan, setExecutionPlan] = useState<any[]>([]);
  
  // Mission Control Timeline Stream
  const [activityStream, setActivityStream] = useState<any[]>([]);

  // WebSocket connection for real-time updates
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/api/ws/activity');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // Check if it's the backend telemetry schema
      if (data.event_type) {
        // Add all telemetry events to the Mission Control timeline
        setActivityStream(prev => [...prev, {
          time: new Date(data.timestamp || Date.now()).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
          event_type: data.event_type,
          uuid: data.execution_id
        }]);
        
        // If the execution failed or completed, update the execution plan statuses
        if (data.event_type === 'Execution Failed') {
          setExecutionPlan(prev => prev.map(t => t.status === 'Running' ? { ...t, status: 'Failed' } : t));
        } else if (data.event_type === 'Completed') {
          setExecutionPlan(prev => prev.map(t => t.status === 'Running' ? { ...t, status: 'Completed' } : t));
        }
      }
    };
    
    return () => ws.close();
  }, []);

  const handleApprove = async () => {
    setIsExecuting(true);
    setExecutionPlan(prev => prev.map(t => ({ ...t, status: 'Running' })));
    setActivityStream([{
      time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
      event_type: 'Executing...',
    }]);
    
    try {
      await fetch(`http://localhost:8000/api/execute/${currentSessionId}`, { method: 'POST', credentials: 'include' });
    } catch (e) {
      console.error(e);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleLogout = async () => {
    try {
      await fetch('http://localhost:8000/api/auth/logout', { method: 'POST', credentials: 'include' });
      window.location.href = '/login';
    } catch (e) {
      console.error(e);
    }
  };

  const handlePlanRequest = async () => {
    if (!input) return;
    const userMessage = input;
    setInput('');
    setHasStartedChat(true);
    setMessages(prev => [...prev, { id: Date.now(), role: 'user', text: userMessage }]);
    setIsPlanning(true);
    
    try {
      const response = await fetch('http://localhost:8000/api/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ user_id: 1, prompt: userMessage })
      });
      const data = await response.json();
      
      const plan = data.plan || {};
      
      setExecutionPlan(plan.tasks || []);
      setCurrentSessionId(data.session_id || 'sess_1_1');
      setExecutionGoal(plan.goal || '');
      setDependencies(plan.dependencies || []);
      setConfidence(plan.confidence || 96);
      setEstimatedDuration(plan.estimated_duration || '6 sec');
      
      setMessages(prev => [...prev, { 
        id: Date.now(), 
        role: 'assistant', 
        text: plan.message || `Execution Blueprint generated successfully. Please review and approve.` 
      }]);
    } catch (e) {
      console.error(e);
    } finally {
      setIsPlanning(false);
    }
  };
  
  // Group tasks by platform for the Blueprint view
  const groupedTasks = executionPlan.reduce((acc, task) => {
    const platform = task.platform || 'General';
    if (!acc[platform]) acc[platform] = [];
    acc[platform].push(task);
    return acc;
  }, {} as Record<string, any[]>);

  return (
    <div className="flex flex-col h-screen bg-[#0b0f19] text-gray-200 overflow-hidden font-sans selection:bg-indigo-500/30">
      
      {/* Top Bar (Enterprise Feel) */}
      <div className="h-12 border-b border-white/10 bg-white/5 flex items-center justify-between px-6 z-20">
        <div className="flex items-center gap-6">
          <h2 className="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-emerald-400 tracking-wide">
            ForgeOS
          </h2>
          <div className="h-4 w-px bg-white/20"></div>
          <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400">
            <ShieldCheck size={14} /> Workspace Healthy
          </div>
        </div>
        <div className="flex items-center gap-6 text-xs text-gray-400">
          <span className="font-semibold text-gray-300">2</span> Connected Platforms
          <div className="h-3 w-px bg-white/20"></div>
          <span className="font-semibold text-gray-300">18</span> Capabilities
          <div className="h-3 w-px bg-white/20"></div>
          <span>Last Sync: {new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
          <button onClick={handleLogout} className="flex items-center gap-2 hover:text-rose-400 transition-colors ml-4">
            <LogOut size={14} /> Logout
          </button>
        </div>
      </div>
      
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar - My Workspace */}
        <div className="w-72 border-r border-white/10 bg-white/5 flex flex-col relative z-10">
          <div className="p-6">
            <h3 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-4">
              My Workspace
            </h3>
            <div className="space-y-3">
              {connectedPlatforms.map((platform, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-xl border border-white/5 bg-white/5 cursor-default">
                  <div className="flex items-center gap-3">
                    <Box size={16} className="text-indigo-400" />
                    <span className="text-sm font-medium text-gray-200">{platform.name}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                    <span className="text-[10px] text-gray-400 uppercase tracking-wide">{platform.status}</span>
                  </div>
                </div>
              ))}
            </div>
            
            <button className="w-full mt-6 py-2 px-4 rounded-lg border border-dashed border-white/20 text-xs text-gray-400 hover:text-gray-200 hover:border-white/40 transition-colors">
              + Connect App
            </button>
          </div>
        </div>
        
        {/* Center - Dashboard / Chat / Execution */}
        <div className="flex-1 flex flex-col relative bg-gradient-to-br from-indigo-900/10 via-transparent to-emerald-900/10">
          <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none"></div>
          
          <div className="flex-1 overflow-y-auto p-8 relative z-10">
            {!hasStartedChat ? (
              <div className="max-w-4xl mx-auto mt-20">
                <h1 className="text-4xl font-light text-white mb-2">
                  Good Evening, <span className="font-semibold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-emerald-400">Vamsi.</span>
                </h1>
                <p className="text-xl text-gray-400 mb-12">Workspace Ready. What would you like to accomplish today?</p>
                
                <div className="grid grid-cols-2 gap-6 mb-12">
                  <div className="glass-panel p-6 border-white/5 hover:border-white/10 transition-colors">
                    <h3 className="text-sm font-semibold text-gray-300 mb-4 uppercase tracking-widest">Today's Workspace</h3>
                    <div className="flex gap-4">
                      <div className="px-3 py-1.5 rounded-md bg-white/5 border border-white/10 text-sm flex items-center gap-2">
                         <div className="w-2 h-2 rounded-full bg-emerald-500" /> Google Workspace
                      </div>
                      <div className="px-3 py-1.5 rounded-md bg-white/5 border border-white/10 text-sm flex items-center gap-2">
                         <div className="w-2 h-2 rounded-full bg-emerald-500" /> GitHub
                      </div>
                    </div>
                  </div>
                  <div className="glass-panel p-6 border-white/5 hover:border-white/10 transition-colors">
                    <h3 className="text-sm font-semibold text-gray-300 mb-4 uppercase tracking-widest">Recent Executions</h3>
                    <p className="text-sm text-gray-500">No pending approvals</p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="max-w-4xl mx-auto space-y-6">
                {messages.map(msg => (
                  <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[80%] rounded-2xl p-4 ${msg.role === 'user' ? 'bg-indigo-600 text-white' : 'glass-panel text-gray-200 shadow-lg shadow-black/20'}`}>
                      {msg.text}
                    </div>
                  </div>
                ))}
                
                {isPlanning && (
                  <div className="flex justify-start">
                    <div className="max-w-[80%] rounded-2xl p-4 glass-panel text-gray-400 shadow-lg flex items-center gap-2">
                      <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                      <span className="ml-2 font-medium text-sm">Processing intent...</span>
                    </div>
                  </div>
                )}
                
                {/* Hero Execution Blueprint */}
                {executionPlan.length > 0 && (
                <div className="glass-panel p-8 mt-8 border-indigo-500/30">
                  <div className="flex items-center justify-between mb-8">
                    <h3 className="text-2xl font-light text-white flex items-center gap-3">
                      Execution <span className="font-semibold text-indigo-400">Blueprint</span>
                    </h3>
                  </div>
                  
                  <div className="mb-8 border-l-2 border-indigo-500/50 pl-4">
                    <p className="text-xs text-indigo-300 uppercase tracking-widest font-semibold mb-1">Goal</p>
                    <p className="text-lg text-gray-200">{executionGoal}</p>
                  </div>
                  
                  <div className="space-y-6">
                    {Object.entries(groupedTasks).map(([platform, tasks]) => (
                      <div key={platform}>
                        <div className="flex items-center gap-4 mb-4">
                          <h4 className="text-sm font-bold text-gray-300 tracking-wide">{platform}</h4>
                          <div className="flex-1 h-px bg-white/10"></div>
                        </div>
                        <ul className="space-y-3 pl-2">
                          {tasks.map(task => (
                            <li key={task.id} className="flex items-center gap-3 text-gray-300">
                              <span className="text-indigo-400">•</span> 
                              <span>{task.action}</span>
                              {task.status === 'Completed' || task.status === 'Success' ? (
                                <CheckCircle size={14} className="text-emerald-500 ml-auto" />
                              ) : task.status === 'Failed' ? (
                                <XCircle size={14} className="text-rose-500 ml-auto" />
                              ) : task.status === 'Running' ? (
                                <Activity size={14} className="text-amber-500 ml-auto animate-pulse" />
                              ) : null}
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                  
                  <div className="mt-10 pt-6 border-t border-white/10 flex items-center justify-between">
                    <div className="flex gap-8">
                      <div>
                        <p className="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Estimated Duration</p>
                        <p className="text-sm font-medium text-gray-200">{estimatedDuration}</p>
                      </div>
                      <div>
                        <p className="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Confidence</p>
                        <p className="text-sm font-medium text-emerald-400">{confidence}%</p>
                      </div>
                      <div>
                        <p className="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Risk</p>
                        <p className="text-sm font-medium text-emerald-400">Low</p>
                      </div>
                    </div>
                    
                    <button 
                      onClick={handleApprove} 
                      disabled={isExecuting}
                      className="btn btn-primary shadow-[0_0_20px_rgba(99,102,241,0.4)] px-8 py-3 text-sm font-bold tracking-wide rounded-xl disabled:opacity-50 disabled:cursor-not-allowed">
                      {isExecuting ? 'Executing...' : 'Approve'}
                    </button>
                  </div>
                </div>
                )}
              </div>
            )}
          </div>
          
          {/* Input Area */}
          <div className="p-6 border-t border-white/10 bg-[#0b0f19]/80 backdrop-blur-md relative z-10">
            <div className="max-w-4xl mx-auto relative">
              <input 
                type="text" 
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handlePlanRequest()}
                disabled={isPlanning}
                placeholder={isPlanning ? "Planning execution..." : "E.g., Create a new GitHub repository called ForgeOS Demo and add a README..."}
                className="w-full bg-white/5 border border-white/10 rounded-xl py-4 pl-4 pr-12 text-gray-200 focus:outline-none focus:border-indigo-500 transition-colors placeholder:text-gray-600 shadow-inner shadow-black/20 disabled:opacity-50"
              />
              <button onClick={handlePlanRequest} disabled={isPlanning} className="absolute right-3 top-1/2 -translate-y-1/2 text-indigo-400 hover:text-indigo-300 p-2 disabled:opacity-50">
                <MessageSquare size={20} />
              </button>
            </div>
          </div>
        </div>
        
        {/* Right Sidebar - Mission Control */}
        {activityStream.length > 0 && (
          <div className="w-80 border-l border-white/10 bg-white/5 flex flex-col z-10">
            <div className="p-6 border-b border-white/10">
              <h3 className="text-sm font-bold text-gray-200 tracking-wide flex items-center gap-2">
                <Activity size={16} className="text-emerald-400" /> Mission Control
              </h3>
            </div>
            <div className="p-6 flex-1 overflow-y-auto space-y-6 relative">
              
              {activityStream.map((activity, i) => (
                <div key={i} className="flex gap-4 relative group">
                  <div className="flex flex-col items-center gap-1 w-12 shrink-0">
                    <span className="text-[10px] text-gray-500 font-mono">{activity.time}</span>
                  </div>
                  <div className="flex-1 flex items-center justify-between">
                    <span className={`text-sm font-medium ${activity.event_type.includes('Failed') || activity.event_type.includes('Error') ? 'text-rose-400' : 'text-gray-300'}`}>
                      {activity.event_type}
                    </span>
                    {activity.event_type.includes('Failed') || activity.event_type.includes('Error') ? (
                      <XCircle size={14} className="text-rose-500" />
                    ) : (
                      <CheckCircle size={14} className="text-emerald-500" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
