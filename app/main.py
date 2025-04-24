from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import datetime

app = FastAPI()

# Allow cross‐origin requests, we're using this for frontend part
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Base URL for Open-Meteo
BASE_URL = "https://api.open-meteo.com/v1/forecast"


@app.get("/weather")
def get_weather(
    latitude: float,
    longitude: float
):
    """
    Fetch the current‐hour temperature for the given lat/lon
    from Open-Meteo, using a 12h past + 12h forecast window.
    """
    now_iso = datetime.utcnow().replace(
        minute=0, second=0, microsecond=0
    ).isoformat()

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

    r = requests.get(BASE_URL, params=params)
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return r.json()


@app.get("/geocode")
def geocode(
    city: str = Query(..., description="Place name to look up")
):
    """
    Look up a city name via OpenStreetMap’s Nominatim
    and return its latitude & longitude.
    """
    resp = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": city, "format": "json", "limit": 1},
        headers={"User-Agent": "weather-wrapper/1.0"}
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    results = resp.json()
    if not results:
        raise HTTPException(status_code=404, detail="Location not found")

    return {
        "latitude":  float(results[0]["lat"]),
        "longitude": float(results[0]["lon"])
    }
