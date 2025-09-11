import json
import logging
from typing import Dict, Any
from pathlib import Path

from ..base_agent import BaseConstructionAgent
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class SpacePlanningAdjacencyAgent(BaseConstructionAgent):
    """
    Core Agent: Space Planning & Adjacency Agent
    Produces layout plans from program constraints.
    """
    def __init__(self):
        super().__init__(
            name="Space Planning & Adjacency Agent",
            description="Generates conceptual floor plans and adjacency analysis."
        )
        self.gemini_service = GeminiService()

    async def process_request(self, user_input: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """
        Generates conceptual floor plans and adjacency analysis based on project data.
        """
        logger.info(f"{self.name}: Generating conceptual floor plan for {project_path.name}")

        try:
            # 1. Extract data gathered by the workflow engine from previous stages
            project_charter = user_input.get('project_charter', {})
            constraints = user_input.get('constraints', {})
            geospatial_analysis = user_input.get('geospatial_analysis', {})
            conceptual_massing_plan = user_input.get('conceptual_massing_plan', {})

            if not all([project_charter, constraints, geospatial_analysis, conceptual_massing_plan]):
                raise ValueError("Missing required artifacts from previous stages for floor plan generation.")

            # Extract relevant details for the prompt
            project_type = project_charter.get('project_type', 'building')
            location = project_charter.get('location', 'a site')
            desired_features = constraints.get('desired_features', [])
            geospatial_summary = geospatial_analysis.get('topography_land_use', 'N/A')
            massing_summary = conceptual_massing_plan.get('design_style_summary', 'N/A')

            # 2. Use Gemini to interpret design brief, site constraints, and propose a concept
            prompt = (
                f"As an architect specializing in space planning, propose a conceptual floor plan and adjacency analysis for a {project_type}. "
                f"Consider the location ({location}), desired features ({', '.join(desired_features)}), "
                f"geospatial context ({geospatial_summary}), and the conceptual massing plan ({massing_summary}). "
                f"Focus on functional adjacencies between spaces (e.g., kitchen near dining, bedrooms private). "
                f"Summarize the proposed layout, key adjacencies, and how it addresses program constraints. "
                f"Format output STRICTLY as a JSON object with keys 'layout_summary' (string), 'key_adjacencies' (list of strings), 'space_program_notes' (list of strings)."
            )
            logger.info(f"{self.name}: Calling Gemini for conceptual floor plan interpretation...")
            gemini_response_str = await self.gemini_service.generate_text(prompt, temperature=0.6)

            if gemini_response_str is None:
                raise ValueError("LLM did not generate a valid response for floor plan concept.")

            try:
                gemini_parsed = json.loads(gemini_response_str)
            except json.JSONDecodeError:
                logger.error(f"{self.name}: Gemini response was not valid JSON: {gemini_response_str}. Using fallback data.")
                gemini_parsed = {
                    "layout_summary": "Could not parse layout summary from AI. Manual review needed.",
                    "key_adjacencies": ["Unspecified"],
                    "space_program_notes": ["Manual review. AI parsing failed or response malformed."]
                }

            json_output_path = project_path / "stage_6" / "conceptual_floor_plan.json"
            with open(json_output_path, "w") as f:
                json.dump(gemini_parsed, f, indent=4)

            logger.info(f"{self.name}: Generated conceptual floor plan JSON for {project_path.name}.")

            # Generate Image Floor Plan
            image_prompt = (
                f"Generate a conceptual floor plan image based on the following layout summary: "
                f"{gemini_parsed.get('layout_summary', 'N/A')}. "
                f"Key adjacencies: {', '.join(gemini_parsed.get('key_adjacencies', []))}. "
                f"The image should be a clear, top-down conceptual diagram, like an architectural sketch, showing basic room layouts and connections."
            )
            floor_plan_image_base64 = await self.gemini_service.generate_image(image_prompt)

            if floor_plan_image_base64 is None:
                raise ValueError("Image generation failed for floor plan.")

            # Save the base64 image to a file (optional, but good for debugging/storage)
            image_output_path = project_path / "stage_6" / "floor_plan.png"
            with open(image_output_path, "wb") as f:
                f.write(base64.b64decode(floor_plan_image_base64))

            logger.info(f"{self.name}: Generated floor plan Image.")

            return {
                "agent_name": self.name,
                "status": "success",
                "details": "Generated conceptual floor plan and drawing image.",
                "artifacts": [
                    {"type": "conceptual_floor_plan", "path": str(json_output_path)},
                    {"type": "floor_plan_image", "content": floor_plan_image_base64, "path": str(image_output_path)}
                ]
            }

        except Exception as e:
            logger.error(f"{self.name}: Error during floor plan generation: {e}", exc_info=True)
            return {"agent_name": self.name, "status": "error", "message": str(e)}

    
