import React, { useState } from 'react'
import { Send, CheckCircle2, Circle, Code, FileText, Calendar, Inbox, ShieldAlert } from 'lucide-react'

// Demo data
const CONNECTED_PLATFORMS = [
  { id: 'google', name: 'Google', connected: true },
  { id: 'github', name: 'GitHub', connected: true },
  { id: 'slack', name: 'Slack', connected: false },
  { id: 'notion', name: 'Notion', connected: true },
]

type Message = {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  isApprovalRequest?: boolean;
  plan?: { tool: string; action: string }[];
}

export default function Workspace() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    const newMsg: Message = { id: Date.now(), role: 'user', content: input }
    setMessages([...messages, newMsg])
    setInput('')

    // Mock AI response demonstrating dynamic tools & approval
    setTimeout(() => {
      if (input.toLowerCase().includes('startup')) {
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          role: 'assistant',
          content: 'I will create the GitHub repository and Google documentation. Since Slack is not connected, I will notify the team via Gmail. Please approve this plan:',
          isApprovalRequest: true,
          plan: [
            { tool: 'GitHub', action: 'Create Repository: Velora' },
            { tool: 'Google Docs', action: 'Create Doc: Setup Guide' },
            { tool: 'Gmail', action: 'Email team updates' }
          ]
        }])
      } else {
        setMessages(prev => [...prev, {
          id: Date.now() + 1,
          role: 'assistant',
          content: 'I can help you with that using your connected tools.'
        }])
      }
    }, 1000)
  }

  const handleApprove = () => {
    setMessages(prev => [...prev, {
      id: Date.now(),
      role: 'assistant',
      content: 'Executing plan... ✅ Done.'
    }])
  }

  return (
    <div style={{ display: 'flex', height: '100vh', padding: '20px', gap: '20px' }}>
      
      {/* Sidebar */}
      <div className="glass-panel" style={{ width: '280px', display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: '24px', borderBottom: '1px solid var(--panel-border)' }}>
          <h2 style={{ fontSize: '20px', fontWeight: 600 }}>ForgeOS</h2>
        </div>
        
        <div style={{ padding: '24px', flex: 1 }}>
          <h3 style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '16px', letterSpacing: '1px' }}>
            Connected Platforms
          </h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {CONNECTED_PLATFORMS.map(platform => (
              <div key={platform.id} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                {platform.connected ? (
                  <CheckCircle2 size={18} color="var(--success-color)" />
                ) : (
                  <Circle size={18} color="var(--text-muted)" />
                )}
                <span style={{ color: platform.connected ? 'var(--text-main)' : 'var(--text-muted)' }}>
                  {platform.name}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="glass-panel animate-fade-in" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <div style={{ padding: '24px', borderBottom: '1px solid var(--panel-border)' }}>
          <h2 style={{ fontSize: '18px', fontWeight: 500 }}>AI Workspace</h2>
        </div>

        <div style={{ flex: 1, padding: '24px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {messages.length === 0 ? (
            <div style={{ margin: 'auto', textAlign: 'center', color: 'var(--text-muted)' }}>
              <p>Type a request to begin.</p>
              <p style={{ fontSize: '14px', marginTop: '8px' }}>Example: "Create new startup"</p>
            </div>
          ) : (
            messages.map(msg => (
              <div key={msg.id} style={{ 
                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '80%'
              }}>
                <div style={{
                  background: msg.role === 'user' ? 'var(--primary-accent)' : 'rgba(255,255,255,0.05)',
                  padding: '16px 20px',
                  borderRadius: '12px',
                  border: msg.role === 'assistant' ? '1px solid var(--panel-border)' : 'none'
                }}>
                  <p style={{ lineHeight: '1.5' }}>{msg.content}</p>
                  
                  {msg.isApprovalRequest && msg.plan && (
                    <div style={{ marginTop: '16px', background: 'rgba(0,0,0,0.2)', padding: '16px', borderRadius: '8px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', color: '#fbbf24' }}>
                        <ShieldAlert size={18} />
                        <strong>Execution Plan Approval</strong>
                      </div>
                      <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px' }}>
                        {msg.plan.map((item, idx) => (
                          <li key={idx} style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px dashed var(--panel-border)', paddingBottom: '8px' }}>
                            <span style={{ color: 'var(--text-muted)' }}>{item.tool}</span>
                            <span>{item.action}</span>
                          </li>
                        ))}
                      </ul>
                      <div style={{ display: 'flex', gap: '12px' }}>
                        <button onClick={handleApprove} className="btn btn-primary" style={{ background: 'var(--success-color)' }}>Approve & Execute</button>
                        <button className="btn btn-secondary">Cancel</button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        <div style={{ padding: '24px', borderTop: '1px solid var(--panel-border)' }}>
          <form onSubmit={handleSend} style={{ display: 'flex', gap: '12px' }}>
            <input 
              type="text" 
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Tell ForgeOS what to do..."
              style={{
                flex: 1,
                background: 'rgba(0,0,0,0.2)',
                border: '1px solid var(--panel-border)',
                borderRadius: '8px',
                padding: '16px',
                color: 'white',
                fontFamily: 'inherit',
                fontSize: '15px',
                outline: 'none'
              }}
            />
            <button type="submit" className="btn btn-primary" style={{ padding: '0 24px' }}>
              <Send size={20} />
            </button>
          </form>
        </div>
      </div>

    </div>
  )
}
