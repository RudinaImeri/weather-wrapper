from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import datetime

# Initialize the FastAPI application
app = FastAPI()

# Configure CORS to allow requests from any origin
# (this is necessary so the frontend can call the API from another origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (you can restrict this in production)
    allow_methods=["GET"],  # Allow only GET requests
    allow_headers=["*"],  # Allow all headers
)

# Base URL for the Open-Meteo weather API
BASE_URL = "https://api.open-meteo.com/v1/forecast"


@app.get("/weather")
def get_weather(
    latitude: float,
    longitude: float
):
    """
    Fetches the current-hour temperature for the given location
    using the Open-Meteo API (12 hours past + 12 hours forecast).
    """
    # Get the current UTC time in ISO format, rounded to the hour
    now_iso = datetime.utcnow().replace(
        minute=0, second=0, microsecond=0
    ).isoformat()

    # Parameters sent to the Open-Meteo API
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_180m",
        "start": now_iso,
        "end":   now_iso,
        "timezone": "auto",
        "timeformat": "unixtime",
        "forecast_hours": 12,
        "past_hours":     12,
        "temporal_resolution": "native",
    }

    # Send the HTTP request to Open-Meteo
    r = requests.get(BASE_URL, params=params)

    # If the API returns an error, raise an HTTP exception
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)

    # Return the response JSON to the frontend
    return r.json()


@app.get("/geocode")
def geocode(
    city: str = Query(..., description="City name to search

