from fastapi import FastAPI
import httpx

app = FastAPI()

@app.get("/forecast")
async def get_forecast(latitude: float, longitude: float):
    """Get weather forecast from Open-Meteo API"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,rain,dew_point_2m,relative_humidity_2m,wind_speed_10m,visibility,apparent_temperature",
        "timezone": "Europe/London",
        "forecast_days": 1,
        "forecast_hours": 1
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()
