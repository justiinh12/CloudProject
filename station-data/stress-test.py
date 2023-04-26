import requests

width = 1265
max_lat = 40.780340433791196
min_lat = 40.7023034776422
min_lng = -74.06844362187502
max_lng = -73.73885377812502

i = 0

while i < 50:
    url = f'https://www.gasbuddy.com/gaspricemap/map?fuelTypeId=1&height=600&width={width}&maxLat={max_lat}&maxLng={max_lng}&minLat={min_lat}&minLng={min_lng}'

    resp = requests.post(url, timeout=20)

    i += 1

