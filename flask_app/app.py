from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
import requests
import json

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

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


        # Query the API for the nearest gas stations to the input location
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=5000&type=gas_station&key={AIzaSyAdHsbB4qey791DIuz8R9hoCT0yH49APT8}"
        response = requests.get(url)
        data = json.loads(response.text)

        # Extract the relevant information from the API response
        results = []
        for result in data['results']:
            name = result['name']
            address = result['vicinity']
            lat = result['geometry']['location']['lat']
            lng = result['geometry']['location']['lng']
            place_id = result['place_id']
            results.append({'name': name, 'location': location, 'lat': lat, 'lng': lng, 'place_id': place_id})

        return render_template('results.html', results=results)
    except Exception as e:
        error_message = str(e)
        return render_template('error.html', error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)
