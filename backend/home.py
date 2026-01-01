import time
from flask import Flask
from flask_cors import CORS 

app = Flask(__name__)
CORS(app) 

# testing my pytest environment
@app.route('/')
def home():
    return "Hello!"


@app.route('/api/time')
def get_current_time():
    
    return {
        'time': time.time(),
        'message': 'Hello from the EmeraldCityPulse Backend!'
    }

if __name__ == "__main__":
    app.run(debug=True, port=5000)