import json
import logging
import base64
from typing import Dict, Any
from pathlib import Path

from ..base_agent import BaseConstructionAgent
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class MepSystemsAgent(BaseConstructionAgent):
    """
    Core Agent: MEP Systems Agent
    Handles mechanical, electrical, and plumbing planning.
    """
    def __init__(self):
        super().__init__(
            name="MEP Systems Agent",
            description="Generates preliminary MEP system recommendations."
        )
        self.gemini_service = GeminiService()

    async def process_request(self, user_input: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """
        Generates preliminary MEP system recommendations based on project data.
        """
        logger.info(f"{self.name}: Generating preliminary MEP design for {project_path.name}")

        try:
            # 1. Extract data gathered by the workflow engine from previous stages
            project_charter = user_input.get('project_charter', {})
            constraints = user_input.get('constraints', {})
            geospatial_analysis = user_input.get('geospatial_analysis', {})
            conceptual_floor_plan = user_input.get('conceptual_floor_plan', {})

            if not all([project_charter, constraints, geospatial_analysis, conceptual_floor_plan]):
                raise ValueError("Missing required artifacts from previous stages for MEP design.")

            # Extract relevant details for the prompt
            project_type = project_charter.get('project_type', 'building')
            location = project_charter.get('location', 'a site')
            geospatial_summary = geospatial_analysis.get('topography_land_use', 'N/A')
            floor_plan_summary = conceptual_floor_plan.get('layout_summary', 'N/A')

            # 2. Construct a detailed prompt for Gemini
            prompt = (
                f"As an MEP engineer, propose preliminary MEP system recommendations for a {project_type}. "
                f"Consider the location ({location}), geospatial context ({geospatial_summary}), and the conceptual floor plan ({floor_plan_summary}). "
                f"Suggest appropriate HVAC systems, electrical layouts, plumbing strategies, and smart home integrations. "
                f"Format output STRICTLY as a JSON object with keys 'hvac_recommendations', 'electrical_notes', 'plumbing_strategies', 'smart_home_integration', and 'notes'."
            )
            logger.info(f"{self.name}: Calling Gemini for MEP design interpretation...")
            gemini_response_str = await self.gemini_service.generate_text(prompt, temperature=0.6)

            if gemini_response_str is None:
                raise ValueError("LLM did not generate a valid response for MEP design.")

            try:
                gemini_parsed = json.loads(gemini_response_str)
            except json.JSONDecodeError:
                logger.error(f"{self.name}: Gemini response was not valid JSON: {gemini_response_str}. Using fallback data.")
                gemini_parsed = {
                    "hvac_recommendations": "Generic HVAC system",
                    "electrical_notes": "Standard electrical layout",
                    "plumbing_strategies": "Basic plumbing strategy",
                    "smart_home_integration": "No smart home integration",
                    "notes": "AI parsing failed or response malformed."
                }

            json_output_path = project_path / "stage_7" / "preliminary_mep_design.json"
            with open(json_output_path, "w") as f:
                json.dump(gemini_parsed, f, indent=4)

            logger.info(f"{self.name}: Generated preliminary MEP design JSON for {project_path.name}.")

            # Generate Image MEP Drawing
            image_prompt = (
                f"Generate a conceptual MEP (Mechanical, Electrical, Plumbing) drawing based on the following recommendations: "
                f"HVAC: {gemini_parsed.get('hvac_recommendations', 'N/A')}. "
                f"Electrical: {gemini_parsed.get('electrical_notes', 'N/A')}. "
                f"Plumbing: {gemini_parsed.get('plumbing_strategies', 'N/A')}. "
                f"Smart Home: {gemini_parsed.get('smart_home_integration', 'N/A')}. "
                f"The image should be a clear, top-down conceptual diagram, like an architectural sketch, showing basic layouts."
            )
            mep_image_base64 = await self.gemini_service.generate_image(image_prompt)

            if mep_image_base64 is None:
                raise ValueError("Image generation failed for MEP drawing.")

            # Save the base64 image to a file (optional, but good for debugging/storage)
            image_output_path = project_path / "stage_7" / "mep_drawing.png"
            with open(image_output_path, "wb") as f:
                f.write(base64.b64decode(mep_image_base64))

            logger.info(f"{self.name}: Generated MEP drawing Image.")

            return {
                "agent_name": self.name,
                "status": "success",
                "details": "Generated preliminary MEP design and drawing image.",
                "artifacts": [
                    {"type": "preliminary_mep_design", "path": str(json_output_path)},
                    {"type": "mep_drawing_image", "content": mep_image_base64, "path": str(image_output_path)}
                ]
            }

        except Exception as e:
            logger.error(f"{self.name}: Error during MEP design generation: {e}", exc_info=True)
            return {"agent_name": self.name, "status": "error", "message": str(e)}

    