import './App.css'
import ChatWidget from './ChatWidget' // ✅ NEW: Bring in your widget

function App() {
  return (
    <div className="app">
      <h1>Welcome to the Poway Chamber</h1>
      <p>This is the main site content. Scroll, click, explore — but if you need help, Orryx is here 👉</p>

      <ChatWidget /> {/* ✅ Floating widget rendered here */}
    </div>
  )
}

export default App
