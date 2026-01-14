from flask import Flask, jsonify, request
from flask_cors import CORS
from backend.api import main_search

app = Flask(__name__)
CORS(app)

@app.route('/api/search', methods=['GET'])
def search():
    address = request.args.get('address')
    
    # Defaulting to 250m and 1 week if not specified
    radius = request.args.get('radius', default=250, type=int)
    time_range = request.args.get('time_range', default='1w', type=str)

    if not address:
        return jsonify({"status": "error", "message": "No address provided"}), 400

    full_address = f"{address}, Seattle, WA"
    
    # Get the results from api.py
    results = main_search(full_address, radius=radius, time_range=time_range)

    # Wrap for the frontend
    response_data = {
        "status": results.get("status", "success"),
        "reports": results.get("reports", []),
        "metadata": {
            "lat": results.get("lat"), 
            "lon": results.get("lon")
        }
    }
    
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)