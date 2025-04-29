from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import datetime

# Inicializimi i aplikacionit FastAPI
app = FastAPI()

# Konfigurimi i CORS për me lejuar kërkesat nga cilido origin
# (e nevojshme që frontend të mund të thërrasë API-n nga një tjetër origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lejo të gjitha origin-et (në praktikë mund ta kufizosh)
    allow_methods=["GET"],  # Lejo vetëm metodat GET
    allow_headers=["*"],  # Lejo të gjitha header-at
)

# URL-ja bazë për API-n e motit nga Open-Meteo
BASE_URL = "https://api.open-meteo.com/v1/forecast"


@app.get("/weather")
def get_weather(
    latitude: float,
    longitude: float
):
    """
    Merr temperaturën për orën aktuale për një lokacion të dhënë
    duke përdorur Open-Meteo API (12 orë në të kaluarën + 12 në të ardhmen).
    """
    # Marrja e kohës aktuale në format ISO, me minuta dhe sekonda të vendosura në 0
    now_iso = datetime.utcnow().replace(
        minute=0, second=0, microsecond=0
    ).isoformat()

    # Parametrat që i dërgohen Open-Meteo API
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

    # Kërkesa HTTP te Open-Meteo
    r = requests.get(BASE_URL, params=params)

    # Nëse ka ndonjë gabim nga API, dërgo HTTP error
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)

    # Kthe të dhënat si JSON për frontend
    return r.json()


@app.get("/geocode")
def geocode(
    city: str = Query(..., description="Emri i qytetit për me u kërku")
):
    """
    Bën kërkim të koordinatave për një qytet përmes OpenStreetMap Nominatim API.
    Kthen gjerësinë dhe gjatësinë gjeografike.
    """
    # Kërkesa HTTP te Nominatim API
    resp = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": city, "format": "json", "limit": 1},
        headers={"User-Agent": "weather-wrapper/1.0"}  # Kërkohet nga API
    )

    # Kontrolli për status code të gabuar
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    # Përpunimi i përgjigjes
    results = resp.json()

    # Nëse nuk gjendet lokacioni, kthe HTTP 404
    if not results:
        raise HTTPException(status_code=404, detail="Location not found")

    # Kthe koordinatat si JSON
    return {
        "latitude":  float(results[0]["lat"]),
        "longitude": float(results[0]["lon"])
    }

