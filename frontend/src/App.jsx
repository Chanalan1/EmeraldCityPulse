import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [data, setData] = useState(null)

  useEffect(() => {
    // We call the full URL for now to be safe
    fetch('http://127.0.0.1:5000/api/time')
      .then((res) => res.json())
      .then((data) => {
        setData(data)
        console.log("Data received:", data)
      })
      .catch((err) => console.error("Error fetching:", err))
  }, [])

  return (
    <div className="App">
      <h1>EmeraldCityPulse Connection Test</h1>
      <div className="card">
        {data ? (
          <div>
            <p>Backend Status: Connected!</p>
            <p><strong>Message:</strong> {data.message}</p>
            <p><strong>Server Time:</strong> {data.time}</p>
          </div>
        ) : (
          <p> Connecting to backend...</p>
        )}
      </div>
    </div>
  )
}

export default App