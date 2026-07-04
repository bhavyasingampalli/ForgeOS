import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Rocket } from 'lucide-react'

export const Login = () => {
  const navigate = useNavigate()

  const [isLoading, setIsLoading] = React.useState(false)

  const handleLogin = () => {
    setIsLoading(true)
    // Directly navigate to backend signin which redirects to Google OAuth
    window.location.href = 'http://localhost:8000/api/auth/signin'
  }

  return (
    <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div className="glass-panel animate-fade-in" style={{ padding: '40px', width: '400px', textAlign: 'center' }}>
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '20px' }}>
          <Rocket size={48} color="var(--primary-accent)" />
        </div>
        <h1 style={{ marginBottom: '8px', fontSize: '24px' }}>ForgeOS</h1>
        <p style={{ color: 'var(--text-muted)', marginBottom: '32px', fontSize: '14px' }}>
          AI Engineering Chief of Staff
        </p>
        
        <button onClick={handleLogin} disabled={isLoading} className="btn btn-primary" style={{ width: '100%', padding: '12px' }}>
          {isLoading ? 'Authenticating...' : 'Sign In to Continue'}
        </button>
      </div>
    </div>
  )
}
