from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
import requests
import json

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

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

def get_gas_prices(lat, lng):
    api_url = f"https://www.gasbuddy.com/gaspricemap/county?lat={lat}&lng={lng}&usa=true"
    response = requests.post(api_url)
    return response.json()

@app.route('/nearest_gas_stations', methods=['POST'])
def nearest_gas_stations():
    try:
        print("starting")
        print(request.form)
        location = request.form['location']

        print("got location")

        # Convert the address to latitude and longitude coordinates
        locator = Nominatim(user_agent="myGeocoder")
        loc = locator.geocode(location)
        lat = loc.latitude
        lng = loc.longitude

        print(lat)
        print(lng)


        # Query the API for the nearest gas stations to the input location
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=5000&type=gas_station&key=AIzaSyAdHsbB4qey791DIuz8R9hoCT0yH49APT8"
        response = requests.get(url)
        data = json.loads(response.text)

        # Extract the relevant information from the API response
        results = []
        for result in data['results']:
            name = result['name']
            address = result['vicinity']
            lat = result['geometry']['location']['lat']
            lng = result['geometry']['location']['lng']
            addr_dict = locator.reverse((lat, lng)).raw['address']
            addr = add_addr(addr_dict)
            place_id = result['place_id']
            results.append({'name': name, 'location': addr, 'lat': lat, 'lng': lng, 'place_id': place_id})

        return render_template('results.html', results=results)
    except Exception as e:
        error_message = str(e)
        return render_template('error.html', error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)
