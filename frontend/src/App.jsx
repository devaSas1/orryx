import { useState } from 'react'
import './App.css'
import ChatWidget from './ChatWidget' // ✅ NEW: Bring in your widget
import { CLIENTS } from './clientConfigs'


function App() {
  const [selectedClient, setSelectedClient] = useState("poway") // default
  return (
    <div className="app">
      <h1>Orryx Multi-Client Chatbot</h1>
      <select onChange={(e) => setSelectedClient(e.target.value)} value={selectedClient}>
        {Object.keys(CLIENTS).map((client) => (
          <option key={client} value={client}>
            {CLIENTS[client].name}
          </option>
        ))}
      </select>

      <ChatWidget client={CLIENTS[selectedClient]} />
    </div>
  )
}

export default App
