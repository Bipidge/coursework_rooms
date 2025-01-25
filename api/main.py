from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import requests
from db.functions import *
import json

app = FastAPI()

# Example model for a POST request
class Item(BaseModel):
    name: str
    description: str
    price: float
    on_offer: bool

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Nothing here"}

def get_coords_from_ukpostcode(postcode): #postcode without spaces
    res = requests.get(f"https://api.getthedata.com/postcode/{postcode}")
    data = json.loads(res.content)

    if data["status"] == "no_match":
        raise HTTPException(400, "invalid postcode. Try again and make sure postocode is written without spaces.")
    
    coords = {"lon": data["data"]["longitude"], "lat": data["data"]["latitude"]}
    return coords

def get_distance(slon,slat, roomlon, roomlat):
    res = requests.get(f"https://router.project-osrm.org/route/v1/driving/{slon},{slat};{roomlon},{roomlat}")
    data = json.loads(res.content)
    return data["routes"][0]["distance"]

def get_24hr_temp_percipation(lon, lat):
    res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,rain_sum,showers_sum,snowfall_sum,precipitation_probability_max&forecast_days=1")
    data = json.loads(res.content)
    percipitation = []
    rain_sum = float(data["daily"]["rain_sum"][0])
    showers_sum = float(data["daily"]["showers_sum"][0])
    snowfall_sum = float(data["daily"]["snowfall_sum"][0])
    if rain_sum <= 0.5 and rain_sum != 0:
        percipitation.append("Light rain")
    elif rain_sum <= 4:
        percipitation.append("Moderate rain")
    elif rain_sum <= 8:
        percipitation.append("Heavy rain")
    else:
        percipitation.append("Very Heavy rain")

    if showers_sum != 0 and showers_sum <= 2:
        percipitation.append("Slight shower")
    elif showers_sum <= 10:
        percipitation.append("Moderate shower")
    elif showers_sum <= 50:
        percipitation.append("Heavy shower")
    else:
        percipitation.append("Violent shower")

    if snowfall_sum != 0 and snowfall_sum <= 5:
        percipitation.append("Light snowfall")
    elif snowfall_sum <= 10:
        percipitation.append("Moderate snowfall")
    else:
        percipitation.append("Heavy snowfall")

    result = {"temp_min": data["daily"]["temperature_2m_min"][0], "temp_max": data["daily"]["temperature_2m_max"][0], "percipitation":str(percipitation)}
    return result

def get_number_of_crimes(lon, lat):
    res = requests.get(f"https://data.police.uk/api/crimes-street/all-crime?date=2024-01&lat={lat}&lng={lon}")
    data = json.loads(res.content)
    return len(data)

# list all rooms (name, location, price, room_id, distance) (weather will be inside the room menu)
@app.get("/rooms/{postcode}")
def get_rooms_list(postcode:str): # rooms from db + distance from user
    room_tuples = get_rooms()
    rooms = []
    for r in room_tuples:
        room = list(r)
        user_coords = get_coords_from_ukpostcode(postcode)
        room_coords = get_coords_from_ukpostcode(room[4])
        distance = get_distance(user_coords["lon"], user_coords["lat"], room_coords["lon"], room_coords["lat"])
        room.append(distance)
        rooms.append(room)
    
    return rooms


# get room by room_id (everything incl distance, weather, criminal thing)
@app.get("/room/{id},{postcode}")
def get_room_by_id(id:int, postcode:str):
    room_tuple = get_room_row(id)
    room = list(room_tuple)

    user_coords = get_coords_from_ukpostcode(postcode)
    room_coords = get_coords_from_ukpostcode(room[4])
    distance = get_distance(user_coords["lon"], user_coords["lat"], room_coords["lon"], room_coords["lat"])
    weather24hr = get_24hr_temp_percipation(room_coords["lon"], room_coords["lat"])
    num_of_crimes_past_month = get_number_of_crimes(room_coords["lon"], room_coords["lat"])

    return {"room": str(room), "distance":distance, "weather24hr":weather24hr, "num_of_crimes_past_month":num_of_crimes_past_month}


# cancel room application

# view history of applications 

if __name__ == "__main__":
    import uvicorn

    # Run the application on localhost:8000
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)
