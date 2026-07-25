import { useState, useRef, useEffect } from 'react'
import { GoogleLogin } from '@react-oauth/google'
import { Send, Mic, User as UserIcon, Calendar, MessageSquare, Phone } from 'lucide-react'
import axios from 'axios'
import './App.css'

interface Message {
  role: 'user' | 'ai'
  content: string
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState<any>(null)
  
  const [messages, setMessages] = useState<Message[]>([
    { role: 'ai', content: 'Hi there! I am your AI Restaurant Agent. Where would you like to book a table today?' }
  ])
  const [input, setInput] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  
  const chatEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleLoginSuccess = (credentialResponse: any) => {
    // In a real app, send credentialResponse to FastAPI backend
    console.log(credentialResponse)
    setUser({ name: "Demo User", email: "demo@gmail.com" })
    setIsAuthenticated(true)
  }

  const handleSend = async () => {
    if (!input.trim()) return
    
    // Add user message to UI
    const newMessages: Message[] = [...messages, { role: 'user', content: input }]
    setMessages(newMessages)
    setInput('')
    
    try {
      // Call our FastAPI LangGraph endpoint
      const response = await axios.post('http://localhost:8000/api/agent/chat', {
        user_input: input
      })
      
      let aiResponse = response.data.general_response || "I am processing that for you."
      
      if (response.data.intent === 'book_table') {
        if (response.data.is_ready_to_call) {
          aiResponse = `Perfect. I have all the details. I will now call ${response.data.restaurant_name} to secure your table for ${response.data.guest_count} guests on ${response.data.date} at ${response.data.time}.`
        } else if (response.data.errors.length > 0) {
          aiResponse = response.data.errors[0] // e.g., "Missing time."
        }
      }
      
      setMessages(prev => [...prev, { role: 'ai', content: aiResponse }])
      
    } catch (error) {
      console.error(error)
      setMessages(prev => [...prev, { role: 'ai', content: 'Sorry, my server is currently offline.' }])
    }
  }

  const toggleRecording = () => {
    setIsRecording(!isRecording)
    // Here we would integrate actual MediaRecorder API to capture audio 
    // and send it via WebSocket to OpenAI Realtime API.
  }

  if (!isAuthenticated) {
    return (
      <div className="app-container">
        <div className="glass-panel" style={{ padding: '40px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px' }}>
          <h2>AI Restaurant Agent</h2>
          <p style={{ color: 'var(--text-muted)' }}>Please log in to continue</p>
          <GoogleLogin
            onSuccess={handleLoginSuccess}
            onError={() => console.log('Login Failed')}
          />
          <button 
            className="btn" 
            style={{ marginTop: '10px', fontSize: '0.9rem', color: 'var(--text-muted)' }}
            onClick={() => handleLoginSuccess({ mock: true })}
          >
            Bypass Login (Dev Mode)
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="app-container">
      <div className="glass-panel main-dashboard">
        
        {/* Sidebar */}
        <div className="sidebar">
          <div className="brand">AI Concierge</div>
          
          <div className="nav-links">
            <div className="nav-item active">
              <MessageSquare size={20} style={{ display: 'inline', marginRight: '8px', verticalAlign: 'middle' }} />
              Chat Booking
            </div>
            <div className="nav-item">
              <Calendar size={20} style={{ display: 'inline', marginRight: '8px', verticalAlign: 'middle' }} />
              My Reservations
            </div>
            <div className="nav-item">
              <Phone size={20} style={{ display: 'inline', marginRight: '8px', verticalAlign: 'middle' }} />
              Call Logs
            </div>
          </div>
          
          <div className="user-profile">
            <div className="avatar">
              <UserIcon size={20} />
            </div>
            <div>
              <div style={{ fontWeight: 500 }}>{user?.name}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{user?.email}</div>
            </div>
          </div>
        </div>

        {/* Chat Area */}
        <div className="chat-container">
          <div className="chat-header">
            <h2>New Reservation</h2>
            <p>I can help you book a table anywhere using Google Places.</p>
          </div>
          
          <div className="chat-messages">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}`}>
                {msg.content}
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>
          
          <div className="chat-input-area">
            <input 
              type="text" 
              placeholder="Ask me to book a table..." 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            />
            
            <button 
              className={`mic-btn ${isRecording ? 'recording' : ''}`}
              onClick={toggleRecording}
              title="Hold to speak"
            >
              <Mic size={24} />
            </button>
            
            <button className="btn btn-primary send-btn" onClick={handleSend}>
              <Send size={20} />
            </button>
          </div>
        </div>

      </div>
    </div>
  )
}

export default App
