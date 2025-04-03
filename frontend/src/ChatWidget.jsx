import { useState } from 'react'
import './ChatWidget.css'
import powayLogo from './assets/poway-logo.png'

function ChatWidget() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [isOpen, setIsOpen] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMsg = { sender: 'user', text: input }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      })
      const data = await res.json()
      const botMsg = { sender: 'orryx', text: data.reply }
      setMessages(prev => [...prev, botMsg])
    } catch (err) {
      console.error('Error:', err)
      setMessages(prev => [...prev, { sender: 'orryx', text: "Something broke. Blame the dev." }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="orryx-widget-container">
      <button className="orryx-toggle-button" onClick={() => setIsOpen(!isOpen)}>
        💬
      </button>

      {isOpen && (
        <div className="orryx-widget-window">
          <img src={powayLogo} alt="Poway Chamber" className="logo" />
          <h1 className="title">Orryx</h1>
          <div className="chat-box">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.sender}`}>
                <strong>{msg.sender === 'user' ? 'You' : 'Orryx'}:</strong> {msg.text}
              </div>
            ))}
            {loading && <div className="message orryx">Orryx is thinking...</div>}
          </div>
          <form onSubmit={handleSubmit} className="input-form">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask me something..."
            />
            <button type="submit">Send</button>
          </form>
        </div>
      )}
    </div>
  )
}

export default ChatWidget
