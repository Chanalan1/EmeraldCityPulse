import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// dynamic usage of map after searching
function RecenterMap({ coords }) {
    const map = useMap();
    if (coords) map.setView(coords, 14);
    return null;
}

// Helper to determine color based on crime category
const getMarkerStyle = (type) => {
    const t = type.toLowerCase();
    if (t.includes('assault') || t.includes('homicide') || t.includes('weapon') || t.includes('robbery')) {
        return { color: '#ff4444', label: 'Violent/Danger' }; // Red
    }
    if (t.includes('theft') || t.includes('burglary') || t.includes('stolen') || t.includes('property')) {
        return { color: '#ffbb33', label: 'Property/Theft' }; // Yellow
    }
    return { color: '#0099CC', label: 'Other/Proactive' }; // Blue
};

const CrimeMap = ({ incidents, center }) => {
    return (
        <div style={{ 
            height: '400px', 
            width: '100%', 
            borderRadius: '12px', 
            overflow: 'hidden', 
            marginBottom: '20px',
            border: '1px solid #444',
            position: 'relative' // Needed to position the legend
        }}>
            {/* --- 🗺️ THE MAP LEGEND --- */}
            <div style={{
                position: 'absolute',
                bottom: '20px',
                right: '10px',
                backgroundColor: 'rgba(0,0,0,0.8)',
                padding: '10px',
                borderRadius: '8px',
                zIndex: 1000, // Stay on top of the map
                fontSize: '0.8rem',
                border: '1px solid #555',
                color: 'white'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
                    <div style={{ width: '12px', height: '12px', backgroundColor: '#ff4444', borderRadius: '50%', marginRight: '8px' }}></div>
                    <span>Violent Crimes</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
                    <div style={{ width: '12px', height: '12px', backgroundColor: '#ffbb33', borderRadius: '50%', marginRight: '8px' }}></div>
                    <span>Property Crimes</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                    <div style={{ width: '12px', height: '12px', backgroundColor: '#0099CC', borderRadius: '50%', marginRight: '8px' }}></div>
                    <span>Other Incidents</span>
                </div>
            </div>

            <MapContainer center={center} zoom={13} style={{ height: '100%', width: '100%' }}>
                <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; OpenStreetMap contributors'
                />
                <RecenterMap coords={center} />
                
                {incidents.map((incident, idx) => {
                    const style = getMarkerStyle(incident.type);
                    
                    return (
                        <CircleMarker 
                            key={idx} 
                            center={incident.coords} 
                            radius={8}
                            pathOptions={{ 
                                color: style.color, 
                                fillColor: style.color, 
                                fillOpacity: 0.6,
                                weight: 2 
                            }}
                        >
                            <Popup>
                                <div style={{ color: '#333' }}>
                                    <strong style={{ fontSize: '1.1rem' }}>{incident.type}</strong><br />
                                    <span>{incident.distance}</span>
                                </div>
                            </Popup>
                        </CircleMarker>
                    );
                })}
            </MapContainer>
        </div>
    );
};

export default CrimeMap;