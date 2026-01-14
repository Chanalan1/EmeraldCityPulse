import { useState } from 'react'
import CrimeMap from './components/CrimeMap';

function App() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [mapCenter, setMapCenter] = useState([47.6062, -122.3321]);
  
  // New states for filtering
  const [radius, setRadius] = useState(1000);
  const [timeRange, setTimeRange] = useState('1y');

  const handleSearch = async (address) => {
    if (!address) return;
    setLoading(true);
    setError(null);

    try {
      // 1. Send request with dynamic radius and time parameters
      const url = `http://127.0.0.1:5000/api/search?address=${encodeURIComponent(address)}&radius=${radius}&time_range=${timeRange}`;
      const response = await fetch(url);
      
      // 2. Check if the server responded okay
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();

      if (data.status === "success") {
        setReports(data.reports);
        
        // --- 🗺️ UPDATE MAP CENTER ---
        if (data.metadata && data.metadata.lat && data.metadata.lon) {
          setMapCenter([data.metadata.lat, data.metadata.lon]);
        }
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
    <div style={{ width: '100vw', display: 'flex', flexDirection: 'column', alignItems: 'center', backgroundColor: '#242424', minHeight: '100vh', color: 'white' }}>
      
      <div style={{ width: '100%', maxWidth: '800px', padding: '40px 20px', boxSizing: 'border-box' }}>
        
        <h1 style={{ textAlign: 'center', fontSize: '3rem', marginBottom: '10px' }}>Emerald City Pulse</h1>
        <p style={{ textAlign: 'center', color: '#ccc', marginBottom: '30px' }}>Real-time Seattle Crime Data by Proximity</p>
        <p style={{ textAlign: 'center', color: '#ccc', marginBottom: '15px' }}>Warning: When searching high density neighborhoods (ex:downtown), you might get timed out due to how dense reports are, please specify the specific address or broadent search for faster results if you are timed out!</p>

        <div style={{ backgroundColor: '#1a1a1a', padding: '20px', borderRadius: '12px', border: '1px solid #333', marginBottom: '30px' }}>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
            <input 
              type="text" 
              placeholder="Enter a Seattle address (e.g. 400 Broad St)"
              id="addressInput"
              onKeyDown={(e) => e.key === 'Enter' && handleSearch(e.target.value)}
              style={{ 
                flex: 1, 
                padding: '12px', 
                borderRadius: '8px', 
                border: '1px solid #444',
                backgroundColor: '#242424',
                color: 'white'
              }}
            />
            <button 
              onClick={() => {
                const val = document.getElementById('addressInput').value;
                handleSearch(val);
              }}
              style={{ 
                padding: '10px 25px', 
                backgroundColor: '#007bff', 
                color: 'white', 
                border: 'none', 
                borderRadius: '8px', 
                cursor: 'pointer',
                fontWeight: 'bold'
              }}
            >
              {loading ? '...' : 'Search'}
            </button>
          </div>

          {/* Filter Controls */}
          <div style={{ display: 'flex', gap: '20px', fontSize: '0.9rem' }}>
            <div style={{ flex: 1 }}>
              <label style={{ display: 'block', marginBottom: '8px', color: '#888' }}>
                Radius: <span style={{ color: '#007bff', fontWeight: 'bold' }}>{radius}m</span>
              </label>
              <input 
                type="range" min="250" max="1000" step="250" 
                value={radius} 
                onChange={(e) => setRadius(e.target.value)}
                style={{ width: '100%', accentColor: '#007bff' }}
              />
            </div>
            <div style={{ flex: 1 }}>
              <label style={{ display: 'block', marginBottom: '8px', color: '#888' }}>Timeframe:</label>
              <select 
                value={timeRange} 
                onChange={(e) => setTimeRange(e.target.value)}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', backgroundColor: '#242424', color: 'white', border: '1px solid #444' }}
              >
                <option value="1w">Past Week</option>
                <option value="2w">Past Two Week</option>
                <option value="1m">Past Month</option>
                <option value="3m">Past 3 Months</option>
                <option value="6m">Past 6 Months</option>
                <option value="1y">Past Year</option>
                <option value="3y">Past 3 Years</option>
              </select>
            </div>
          </div>
        </div>
    
        {error && <div style={{ color: '#ff4444', marginBottom: '20px', textAlign: 'center' }}>⚠️ {error}</div>}

        <CrimeMap incidents={reports} center={mapCenter} />
    
        <div className="results-list" style={{ marginTop: '20px' }}>
          {reports.length === 0 && !loading && !error && (
              <p style={{ textAlign: 'center', color: '#888' }}>Adjust filters and search an address to see incidents.</p>
          )}

          {reports.map((report, index) => (
            <div key={index} style={{ 
              padding: '20px 0', 
              borderBottom: '1px solid #333', 
              display: 'flex', 
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div>
                <h3 style={{ margin: '0 0 5px 0', fontSize: '1.1rem', textTransform: 'uppercase' }}>{report.type}</h3>
                <span style={{ color: '#888', fontSize: '0.9rem' }}>{report.date}</span>
              </div>
              <div style={{ fontWeight: 'bold', color: '#28a745', fontSize: '1.2rem' }}>
                {report.distance}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;