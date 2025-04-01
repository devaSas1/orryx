import { useState } from "react";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = input;
    setMessages([...messages, { role: "user", text: userMsg }]);
    setInput("");

    const res = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userMsg }),
    });

    const data = await res.json();
    setMessages((prev) => [...prev, { role: "bot", text: data.reply }]);
  };

  return (
    <div className="App">
      <h1>Talk to Orryx 🦉</h1>
      <div className="chat-box">
        {messages.map((msg, i) => (
          <div key={i} className={`msg ${msg.role}`}>
            <strong>{msg.role === "user" ? "You" : "Orryx"}:</strong> {msg.text}
          </div>
        ))}
      </div>
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        placeholder="Ask me anything about Poway..."
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}

export default App;
