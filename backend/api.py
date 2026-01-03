import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim



" reference: https://requests.readthedocs.io/en/latest/user/quickstart/  -> custom headers"
" reference: https://dev.socrata.com/docs/authentication.html -> how to authenticate"
" reference: https://dev.socrata.com/docs/queries/ -> how to write Socrate QL queries" 
"reference: https://geopy.readthedocs.io/en/stable/#nominatim -> geopy nominatim "

# request changes the JSON to a python dictionary/list
def get_data(lat=None, lon=None, neighborhood=None, time_range='30d', radius=600, limit=20):
    """
    Grabs the latest crime incidents from Seattle Open Data Portal API
    
    Parameters:
        lat/lon(float): latitude and longitude for searching
        neighborhood(str): specific city neighborhood to search
        time_range(str): how far back to look up 
        radius(int): search radius in meters from the location looked up
        limit(int): maximum number of records to be pulled
        
    Returns:
        List of dictionaries in invidual form of crime reports/incidents 
    """

    url = 'https://data.seattle.gov/resource/tazs-3rd5.json'
    headers = {"X-App-Token": os.getenv("SEATTLE_API_KEY_ID")}
    
    # create the filters for SocratesQL by adding time cutoff
    # Ex: all most recent reports from 30 days starting from December 1, 2025
    date_helper = get_date(time_range)
    search = f"report_date_time > '{date_helper}'"
    

    # Priorities neighborhood address then looks to append lat and long
    if neighborhood:
        search += f" AND neighborhood = '{neighborhood.upper()}'"

    elif lat and lon:
        # within_circle SoQL function for geospatial quaries
        search += f" AND within_circle(canvas_location, {lat}, {lon}, {radius})" 

    params = {
        "$where": search,
        "$limit": limit,
        "$order": "report_date_time DESC"
    }

    r = requests.get(url, headers=headers, params=params, timeout=10)

    if r.status_code == 200:
        return r.json()
    else:
        return []

def get_date(time_range):
    """
    Helper function to calculate the date format needed for the database as a string

    Parameters:
        time_range(str): the amount of time that needsd to be converted to ISO-formatted date

    Returns:
        String of time in YYYY-MM-DDTHH:MM:SS format (ISO 8601)

    """

    now = datetime.now()

    # ranges of time that the users are able to choose from, ranging from last 7 days to last 3 years
    if time_range == '7d':
        delta = timedelta(days=7)
    elif time_range == '30d':
        delta = timedelta(days=30)
    elif time_range == '3m':
        delta = timedelta(days=90)  
    elif time_range == '6m':
        delta = timedelta(days=180)
    elif time_range == '1y':
        delta = timedelta(days=365)
    elif time_range == '3y':
        delta = timedelta(days=1095)
    else:
        delta = timedelta(days=30)

    calculated_time = now - delta

    # returns the calculated timer period in the proper format of years, month, date, hour, minute, and seconds
    return calculated_time.strftime("%Y-%m-%dT%H:%M:%S")

def get_coordinates(address):
    """
    This helper function converts the address given to latitude and longitude
    
    Parameters:
        address(str): address to convert to lat,long

    Returns:
        tuple in the form of latitude and longitude
    """

    # custom agent to comply with OpenStreetMap usage policy
    geolocator = Nominatim(user_agent = 'EmeraldCityPulse')

    location = geolocator.geocode(address)

    if location:
        return location.latitude, location.longitude
    
    return None, None
    
    
