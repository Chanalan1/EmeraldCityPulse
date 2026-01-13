from flask import Flask, jsonify, request
from flask_cors import CORS
from backend.api import main_search

'Sourced sample code: https://flask-cors.readthedocs.io/en/latest/'


app = Flask(__name__)
CORS(app)

@app.route('/api/search', methods=['GET'])
def search():

    address = request.args.get('address')

    results = main_search(address)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)