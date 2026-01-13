import { useState } from 'react'

function App() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (address) => {
    setLoading(true);
    setError(null);

    try {
      // 1. Send the request to your Flask backend
      const response = await fetch(`http://127.0.0.1:5000/api/search?address=${encodeURIComponent(address)}`);
      
      // 2. Check if the server responded okay
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      // 3. Parse the JSON
      const data = await response.json();

      if (data.status === "success") {
        setReports(data.reports);
      } else {
        setError(data.message || "No results found.");
      }
    } catch (err) {
      setError("Failed to connect to the server.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>Emerald City Pulse</h1>
      <p>Real-time Seattle Crime Data by Proximity</p>
  
      <div style={{ display: 'flex', gap: '10px', marginBottom: '30px' }}>
        <input 
          type="text" 
          placeholder="Enter a Seattle address (e.g. 400 Broad St)"
          id="addressInput"
          style={{ flex: 1, padding: '10px', borderRadius: '4px', border: '1px solid #ddd' }}
        />
        <button 
          onClick={() => {
            const val = document.getElementById('addressInput').value;
            handleSearch(val);
          }}
          style={{ padding: '10px 20px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>
  
      {error && <div style={{ color: 'red', marginBottom: '20px' }}>⚠️ {error}</div>}
  
      <div className="results-list">
        {reports.map((report, index) => (
          <div key={index} style={{ 
            padding: '15px', 
            borderBottom: '1px solid #eee', 
            display: 'flex', 
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <div>
              <h3 style={{ margin: '0 0 5px 0', fontSize: '1.1rem' }}>{report.type}</h3>
              <span style={{ color: '#666', fontSize: '0.9rem' }}>{report.date}</span>
            </div>
            <div style={{ fontWeight: 'bold', color: '#28a745' }}>
              {report.distance}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
        }
export default App