import pytest
import requests
import os
from dotenv import load_dotenv
from api import get_date, get_coordinates, get_data, format_incident_date, calculate_distance, process_report_data, get_distance_value
from unittest.mock import patch, MagicMock



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

# test to make sure the get date function properly returns the right format
# ISO 8601 date/time has 19 characters 
def test_get_date_format():
    date = get_date('30d')
    assert len(date) == 19

# testing the accuracy of the latitude and longitude helper given an address/location
def test_location():
    coords = get_coordinates("Space Needle")
    lat = coords[0]
    lon = coords[1]
    # lat and long of the space needle
    assert round(lat, 2) == 47.62
    assert round(lon, 2) == -122.35


# test to ensure the date is converted to human-readable format
def test_format_incident_date():
    raw = "2026-01-04T14:30:00"
    formatted = format_incident_date(raw)
    assert formatted == "Jan 04, 2026, 02:30 PM"

# test to ensure the distance calculation returns an integer in meters
def test_calculate_distance():
    dist = calculate_distance(47.6205, -122.3493, 47.6089, -122.3401)
    assert isinstance(dist, int)
    assert 1400 < dist < 1700

# test to ensure the sorting librarian extracts the hidden raw_dist value
def test_get_distance_value():
    card = {"raw_dist": 500}
    assert get_distance_value(card) == 500

# test to ensure closest incident is first and empty data is handled
def test_process_report_data():
    fake_data = [
        {'latitude': '48.0', 'longitude': '-123.0'},
        {'latitude': '47.6', 'longitude': '-122.3'}
    ]
    result = process_report_data(fake_data, 47.6, -122.3)
    assert result['reports'][0]['raw_dist'] < result['reports'][1]['raw_dist']
    
    empty_result = process_report_data([], 47.6, -122.3)
    assert empty_result['status'] == "empty"


# test to ensure that crimes with none return empty and not crash (edgecase)
# mock test to not send real api to database
@patch('api.requests.get')
@patch('api.os.getenv')
def test_no_results_found(mock_getenv, mock_get):
    mock_getenv.return_value = 'fake_token'
    
    # testing response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []
    mock_get.return_value = mock_response

    results = get_data(lat=47.6, lon=-122.3)
    
    # makes sure the list is empty
    assert results == []