import json
import logging
import base64
from typing import Dict, Any
from pathlib import Path

from ..base_agent import BaseConstructionAgent
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class GeospatialSiteContextAgent(BaseConstructionAgent):
    """
    Specialist Agent: Geospatial & Site Context
    Performs advanced microclimate, seismic, and soil analysis using an LLM.
    """
    def __init__(self):
        super().__init__(
            name="Geospatial & Site Context Agent",
            description="Analyzes geospatial context based on project coordinates."
        )
        self.gemini_service = GeminiService()

    async def process_request(self, user_input: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """
        Reads geocoding data and uses an LLM to infer and analyze the site context.
        """
        logger.info(f"{self.name}: Starting geospatial context analysis for {project_path.name}")

        try:
            # 1. Read geocoding data from the current stage's artifacts
            geocoding_path = project_path / "stage_2" / "geocoding_data.json"
            if not geocoding_path.exists():
                raise FileNotFoundError("Geocoding data from Data Harvester Agent not found.")

            with open(geocoding_path, 'r') as f:
                geo_data = json.load(f)

            lat = geo_data['results'][0]['geometry']['location']['lat']
            lon = geo_data['results'][0]['geometry']['location']['lng']
            display_name = geo_data['results'][0]['formatted_address'] # Use formatted_address for display

            # 2. Create a prompt for Gemini to act as a geospatial analyst
            prompt = (
                f"As a senior geospatial analyst, provide a summary of the site context for a construction project "
                f"located at approximately latitude {lat}, longitude {lon} (near {display_name}). "
                f"Based on general knowledge of this region, infer the following: "
                f"1. **Topography & Land Use:** Describe the likely topography (e.g., flat, hilly, coastal) and dominant land use (e.g., dense urban, suburban, rural, industrial). "
                f"2. **Potential Environmental Risks:** Identify common environmental risks for this area (e.g., flood zones, seismic activity, wildfires, high winds, soil issues). "
                f"3. **Infrastructure & Accessibility:** Comment on the likely proximity to major infrastructure like highways, public transit, and utilities. "
                f"Format the output STRICTLY as a JSON object with keys 'topography_land_use', 'environmental_risks', and 'infrastructure_accessibility'."
            )

            # 3. Call Gemini and save the analysis
            analysis_str = await self.gemini_service.generate_text(prompt, temperature=0.4)
            if not analysis_str:
                raise ValueError("Gemini returned no response for geospatial analysis.")

            # Remove markdown code block fences if present
            if analysis_str.startswith("```json\n") and analysis_str.endswith("\n```"):
                analysis_str = analysis_str[len("```json\n"):-len("\n```")]

            analysis_data = json.loads(analysis_str)
            
            json_output_path = project_path / "stage_2" / "geospatial_analysis.json"
            with open(json_output_path, "w") as f:
                json.dump(analysis_data, f, indent=4)

            logger.info(f"{self.name}: Successfully generated and saved geospatial analysis JSON.")

            # Generate Image Site Plan
            image_prompt = (
                f"Generate a conceptual site plan for a construction project located near {display_name}. "
                f"Include visual representations of: "
                f"1. Topography and Land Use: {analysis_data.get('topography_land_use', 'N/A')}. "
                f"2. Potential Environmental Risks: {analysis_data.get('environmental_risks', 'N/A')}. "
                f"3. Infrastructure and Accessibility: {analysis_data.get('infrastructure_accessibility', 'N/A')}. "
                f"The image should be a top-down view, clear, and conceptual, like an architectural sketch."
            )
            site_plan_image_base64 = await self.gemini_service.generate_image(image_prompt)

            if site_plan_image_base64 is None:
                raise ValueError("Image generation failed for site plan.")

            # Save the base64 image to a file (optional, but good for debugging/storage)
            image_output_path = project_path / "stage_2" / "site_plan.png"
            with open(image_output_path, "wb") as f:
                f.write(base64.b64decode(site_plan_image_base64))

            logger.info(f"{self.name}: Successfully generated and saved Site Plan Image.")

            return {
                "agent_name": self.name,
                "status": "success",
                "details": f"Generated geospatial analysis and site plan image for {display_name}.",
                "artifacts": [
                    {"type": "geospatial_analysis", "path": str(json_output_path)},
                    {"type": "site_plan_image", "content": site_plan_image_base64, "path": str(image_output_path)}
                ]
            }

        except Exception as e:
            logger.error(f"{self.name}: Error during geospatial analysis: {e}", exc_info=True)
            return {"agent_name": self.name, "status": "error", "message": str(e)}

    