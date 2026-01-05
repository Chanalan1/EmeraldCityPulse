import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
from math import radians, cos, sin, asin, sqrt


" reference: https://requests.readthedocs.io/en/latest/user/quickstart/  -> custom headers"
" reference: https://dev.socrata.com/docs/authentication.html -> how to authenticate"
" reference: https://dev.socrata.com/docs/queries/ -> how to write Socrata QL queries" 
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
    
    # create the filters for SocrataQL by adding time cutoff
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
    

def format_incident_date(raw_date):
    """
    Converts ISO 8601 format into 'Month date, year, time AM/PM' format for our reports

    Parameters:
        raw_date(str): ISO8601 format from the database
    """
    if not raw_date:
        return "Date Unknown"
    
    dt_obj = datetime.strptime(raw_date.split('.')[0], "%Y-%m-%dT%H:%M:%S")
    return dt_obj.strftime("%b %d, %Y, %I:%M %p")

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    helper function that calculates the distance in meters between two sets of GPS coordinates
    
    Parameters:
        lat1(float): latitude of the first point (user search)
        lon1(float): longitude of the first point (user search)
        lat2(float): latitude of the second point (incident report location)
        lon2(float): longitude of the second point (incident report location)

    Returns:
        int: The distance between the two points in meters
    """
    # Convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula needed to calculate two distances 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth 
    
    distance_km = c * r
    return round(distance_km * 1000)

def get_distance_value(incident_card):
    """
    this  acts as a 'sorting rule' for Python's sort method
    it extracts the calculated 'raw_dist' from report so the computer can rank incidents by proximity.
    EX: report says it was 300 meters away, it changes the 300 meters into an interger
    
    Parameters:
        incident_card(dict): A single dictionary representing one crime report

    Returns:
        int: The numerical distance in meters
    """
    return incident_card['raw_dist']

def process_report_data(raw_data, user_lat, user_lon):
    """
    This master function transforms raw database information into report cards shown to users' 
    It combines database info with NEW calculated data (like proximity) for the user.
    
    Parameters:
        raw_data(list): Raw crime data records from the Seattle Open Data API
        user_lat(float): Latitude of the center of the user's search
        user_lon(float): Longitude of the center of the user's search

    Returns:
        A status message and a list of cards sorted from closest to furthest.
    """
    # edge case where there are no reports 
    if not raw_data:
        return {
            "status": "empty", 
            "message": "No incidents found in this area for the selected time.", 
            "reports": []
        }

    processed_list = []
    
    for item in raw_data:
        # Pull coordinates from the database (default to 0 if missing)
        report_lat = float(item.get('latitude', 0))
        report_lon = float(item.get('longitude', 0))
        

        dist = calculate_distance(user_lat, user_lon, report_lat, report_lon)
        
        # creating our "report" back to the user
        card = {
            "type": item.get('offense_description', 'Incident Reported'),
            "date": format_incident_date(item.get('report_date_time')),
            "distance": f"{dist}m away",  
            "raw_dist": dist,             
            "coords": [report_lat, report_lon]
        }
        processed_list.append(card)

    # helper function to convert string informatin into int and rank the distances 
    processed_list.sort(key=get_distance_value)
    
    return {"status": "success", "reports": processed_list}


def main_search(address, time_range='30d', radius=600):
    """
    The main function that connects geocoding, API fetching, and data processing.
    
    Parameters:
        address(str): The physical address entered by the user
        time_range(str): The timeframe string (e.g., '7d', '30d')
        radius(int): The search radius in meters
        
    Returns:
        The final processed results ready for the web interface
    """
    # convert address to coordinates
    lat, lon = get_coordinates(address)
    
    if lat is None:
        return {"status": "error", "message": "Could not find that address. Please try again."}
    
    # fetch raw data from Seattle API
    raw_data = get_data(lat=lat, lon=lon, time_range=time_range, radius=radius)
    
    # process, format, and sort the data
    return process_report_data(raw_data, lat, lon)