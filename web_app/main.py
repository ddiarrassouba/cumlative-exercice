"""FastAPI application for converting locations and checking weather."""

import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Path
from fastapi.responses import HTMLResponse

load_dotenv()

app = FastAPI()

API_KEY = os.getenv("GEOCODING_API_KEY") or ""


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    """Return the application's home page."""
    return """
    <html>
        <head>
            <title>City Coordinate Finder</title>
        </head>
        <body>
            <h1>City Coordinate Finder</h1>
            <p>The FastAPI application is working.</p>
        </body>
    </html>
    """


@app.post("/coordinates/{city}/{state}")
def get_coordinates(
    city: str = Path(min_length=2),
    state: str = Path(min_length=2),
) -> dict[str, object]:
    """Get the coordinates of a city and state in the United States."""
    url = "https://api.geoapify.com/v1/geocode/search"

    parameters: dict[str, str] = {
        "text": f"{city}, {state}, United States",
        "format": "json",
        "filter": "countrycode:us",
        "limit": "1",
        "apiKey": API_KEY,
    }

    response = httpx.get(url, params=parameters, timeout=10)

    if response.status_code != 200:
        return {"message": "The geocoding service is unavailable."}

    results = response.json()["results"]

    if not results:
        return {"message": "The city and state were not found."}

    location = results[0]

    return {
        "city": city,
        "state": state,
        "latitude": location["lat"],
        "longitude": location["lon"],
    }


@app.get("/weather/{latitude}/{longitude}")
def get_weather(
    latitude: float = Path(ge=-90, le=90),
    longitude: float = Path(ge=-180, le=180),
) -> dict[str, object]:
    """Return the current weather for a latitude and longitude."""
    url = "https://api.open-meteo.com/v1/forecast"

    parameters: dict[str, str] = {
        "latitude": str(latitude),
        "longitude": str(longitude),
        "current": "temperature_2m,weather_code,wind_speed_10m",
        "timezone": "auto",
    }

    response = httpx.get(url, params=parameters, timeout=10)

    if response.status_code != 200:
        return {"message": "The weather service is unavailable."}

    weather_data = response.json()
    current_weather = weather_data["current"]
    current_units = weather_data["current_units"]

    return {
        "latitude": latitude,
        "longitude": longitude,
        "time": current_weather["time"],
        "temperature": current_weather["temperature_2m"],
        "temperature_unit": current_units["temperature_2m"],
        "weather_code": current_weather["weather_code"],
        "wind_speed": current_weather["wind_speed_10m"],
        "wind_speed_unit": current_units["wind_speed_10m"],
    }
