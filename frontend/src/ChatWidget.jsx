import { useState, useEffect } from 'react'
import './ChatWidget.css'
import orryxLogo from './assets/orryx-logo.png'

function linkify(text) {
  const urlRegex = /https?:\/\/[^\s<>()]+/g;

  return text.split(urlRegex).map((part, i, arr) => {
    if (i === arr.length - 1) return part;

    const match = text.match(urlRegex)[i];
    const trimmedURL = match.replace(/[.,!?)]*$/, '');
    const trailing = match.slice(trimmedURL.length);

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
  const [showPrompt, setShowPrompt] = useState(true)
  const [chatSplashVisible, setChatSplashVisible] = useState(false) // ✅ NEW: splash inside chat

  useEffect(() => {
    const timer = setTimeout(() => setShowPrompt(false), 5000)
    return () => clearTimeout(timer)
  }, [])

  const handleToggle = () => {
    if (!isOpen) {
      setIsOpen(true)
      setChatSplashVisible(true)
      setTimeout(() => setChatSplashVisible(false), 2500)
    } else {
      setIsOpen(false)
    }
  }
  // 🆕 [REPORT FEATURE] report handler
  const handleReport = async (userMessage, botReply) => {
    const comment = prompt("Optional: Add a note about what went wrong.")
    const reportData = {
        user_message: userMessage,
        bot_reply: botReply,
        comment: comment || ""
      }
      
    try {
        await fetch(`http://127.0.0.1:8000/report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reportData)
      })
      alert("Report submitted. We'll review it shortly.")
    } catch (err) {
      console.error("Failed to send report:", err)
      alert("Something went wrong. Try again later.")
    }
  }


  // Smart greeting
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
      {showPrompt && !isOpen && (
        <div className="orryx-prompt-bubble">
          💡 Talk with our AI Assistant to navigate the website faster!
        </div>
      )}

      <button className="orryx-toggle-button" onClick={handleToggle}>
        💬
      </button>

      {isOpen && (
        <div className="orryx-widget-window" style={{ borderColor: 'transparent' }}>
          {chatSplashVisible ? (
            <div className="chat-splash">
              <img src={orryxLogo} alt="Orryx Logo" className="splash-logo" />
              <p className="splash-text">Initializing Orryx</p>
              <div className="orryx-footer">
                Powered by <span className="orryx-brand">Orryx</span>
              </div>
            </div>
          ) : (
            <>
              <img src={client.logo} alt={client.name} className="logo" />
              <div className="chat-box">
                {messages.map((msg, idx) => (
                  <div key={idx} className={`message ${msg.sender}`}>
                    <strong>{msg.sender === 'user' ? 'You' : 'Orryx'}:</strong> {linkify(msg.text)}
                    {/* 🆕 [REPORT FEATURE] button for bot messages */}
                    {msg.sender === 'orryx' && idx > 0 && (
                      <button
                        className="report-button"
                        onClick={() => handleReport(messages[idx - 1]?.text, msg.text)}
                      >
                        ⚠️ Report
                      </button>
                    )}
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

              <div className="orryx-footer">
                Powered by <span className="orryx-brand">Orryx</span>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  )
}

export default ChatWidget
