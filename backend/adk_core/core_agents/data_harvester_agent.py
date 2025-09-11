import json
import logging
import httpx
import asyncio
from typing import Dict, Any
from pathlib import Path

from ..base_agent import BaseConstructionAgent

logger = logging.getLogger(__name__)

class DataHarvesterAgent(BaseConstructionAgent):
    """
    Core Agent: Data Harvester Agent
    Collects GIS, surveys, climate, and geotech data from external APIs.
    """
    def __init__(self):
        super().__init__(
            name="Data Harvester Agent",
            description="Collects GIS, climate, and geospatial data for the project site."
        )

    async def process_request(self, user_input: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """
        Reads the project location, fetches data from external APIs, and saves it as artifacts.
        """
        logger.info(f"{self.name}: Starting data harvesting for project {project_path.name}")
        
        async with httpx.AsyncClient() as client:
            try:
                # 1. Read location from Stage 1 artifacts
                charter_path = project_path / "stage_1" / "project_charter.json"
                if not charter_path.exists():
                    raise FileNotFoundError("Project charter from Stage 1 not found.")
                
                with open(charter_path, 'r') as f:
                    charter_data = json.load(f)
                
                location = charter_data.get('location')
                if not location:
                    raise ValueError("Location not found in project charter.")

                logger.info(f"{self.name}: Found location '{location}' for data harvesting.")

                # Use Google Geocoding API
                google_geocoding_api_key = "" # Replace with actual key from config/env
                google_geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"

                geocoded = False
                
                logger.info(f"{self.name}: Attempting to geocode with Google Geocoding API for: '{location}'")
                geo_response = await client.get(
                    google_geocoding_url,
                    params={"address": location, "key": google_geocoding_api_key}
                )
                geo_response.raise_for_status()
                geo_data = geo_response.json()
                
                if geo_data.get('status') == 'OK' and geo_data.get('results'):
                    lat = geo_data['results'][0]['geometry']['location']['lat']
                    lon = geo_data['results'][0]['geometry']['location']['lng']
                    logger.info(f"{self.name}: Successfully geocoded '{location}' to (lat: {lat}, lon: {lon}).")
                    geocoded = True
                
                if not geocoded:
                    raise ValueError(f"Could not geocode location: {location}")

                logger.info(f"{self.name}: Geocoded {location} to (lat: {lat}, lon: {lon}).")

                # 3. Fetch climate and elevation data
                forecast_params = {
                    "latitude": lat,
                    "longitude": lon,
                    "hourly": "temperature_2m,precipitation,wind_speed_10m",
                    "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
                    "timezone": "auto"
                }
                elevation_params = {"latitude": lat, "longitude": lon}

                climate_res, elevation_res = await asyncio.gather(
                    client.get("https://api.open-meteo.com/v1/forecast", params=forecast_params),
                    client.get("https://api.open-meteo.com/v1/elevation", params=elevation_params)
                )
                climate_res.raise_for_status()
                elevation_res.raise_for_status()

                climate_data = climate_res.json()
                elevation_data = elevation_res.json()
                logger.info(f"{self.name}: Successfully fetched climate and elevation data.")

                # 4. Save artifacts to Stage 2 directory
                stage_2_path = project_path / "stage_2"
                climate_path = stage_2_path / "climate_data.json"
                elevation_path = stage_2_path / "elevation_data.json"
                geocoding_path = stage_2_path / "geocoding_data.json"

                with open(climate_path, "w") as f:
                    json.dump(climate_data, f, indent=4)
                with open(elevation_path, "w") as f:
                    json.dump(elevation_data, f, indent=4)
                with open(geocoding_path, "w") as f:
                    json.dump(geo_data, f, indent=4)

                return {
                    "agent_name": self.name,
                    "status": "success",
                    "details": f"Successfully harvested data for {location}.",
                    "artifacts": [
                        {"type": "climate_data", "path": str(climate_path)},
                        {"type": "elevation_data", "path": str(elevation_path)},
                        {"type": "geocoding_data", "path": str(geocoding_path)}
                    ]
                }

            except Exception as e:
                logger.error(f"{self.name}: Error during data harvesting: {e}", exc_info=True)
                return {"agent_name": self.name, "status": "error", "message": str(e)}
