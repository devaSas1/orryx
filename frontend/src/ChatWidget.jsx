import { useState, useEffect } from 'react' // ✅ NEW: useEffect for prompt bubble
import './ChatWidget.css'

function linkify(text) {
    const urlRegex = /https?:\/\/[^\s<>()]+/g;
  
    return text.split(urlRegex).map((part, i, arr) => {
      if (i === arr.length - 1) return part;
  
      const match = text.match(urlRegex)[i];
      
      // Remove trailing punctuation if present
      const trimmedURL = match.replace(/[.,!?)]*$/, '');
      const trailing = match.slice(trimmedURL.length); // Save what's removed
  
      return (
        <span key={i}>
          {part}
          <a href={trimmedURL} target="_blank" rel="noopener noreferrer" className="chat-link">
            {trimmedURL}
          </a>
          {trailing}
        </span>
      );
    });
  }
  
  
  function ChatWidget({ client }) {
  const clientId = client.apiPath  
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [isOpen, setIsOpen] = useState(false)
  const [showPrompt, setShowPrompt] = useState(true) // ✅ NEW: Control prompt visibility

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowPrompt(false) // ✅ NEW: Hide prompt after 5s
    }, 5000)

    return () => clearTimeout(timer) // ✅ NEW: Cleanup
  }, [])

// ✅ Smarter greeting on open
useEffect(() => {
    if (isOpen && messages.length === 0) {
      const hour = new Date().getHours()
      let greetingOptions = []
  
      if (hour >= 5 && hour < 11) {
        greetingOptions = [
          "Good morning! ☀️ How can I help you today?",
          "Hey there! Bright and early, huh? Let’s get to it.",
          "Top of the mornin’ to ya! Need help with something?"
        ]
      } else if (hour >= 11 && hour < 17) {
        greetingOptions = [
          "Good afternoon! How can I assist?",
          "Midday grind? I got your back 💪",
          "Hope your day’s going smooth—what do you need help with?"
        ]
      } else if (hour >= 17 && hour < 22) {
        greetingOptions = [
          "Evening vibes detected 🌇 How can I help?",
          "Hey hey! Burning that post-5pm oil? I'm here for it.",
          "Let’s wrap up your day strong—how can I help?"
        ]
      } else {
        greetingOptions = [
          "Late night session huh? Let’s make it count 🌙",
          "I'm up too. What can I help you with?",
          "Working the graveyard shift? Respect. Ask away."
        ]
      }
  
      const randomGreeting = greetingOptions[Math.floor(Math.random() * greetingOptions.length)]
      setMessages([{ sender: 'orryx', text: randomGreeting }])
    }
  }, [isOpen])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMsg = { sender: 'user', text: input }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await fetch(`http://127.0.0.1:8000/chat/${clientId}`, {

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

      {/* ✅ NEW: Prompt bubble */}
      {showPrompt && !isOpen && (
        <div className="orryx-prompt-bubble">
          💡 Talk with our AI Assistant to navigate the website faster!
        </div>
      )}

      <button className="orryx-toggle-button" onClick={() => setIsOpen(!isOpen)}>
        💬
      </button>

      {isOpen && (
        <div className="orryx-widget-window"style={{ borderColor: client.primaryColor }}>
          <img src={client.logo} alt={client.name} className="logo" />
          <h1 className="title"></h1>
          <div className="chat-box">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.sender}`}>
                <strong>{msg.sender === 'user' ? 'You' : 'Orryx'}:</strong> {linkify(msg.text)} {/* ✅ NEW: Make URLs clickable */}
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
