import requests
import time
import random

import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

id = 7
while id < 208873:

    url2 = 'https://www.gasbuddy.com/gaspricemap/station'
                        
    resp2 = requests.post(url2, timeout=20, json={"id": id, "fuelTypeId": "1"})

    body = resp2.json()["station"]
    supabase.table("stations").insert({"id": body["Id"], "name": body["Name"], "site_name": body["Site"]["Name"], "country": body["Country"], "lat": body["Lat"], "lng": body["Lng"], "rating": body["Rating"]["StarValue"]}).execute()
    id += 1
    time.sleep(random.uniform(1.2, 5.6))
# try:
#     body = resp2.json()
#     supabase.table("stations").insert({"id": body["Id"], "name": body["Name"], "site_name": body["Site"]["Name"], "country": body["Country"], "lat": body["Lat"], "lng": body["Lng"], "rating": body["Rating"]["StarValue"]}).execute()
# except:
#     print("failure\n")
#     print(resp2.content)