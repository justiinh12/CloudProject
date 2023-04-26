import requests
import flask
from geopy.distance import geodesic, Point
from supabase import create_client, Client
import os
import time

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

locations = [
    # (42.0987, -75.9180, "binghamton"), # binghamton
    # (40.7423034776422, -73.82885377812502, "new york"), # new york
    (37.7749, -122.4194, "san francisco"), # san francisco
    # (25.7617, -80.1918, "miami"), # miami
    # (41.9779, -91.6656, "cedar rapids"), # cedar rapids
    # (47.6740, -122.1215, "redmond"), # redmond
    # (34.0522, -118.2437, "los angeles"), # los angeles
    # (30.2672, -97.7431, "austin"), # austin
]

stations = []

def save_to_db():
    # grab stations for each location
    for location in locations:
        p = Point(location[0], location[1])
        dist = 2500

        max_lat = geodesic(meters=dist).destination(p, 0).latitude
        min_lat = geodesic(meters=dist).destination(p, 180).latitude
        max_lng = geodesic(meters=dist).destination(p, 90).longitude
        min_lng = geodesic(meters=dist).destination(p, 270).longitude
        width = 1265

        if location[2] == "new york":
            max_lat = 40.780340433791196
            min_lat = 40.7023034776422
            min_lng = -74.06844362187502
            max_lng = -73.73885377812502

        if location[2] == "los angeles":
            min_lat = 40.7023034776422
            max_lat = 40.780340433791196
            min_lng = -74.06844362187502
            max_lng = -73.73885377812502

        url = f'https://www.gasbuddy.com/gaspricemap/map?fuelTypeId=1&height=600&width={width}&maxLat={max_lat}&maxLng={max_lng}&minLat={min_lat}&minLng={min_lng}'

        resp = requests.post(url, timeout=20)

        try:
            body = resp.json()
            for station in body["primaryStations"]:
                if station['price'] != '--':

                    url2 = 'https://www.gasbuddy.com/gaspricemap/station'
                    
                    resp2 = requests.post(url2, timeout=20, json={"id": station["id"],"fuelTypeId": "1"})

                    try:
                        station_details = resp2.json()["station"]

                        supabase.table("stations").insert({"id": station_details["Id"], "name": station_details["Name"], "site_name": station_details["Site"]["Name"], "country": station_details["Country"], "lat": station_details["Lat"], "lng": station_details["Lng"], "rating": station_details["Rating"]["StarValue"]}).execute()
                        # stations.append({"id:": station["id"], "location": location[2], "price": station["price"], "lat": station["lat"], "lng": station["lng"], "name": station_details["station"]["Name"], "rating": station_details["station"]["Rating"]["StarValue"]})
                        # print("loc: " + location[2] + " ID: " + str(station["id"]) + " price: " + str(station["price"]) + " lat: " + str(station["lat"]) + " " + str(station["lng"]))
                    except ValueError:
                        print("Failed to receive station response")
                # time.sleep(0.05)
        except ValueError:
            print("Failed to receive fuel price response")

    # grab the station data for each station in each location

    # parse and format this data

    # dump the data into supabase
    return

save_to_db()