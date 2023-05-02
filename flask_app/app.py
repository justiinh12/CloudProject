from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
from geopy.distance import geodesic, Point
import traceback
import requests
import json
import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


#app = Flask(__name__, template_folder='templates')
api_key = "AIzaSyAdHsbB4qey791DIuz8R9hoCT0yH49APT8"

app = Flask(__name__, template_folder='templates', static_folder="static")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/prices')
def prices():
    logs = supabase.table("prices").select("*").execute().data
    for i in range(0, len(logs)):
        logs[i]["created_at"] = logs[i]["created_at"][0:10]
        del logs[i]["id"]
    return render_template('graphs.html', data=logs)

@app.route('/prices/<place>')
def price(place):
    if place == 'austin' or place == 'binghamton' or place == 'new york' or place == 'san francisco' or place == 'miami' or place == 'cedar rapids' or place == 'redmond' or place == 'los angeles':
        logs = supabase.table("prices").select("*").execute().data
        logs = list(filter(lambda x: x["loc"] == place, logs))
        for i in range(0, len(logs)):
            logs[i]["created_at"] = logs[i]["created_at"][0:10]
            del logs[i]["id"]
        return logs
    else:
        return [{'err': True}]

def add_addr(addr_dict):
    address_parts = []
    if 'house_number' in addr_dict:
        address_parts.append(addr_dict['house_number'])
    elif 'amenity' in addr_dict:
        address_parts.append(addr_dict['amenity'])
    if 'road' in addr_dict:
        address_parts.append(addr_dict['road'])
    if 'town' in addr_dict:
        address_parts.append(addr_dict['town'])
    if 'state' in addr_dict:
        address_parts.append(addr_dict['state'])
    if 'postcode' in addr_dict:
        address_parts.append(addr_dict['postcode'])
    return ', '.join(address_parts)

def get_gas_prices(lat, lng, dist):
    #api_url = f"https://www.gasbuddy.com/gaspricemap/county?lat={lat}&lng={lng}&usa=true"
   
    p = Point(lat, lng)

    maxLat = geodesic(meters=dist).destination(p, 0).latitude
    minLat = geodesic(meters=dist).destination(p, 180).latitude
    maxLng = geodesic(meters=dist).destination(p, 90).longitude
    minLng = geodesic(meters=dist).destination(p, 270).longitude

    print(maxLat, minLat, maxLng, minLng)
    
    print("Sending request")

    url = f'https://www.gasbuddy.com/gaspricemap/map?fuelTypeId=1&height=600&width=1265&maxLat={maxLat}&maxLng={maxLng}&minLat={minLat}&minLng={minLng}'
    
    test_url =  'https://www.gasbuddy.com/gaspricemap/map?fuelTypeId=1&height=600&width=1265&maxLat=45.40307408555111&maxLng=-75.72397054133633&minLat=45.31101409445494&minLng=-75.83098073480714'
    response = requests.post(url)


    print("Returning response")
    try:
        return response.json()
    except ValueError:
        print(response.content)
    return {}

@app.route('/nearest_gas_stations', methods=['POST'])
def nearest_gas_stations():
    try:
        print(request.form)
        location = request.form['location']
        dist = int(request.form['distance'])

        # Convert the address to latitude and longitude coordinates
        locator = Nominatim(user_agent="myGeocoder", timeout=10)
        loc = locator.geocode(location)
        prompt_lat = loc.latitude
        prompt_lng = loc.longitude

        print(prompt_lat, prompt_lng)

        prices = get_gas_prices(prompt_lat, prompt_lng, dist)
        print("got prices")
        print(prices)

        coords = []
        for gas_station in prices['primaryStations'] + prices['secondaryStations']:
            coords.append((gas_station['lat'], gas_station['lng'], gas_station['price']))

        #url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=5000&type=gas_station&key=AIzaSyAdHsbB4qey791DIuz8R9hoCT0yH49APT8"
        
            #url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=latlng:{lat},{lng}&inputtype=textquery&fields=name,rating,formatted_address,geometry&key={api_key}"

        results = []

        for coord in coords:
            lat = coord[0]
            lng = coord[1]

            found = False
            radius = 50
            while(not found):
                # Query the API for the gas station input lat/lng
                url=f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius}&type=gas_station&key={api_key}"
                response = requests.get(url, timeout=20)
                if response.json()['results']:
                    found = True
                else:
                    radius += 10
            data = response.json()['results'][0]
            name = data['name']
            addr = data['vicinity']
            place_id = data['place_id']
            try:
                rating = data['rating']
            except Exception as e:
                rating = "NAN"
            price = coord[2]
            results.append({'name': name, 'addr': addr, 'lat': lat, 'lng': lng, 'place_id': place_id, 'price': price, 'rating': rating})

        print("appended")

        # Extract the relevant information from the API response
        #results = []
        #for result in data['results']:
            #name = result['name']
            #address = result['vicinity']
            #lat = result['geometry']['location']['lat']
            #lng = result['geometry']['location']['lng']
            #print(lat)
            #print(lng)
            #addr_dict = locator.reverse((lat, lng)).raw['address']
            #addr = add_addr(addr_dict)
            #place_id = result['place_id']
            #results.append({'name': name, 'location': addr, 'lat': lat, 'lng': lng, 'place_id': place_id})

        results = [s for s in results if s['price'] != "--"]
        results = sorted(results, key=lambda x: x['price'])


        #for result in data['results']:
            #name = result['name']
            #address = result['vicinity']
            #lat = result['geometry']['location']['lat']
            #lng = result['geometry']['location']['lng']
            #print(lat)
            #print(lng)
            #addr_dict = locator.reverse((lat, lng)).raw['address']
            #addr = add_addr(addr_dict)
            #place_id = result['place_id']
            #results.append({'name': name, 'location': addr, 'lat': lat, 'lng': lng, 'place_id': place_id})


        #print("getting price")
        #prices = get_gas_prices(prompt_lat, prompt_lng)
        #print("got prices")
        #for i in range(len(results)):
            #try:
                #station = prices["primaryStations"][i]
                #if station:
                    #results[i]["price"] = station["price"]
                #else:
                    #results[i]["price"] = "?"
            #except:
                #pass
        #print(prices)

        return render_template('results.html', results=results)
    except Exception as e:
        line = f"An exception occurred on line {traceback.tb_lineno(e.__traceback__)}: {e}\n"        
        error_message = str(e) + line
        return render_template('error.html', error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)
