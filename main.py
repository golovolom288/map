import json
import requests
import folium
import os

from geopy import distance
from flask import Flask
from dotenv import load_dotenv


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def read_json(json_file):
    with open(json_file, "r", encoding="CP1251") as js_file:
        bars = json.loads(js_file.read())
    return bars


def get_bars_info(bars,my_coords):
    bars_info = []
    for bar in bars:
        latitude = bar["Latitude_WGS84"]
        longitude = bar["Longitude_WGS84"]
        name = bar["Name"]
        bar_coords = (latitude,longitude)
        distance_to_bar = distance.distance(bar_coords, my_coords).km
        bars_info.append({"title": name,
                     "distance": distance_to_bar,
                     "latitude": latitude,
                     "longitude": longitude,
        })
    return sorted(bars_info, key=lambda x: x["distance"])[:5]


def get_map():
    load_dotenv()
    yandex_api = os.getenv("YANDEXAPI")
    my_coords = fetch_coordinates(yandex_api, address)
    bars = read_json("coffee.json")
    bars_info = get_bars_info(bars, my_coords)
    m = folium.Map(
        my_coords,
        zoom_start=12,
        tiles="Stamen Terrain"
    )
    for bar in bars_info:
        folium.Marker(
            location=(bar["latitude"], bar["longitude"]),
            tooltip="Click me!",
            popup=bar["title"],
            icon=folium.Icon(icon="cloud"),
        ).add_to(m)
    m.save("index.html")
    with open('index.html', "rb") as file:
        return file.read()


def main():
    app = Flask(__name__)
    app.add_url_rule('/', 'hello', get_map)
    app.run('0.0.0.0')


if __name__ == "__main__":
    address = input("Где вы находитесь?")
    main()