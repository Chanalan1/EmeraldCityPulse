import requests
import os
from dotenv import load_dotenv


" reference: https://requests.readthedocs.io/en/latest/user/quickstart/  -> custom headers"
" reference: https://dev.socrata.com/docs/authentication.html -> how to authenticate"
" reference: https://dev.socrata.com/docs/queries/ -> how to write Socrate QL queries" 

# request changes the JSON to a python dictionary/list
def get_data(neighborhood=None, limit = 20):
    """
    Grabs the latest crime incidents from Seattle Open Data Portal API
    
    Parameters:
        neighborhood(str, optional): Name of the Seattle neighborhood
        limit(int): limit on how many records it returns
    

    Returns:
      list: A list of dictionaries containing crime incident data, or an 
              empty list if the request fails.
    """

    url = 'https://data.seattle.gov/resource/tazs-3rd5.json'
    headers = {"X-App-Token": os.getenv("SEATTLE_API_KEY_ID")}
    params = {
        "$limit": limit,
        "$order": "report_date_time DESC"
    }

    # append neighborhood to parameters if given
    if neighborhood:
        params["$where"] = f"neighborhood = '{neighborhood.upper()}'"

    r = requests.get(url, headers=headers, params=params)

    if r.status_code == 200:
        return r.json()
    else:
        print(f"Error: {r.status_code}")
        print(r.text)
        return []