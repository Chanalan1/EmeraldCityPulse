# Emerald City Pulse
**Real-time geospatial crime analytics for the city of Seattle.**

Emerald City Pulse is a full-stack web application that allows users to monitor public safety incidents in Seattle by proximity. By combining real-time data from the Seattle Police Department with interactive mapping, the platform provides hyper-local insights into neighborhood safety.

## Features
- **Proximity-Based Search:** Search any Seattle address to find incidents within a custom radius (250m - 5km).
- **Interactive Mapping:** Color-coded markers categorize incidents by severity (Violent, Property, Other).
- **Historical Analysis:** Filter data from the past week up to the past three years.
- **Privacy-Preserving Data:** Displays incident block-locations and proximity while respecting victim privacy.
- **Resilient Backend:** Implements robust error handling and optimized sorting for deep-history data requests.

## Project Architecture
<img width="930" height="1272" alt="image" src="https://github.com/user-attachments/assets/6cea4e81-051f-40a7-bb73-2658a0de34a8" />


## Tech Stack
- **Frontend:** React.js, Leaflet.js (Mapping), CSS3 (Zebra-striping UI)
- **Backend:** Python, Flask, Socrata Open Data API (SoQL)
- **Geocoding:** Nominatim (OpenStreetMap)
- **Testing:** Pytest (12 automated test cases for API reliability)

## Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js & npm
- A Seattle Open Data API Key 

### Backend Setup
1. Create a `.env` file in the root directory and add:
   `SEATTLE_API_KEY=your_key_here`
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
