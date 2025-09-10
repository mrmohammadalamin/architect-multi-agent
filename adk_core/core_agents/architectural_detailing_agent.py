import json
import logging
import base64
from typing import Dict, Any
from pathlib import Path

from ..base_agent import BaseConstructionAgent
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class ArchitecturalDetailingAgent(BaseConstructionAgent):
    """
    Core Agent: Architectural Detailing Agent
    Generates detailed architectural drawings like elevations, sections, and roof plans.
    """
    def __init__(self):
        super().__init__(
            name="Architectural Detailing Agent",
            description="Generates detailed architectural drawings."
        )
        self.gemini_service = GeminiService()

    async def process_request(self, user_input: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """
        Generates detailed drawings based on conceptual plans.
        """
        logger.info(f"{self.name}: Generating architectural details for {project_path.name}")

        try:
            # Inputs from previous stages (placeholders for now)
            conceptual_floor_plan = user_input.get('conceptual_floor_plan', {})
            conceptual_massing_plan = user_input.get('conceptual_massing_plan', {})

            if not all([conceptual_floor_plan, conceptual_massing_plan]):
                raise ValueError("Missing required artifacts for detailing.")

            # Generate Drawings (Images)
            artifacts = []
            details = []

            # Elevation Drawing
            elevation_prompt = (
                f"Generate a conceptual architectural elevation drawing for a building with a design style of "
                f"{conceptual_massing_plan.get('design_style_summary', 'N/A')}. "
                f"The image should show the exterior facade, windows, and doors from a straight-on perspective. "
                f"Focus on the overall form and aesthetic."
            )
            elevation_image_base64 = await self.gemini_service.generate_image(elevation_prompt)
            if elevation_image_base64:
                elevation_path = project_path / "stage_8" / "elevation_drawing.png"
                with open(elevation_path, "wb") as f:
                    f.write(base64.b64decode(elevation_image_base64))
                artifacts.append({"type": "elevation_drawing_image", "content": elevation_image_base64, "path": str(elevation_path)})
                details.append("Generated elevation drawing image.")

            # Cross-Section Drawing
            cross_section_prompt = (
                f"Generate a conceptual architectural cross-section drawing for a building with a layout summary of "
                f"{conceptual_floor_plan.get('layout_summary', 'N/A')}. "
                f"The image should show a vertical cut through the building, revealing internal spaces, floor levels, and roof structure. "
                f"Focus on spatial relationships and structural elements."
            )
            cross_section_image_base64 = await self.gemini_service.generate_image(cross_section_prompt)
            if cross_section_image_base64:
                cross_section_path = project_path / "stage_8" / "cross_section_drawing.png"
                with open(cross_section_path, "wb") as f:
                    f.write(base64.b64decode(cross_section_image_base64))
                artifacts.append({"type": "cross_section_drawing_image", "content": cross_section_image_base64, "path": str(cross_section_path)})
                details.append("Generated cross-section drawing image.")

            # Roof Plan Drawing
            roof_plan_prompt = (
                f"Generate a conceptual architectural roof plan drawing for a building with a design style of "
                f"{conceptual_massing_plan.get('design_style_summary', 'N/A')}. "
                f"The image should be a top-down view of the roof, showing its shape, slopes, and any major features like skylights or vents. "
                f"Focus on the roof geometry."
            )
            roof_plan_image_base64 = await self.gemini_service.generate_image(roof_plan_prompt)
            if roof_plan_image_base64:
                roof_plan_path = project_path / "stage_8" / "roof_plan_drawing.png"
                with open(roof_plan_path, "wb") as f:
                    f.write(base64.b64decode(roof_plan_image_base64))
                artifacts.append({"type": "roof_plan_drawing_image", "content": roof_plan_image_base64, "path": str(roof_plan_path)})
                details.append("Generated roof plan drawing image.")

            return {
                "agent_name": self.name,
                "status": "success",
                "details": " ".join(details),
                "artifacts": artifacts
            }

        except Exception as e:
            logger.error(f"{self.name}: Error during architectural detailing: {e}", exc_info=True)
            return {"agent_name": self.name, "status": "error", "message": str(e)}

    
