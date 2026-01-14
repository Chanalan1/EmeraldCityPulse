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
def get_data(lat=None, lon=None, neighborhood=None, time_range='1w', radius=250, limit=20, sort_order="DESC"):
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
    headers = {"X-App-Token": os.getenv("SEATTLE_API_KEY")}
    
    # create the filters for SocrataQL by adding time cutoff
    # Ex: all most recent reports from 30 days starting from December 1, 2025
    date_helper = get_date(time_range)
    search = f"report_date_time > '{date_helper}'"
    api_key = os.getenv("SEATTLE_API_KEY")
    print(f"DEBUG: API Key found? {api_key is not None}")
    

    # Priorities neighborhood address then looks to append lat and long
    if neighborhood:
        search += f" AND neighborhood = '{neighborhood.upper()}'"

    elif lat and lon:
        
        # geospatial calculation to determine search box around user, 1 degree = 111.... meters
        lat_offset = radius / 111139.0
        lon_offset = radius / (111139.0 * cos(radians(lat)))
        
        min_lat, max_lat = lat - lat_offset, lat + lat_offset
        min_lon, max_lon = lon - lon_offset, lon + lon_offset

        # gets rid of all data that has redacted from report for parsing purposes (due to privacy reasons from city)
        search += " AND latitude != 'REDACTED' AND longitude != 'REDACTED'"

       # database requires lat/long as Text strings rather than int, changes to int then into string
        search += f" AND latitude::number BETWEEN {min_lat} AND {max_lat}"
        search += f" AND longitude::number BETWEEN {min_lon} AND {max_lon}"
        
        

    print(f"DEBUG Socrata Query: {search}")

    params = {
        "$where": search,
        "$limit": limit,
        "$order": f"report_date_time {sort_order}" 
    }

    try:
        # Increased timeout to 60 seconds
        # error handling to see error messagei fails
        r = requests.get(url, headers=headers, params=params, timeout=60)
        
        if r.status_code == 200:
            return r.json()
        else:
            print(f" API ERROR: {r.status_code} - {r.text}")
            return []
            
    except requests.exceptions.ReadTimeout:
        print(" DATABASE TIMEOUT: The Seattle API took too long to respond.")
        return [] 
    except requests.exceptions.RequestException as e:
        print(f"⚠️CONNECTION ERROR: {e}")
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
        try:
            report_lat = float(item.get('latitude'))
            report_lon = float(item.get('longitude'))
        except (ValueError, TypeError):
            continue

        dist = calculate_distance(user_lat, user_lon, report_lat, report_lon)
        # Pull coordinates from the database (default to 0 if missing)
        report_lat = float(item.get('latitude', 0))
        report_lon = float(item.get('longitude', 0))
        

        dist = calculate_distance(user_lat, user_lon, report_lat, report_lon)
        
        # creating our "report" back to the user
        card = {
            "type": item.get('offense_sub_category', item.get('offense_category', 'Incident Reported')),
            "date": format_incident_date(item.get('report_date_time')),
            "distance": f"{dist}m away",  
            "raw_dist": dist,             
            "coords": [report_lat, report_lon]
        }
        processed_list.append(card)

    # helper function to convert string informatin into int and rank the distances 
    processed_list.sort(key=get_distance_value)
    
    return {"status": "success", "reports": processed_list}

def get_date(time_range):
    """
    Helper function to calculate the date format needed for the database as a string
    """
    now = datetime.now()

    if time_range == '1w':
        delta = timedelta(days=7)
    elif time_range == '2w':
        delta = timedelta(days=14)
    elif time_range == '1m':
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
        # Fallback default as 30 days
        delta = timedelta(days=30)

    calculated_time = now - delta
    return calculated_time.strftime("%Y-%m-%dT%H:%M:%S")

def main_search(address, time_range='1w', radius=250):
    lat, lon = get_coordinates(address)
    if lat is None:
        return {"status": "error", "message": "Could not find address."}

    
    # If timeframe is > 1 week, start from the bottom of the date range (Oldest First)
    if time_range in ['1w']:
        order = "DESC" # Newest first for quick checks
    else:
        order = "ASC"  # Oldest first for deep history checks

    raw_data = get_data(lat=lat, lon=lon, time_range=time_range, radius=radius, sort_order=order)
    
    processed = process_report_data(raw_data, lat, lon)
    processed['lat'] = lat
    processed['lon'] = lon
    
    return processed