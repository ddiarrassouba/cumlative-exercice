import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Path
from fastapi.responses import HTMLResponse

load_dotenv()

app = FastAPI()

API_KEY = os.getenv("GEOCODING_API_KEY")


@app.get("/", response_class=HTMLResponse)
def home():
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
):
    url = "https://api.geoapify.com/v1/geocode/search"

    parameters = {
        "text": f"{city}, {state}, United States",
        "format": "json",
        "filter": "countrycode:us",
        "limit": 1,
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
