import json
import logging
import base64
from typing import Dict, Any
from pathlib import Path

from ..base_agent import BaseConstructionAgent
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class StructuralDesignAgent(BaseConstructionAgent):
    """
    Core Agent: Structural Design Agent
    Handles system selection and load calculations.
    """
    def __init__(self):
        super().__init__(
            name="Structural Design Agent",
            description="Generates preliminary structural design considerations."
        )
        self.gemini_service = GeminiService()

    async def process_request(self, user_input: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """
        Generates preliminary structural design based on project data.
        """
        logger.info(f"{self.name}: Generating preliminary structural design for {project_path.name}")

        try:
            # 1. Extract data gathered by the workflow engine from previous stages
            project_charter = user_input.get('project_charter', {})
            constraints = user_input.get('constraints', {})
            geospatial_analysis = user_input.get('geospatial_analysis', {})
            conceptual_floor_plan = user_input.get('conceptual_floor_plan', {})

            if not all([project_charter, constraints, geospatial_analysis, conceptual_floor_plan]):
                raise ValueError("Missing required artifacts from previous stages for structural design.")

            # Extract relevant details for the prompt
            project_type = project_charter.get('project_type', 'building')
            location = project_charter.get('location', 'a site')
            geospatial_summary = geospatial_analysis.get('topography_land_use', 'N/A')
            floor_plan_summary = conceptual_floor_plan.get('layout_summary', 'N/A')

            # 2. Construct a detailed prompt for Gemini
            prompt = (
                f"As a structural engineer, propose preliminary structural design considerations for a {project_type}. "
                f"Consider the location ({location}), geospatial context ({geospatial_summary}), and the conceptual floor plan ({floor_plan_summary}). "
                f"Suggest appropriate foundation types, primary structural systems (e.g., steel, concrete, timber), and any critical load considerations. "
                f"Format output STRICTLY as a JSON object with keys 'foundation_type', 'structural_system', 'load_considerations' (list of strings), and 'notes'."
            )
            logger.info(f"{self.name}: Calling Gemini for structural design interpretation...")
            gemini_response_str = await self.gemini_service.generate_text(prompt, temperature=0.6)

            if gemini_response_str is None:
                raise ValueError("LLM did not generate a valid response for structural design.")

            try:
                gemini_parsed = json.loads(gemini_response_str)
            except json.JSONDecodeError:
                logger.error(f"{self.name}: Gemini response was not valid JSON: {gemini_response_str}. Using fallback data.")
                gemini_parsed = {
                    "foundation_type": "Generic Foundation",
                    "structural_system": "Generic System",
                    "load_considerations": ["Manual review needed."],
                    "notes": "AI parsing failed or response malformed."
                }

            json_output_path = project_path / "stage_7" / "preliminary_structural_design.json"
            with open(json_output_path, "w") as f:
                json.dump(gemini_parsed, f, indent=4)

            logger.info(f"{self.name}: Generated preliminary structural design JSON for {project_path.name}.")

            # Generate Image Structural Drawing
            image_prompt = (
                f"Generate a conceptual structural drawing based on the following: "
                f"Foundation Type: {gemini_parsed.get('foundation_type', 'N/A')}. "
                f"Structural System: {gemini_parsed.get('structural_system', 'N/A')}. "
                f"Load Considerations: {', '.join(gemini_parsed.get('load_considerations', []))}. "
                f"The image should be a clear, conceptual diagram, like an architectural sketch, showing basic structural elements."
            )
            structural_image_base64 = await self.gemini_service.generate_image(image_prompt)

            if structural_image_base64 is None:
                raise ValueError("Image generation failed for structural drawing.")

            # Save the base64 image to a file (optional, but good for debugging/storage)
            image_output_path = project_path / "stage_7" / "structural_drawing.png"
            with open(image_output_path, "wb") as f:
                f.write(base64.b64decode(structural_image_base64))

            logger.info(f"{self.name}: Generated structural drawing Image.")

            return {
                "agent_name": self.name,
                "status": "success",
                "details": "Generated preliminary structural design and drawing image.",
                "artifacts": [
                    {"type": "preliminary_structural_design", "path": str(json_output_path)},
                    {"type": "structural_drawing_image", "content": structural_image_base64, "path": str(image_output_path)}
                ]
            }

        except Exception as e:
            logger.error(f"{self.name}: Error during structural design generation: {e}", exc_info=True)
            return {"agent_name": self.name, "status": "error", "message": str(e)}

    