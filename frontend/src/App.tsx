import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './pages/Login';
import { WorkspaceIntegrations } from './pages/WorkspaceIntegrations';
import { MCPExplorer } from './pages/MCPExplorer';
import { CommandCenter } from './pages/CommandCenter';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/connections" element={<Navigate to="/integrations" replace />} />
        <Route path="/integrations" element={<WorkspaceIntegrations />} />
        <Route path="/explorer" element={<MCPExplorer />} />
        <Route path="/command-center" element={<CommandCenter />} />
        <Route path="/workspace" element={<Navigate to="/command-center" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
