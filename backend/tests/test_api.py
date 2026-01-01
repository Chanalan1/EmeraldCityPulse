import pytest
import requests
import os
from dotenv import load_dotenv
from api import get_data

load_dotenv()

# test to see if api endpoint is reachable
# if response is 200 meaning client request worked
def test_api_endpoint():

    url = 'https://data.seattle.gov/resource/tazs-3rd5.json' # the endpoint for the Seattle data base
    headers = {"X-App-Token": os.getenv("SEATTLE_API_KEY_ID")}
    response = requests.get(url, headers=headers, params={"$limit": 1})

    assert response.status_code == 200

# test to see if the request we get is returned as JSON format
# checks to see if connection is good first, then checks the response type which should be JSON
def test_isJSON():

    url = 'https://data.seattle.gov/resource/tazs-3rd5.json' 
    headers = {"X-App-Token": os.getenv("SEATTLE_API_KEY_ID")}
    response = requests.get(url, headers=headers, params={"$limit": 1})

    assert response.status_code == 200
    assert "application/json" in response.headers["Content-Type"]

# tests to make sure the logic of getting data returns actual data (such as correct data structure and actual data)
def test_get_data_returns_list():
    results = get_data()
    assert isinstance(results, list)
    assert len(results) > 0  

# tests to make sure the limit works and we get exactly how much is asked of us
def test_get_data_respects_limit():
    limit_count = 5
    results = get_data(limit=limit_count)
    assert len(results) == limit_count