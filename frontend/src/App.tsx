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
  const [bookingContext, setBookingContext] = useState<any>({})
  
  const chatEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleLoginSuccess = (credentialResponse: any) => {
    console.log(credentialResponse)
    if (credentialResponse?.credential) {
      try {
        const base64Url = credentialResponse.credential.split('.')[1]
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
        const jsonPayload = decodeURIComponent(
          atob(base64)
            .split('')
            .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
            .join('')
        )
        const payload = JSON.parse(jsonPayload)
        setUser({
          name: payload.name || "Google User",
          email: payload.email || "user@gmail.com"
        })
      } catch (err) {
        console.error("Failed to decode token", err)
        setUser({ name: "Google User", email: "user@gmail.com" })
      }
    } else {
      setUser({ name: "Demo User", email: "demo@gmail.com" })
    }
    setIsAuthenticated(true)
  }

  const handleSend = async () => {
    if (!input.trim()) return
    
    // Add user message to UI
    const newMessages: Message[] = [...messages, { role: 'user', content: input }]
    setMessages(newMessages)
    const userText = input
    setInput('')
    
    try {
      // Call our FastAPI LangGraph endpoint with accumulated context
      const response = await axios.post('http://localhost:8000/api/agent/chat', {
        user_input: userText,
        current_state: bookingContext
      })
      
      let aiResponse = response.data.general_response || "I am processing that for you."
      
      if (response.data.intent === 'book_table') {
        if (response.data.is_ready_to_call) {
          const restName = response.data.restaurant_name || "the restaurant"
          const guests = response.data.guest_count || 2
          const date = response.data.date || "tomorrow"
          const time = response.data.time || "the scheduled time"
          
          if (!response.data.call_initiated && response.data.call_status_message) {
            aiResponse = `Perfect, I have all the details for ${restName} (${guests} guests on ${date} at ${time}). However, the call cannot be initiated because the Voice Call API is not working or not configured.`
          } else {
            aiResponse = `Perfect. I have all the details. I will now call ${restName} to secure your table for ${guests} guests on ${date} at ${time}.`
          }
          // Clear booking context on completion
          setBookingContext({})
        } else {
          // Accumulate updated booking context
          setBookingContext((prev: any) => ({
            ...prev,
            restaurant_name: response.data.restaurant_name || prev.restaurant_name,
            date: response.data.date || prev.date,
            time: response.data.time || prev.time,
            guest_count: response.data.guest_count || prev.guest_count,
            place_id: response.data.restaurant_details?.place_id || prev.place_id,
            restaurant_details: response.data.restaurant_details || prev.restaurant_details
          }))
          
          if (response.data.errors.length > 0) {
            aiResponse = response.data.errors[0]
          }
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
