import json
import logging
import base64
from typing import Dict, Any
from pathlib import Path

from ..base_agent import BaseConstructionAgent
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class InteriorDesignAgent(BaseConstructionAgent):
    """
    Core Agent: Interior Design Agent
    Generates interior design drawings like furniture layouts, RCPs, and interior elevations.
    """
    def __init__(self):
        super().__init__(
            name="Interior Design Agent",
            description="Generates interior design drawings."
        )
        self.gemini_service = GeminiService()

    async def process_request(self, user_input: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """
        Generates interior design drawings based on conceptual plans and user input.
        """
        logger.info(f"{self.name}: Generating interior design details for {project_path.name}")

        try:
            # Inputs from previous stages (placeholders for now)
            conceptual_floor_plan = user_input.get('conceptual_floor_plan', {})
            # Add more inputs as needed, e.g., client preferences, design brief

            if not conceptual_floor_plan:
                raise ValueError("Missing conceptual floor plan for interior design.")

            # Generate Drawings (Images)
            artifacts = []
            details = []

            # Furniture Layout Plan
            furniture_layout_prompt = (
                f"Generate a conceptual furniture layout plan image based on the following floor plan summary: "
                f"{conceptual_floor_plan.get('layout_summary', 'N/A')}. "
                f"The image should be a top-down view, showing basic furniture arrangements within rooms."
            )
            furniture_layout_image_base64 = await self.gemini_service.generate_image(furniture_layout_prompt)
            if furniture_layout_image_base64:
                furniture_layout_path = project_path / "stage_6" / "furniture_layout.png"
                with open(furniture_layout_path, "wb") as f:
                    f.write(base64.b64decode(furniture_layout_image_base64))
                artifacts.append({"type": "furniture_layout_image", "content": furniture_layout_image_base64, "path": str(furniture_layout_path)})
                details.append("Generated furniture layout image.")

            # Reflected Ceiling Plan (RCP)
            rcp_prompt = (
                f"Generate a conceptual Reflected Ceiling Plan (RCP) image based on the following floor plan summary: "
                f"{conceptual_floor_plan.get('layout_summary', 'N/A')}. "
                f"The image should be a top-down view, showing ceiling elements like lights, vents, and ceiling changes."
            )
            rcp_image_base64 = await self.gemini_service.generate_image(rcp_prompt)
            if rcp_image_base64:
                rcp_path = project_path / "stage_6" / "rcp_drawing.png"
                with open(rcp_path, "wb") as f:
                    f.write(base64.b64decode(rcp_image_base64))
                artifacts.append({"type": "rcp_drawing_image", "content": rcp_image_base64, "path": str(rcp_path)})
                details.append("Generated RCP drawing image.")

            # Interior Elevation
            interior_elevation_prompt = (
                f"Generate a conceptual interior elevation image based on the following floor plan summary: "
                f"{conceptual_floor_plan.get('layout_summary', 'N/A')}. "
                f"The image should show a straight-on view of an interior wall, including windows, doors, and built-in elements."
            )
            interior_elevation_image_base64 = await self.gemini_service.generate_image(interior_elevation_prompt)
            if interior_elevation_image_base64:
                interior_elevation_path = project_path / "stage_6" / "interior_elevation.png"
                with open(interior_elevation_path, "wb") as f:
                    f.write(base64.b64decode(interior_elevation_image_base64))
                artifacts.append({"type": "interior_elevation_image", "content": interior_elevation_image_base64, "path": str(interior_elevation_path)})
                details.append("Generated interior elevation image.")

            # Lighting Plan
            lighting_plan_prompt = (
                f"Generate a conceptual lighting plan image based on the following floor plan summary: "
                f"{conceptual_floor_plan.get('layout_summary', 'N/A')}. "
                f"The image should be a top-down view, showing the placement of various light fixtures."
            )
            lighting_plan_image_base64 = await self.gemini_service.generate_image(lighting_plan_prompt)
            if lighting_plan_image_base64:
                lighting_plan_path = project_path / "stage_6" / "lighting_plan.png"
                with open(lighting_plan_path, "wb") as f:
                    f.write(base64.b64decode(lighting_plan_image_base64))
                artifacts.append({"type": "lighting_plan_image", "content": lighting_plan_image_base64, "path": str(lighting_plan_path)})
                details.append("Generated lighting plan image.")

            # Finishing Schedule and Drawings
            finishing_schedule_prompt = (
                f"Generate a conceptual finishing schedule image based on the following floor plan summary: "
                f"{conceptual_floor_plan.get('layout_summary', 'N/A')}. "
                f"The image should be a table or list format, detailing finishes for floors, walls, and ceilings in different rooms."
            )
            finishing_schedule_image_base64 = await self.gemini_service.generate_image(finishing_schedule_prompt)
            if finishing_schedule_image_base64:
                finishing_schedule_path = project_path / "stage_6" / "finishing_schedule.png"
                with open(finishing_schedule_path, "wb") as f:
                    f.write(base64.b64decode(finishing_schedule_image_base64))
                artifacts.append({"type": "finishing_schedule_image", "content": finishing_schedule_image_base64, "path": str(finishing_schedule_path)})
                details.append("Generated finishing schedule image.")

            # Millwork/Casework Drawings
            millwork_drawing_prompt = (
                f"Generate a conceptual millwork/casework drawing image based on the following floor plan summary: "
                f"{conceptual_floor_plan.get('layout_summary', 'N/A')}. "
                f"The image should show detailed views of custom cabinetry or built-in furniture."
            )
            millwork_drawing_image_base64 = await self.gemini_service.generate_image(millwork_drawing_prompt)
            if millwork_drawing_image_base64:
                millwork_drawing_path = project_path / "stage_6" / "millwork_drawing.png"
                with open(millwork_drawing_path, "wb") as f:
                    f.write(base64.b64decode(millwork_drawing_image_base64))
                artifacts.append({"type": "millwork_drawing_image", "content": millwork_drawing_image_base64, "path": str(millwork_drawing_path)})
                details.append("Generated millwork drawing image.")

            # Interior Plumbing and Electrical Layouts
            interior_plumbing_electrical_layout_prompt = (
                f"Generate a conceptual interior plumbing and electrical layout image based on the following floor plan summary: "
                f"{conceptual_floor_plan.get('layout_summary', 'N/A')}. "
                f"The image should be a top-down view, showing the placement of interior plumbing fixtures and electrical outlets/switches."
            )
            interior_plumbing_electrical_layout_image_base64 = await self.gemini_service.generate_image(interior_plumbing_electrical_layout_prompt)
            if interior_plumbing_electrical_layout_image_base64:
                interior_plumbing_electrical_layout_path = project_path / "stage_6" / "interior_plumbing_electrical_layout.png"
                with open(interior_plumbing_electrical_layout_path, "wb") as f:
                    f.write(base64.b64decode(interior_plumbing_electrical_layout_image_base64))
                artifacts.append({"type": "interior_plumbing_electrical_layout_image", "content": interior_plumbing_electrical_layout_image_base64, "path": str(interior_plumbing_electrical_layout_path)})
                details.append("Generated interior plumbing and electrical layout image.")

            return {
                "agent_name": self.name,
                "status": "success",
                "details": " ".join(details),
                "artifacts": artifacts
            }

        except Exception as e:
            logger.error(f"{self.name}: Error during interior design generation: {e}", exc_info=True)
            return {"agent_name": self.name, "status": "error", "message": str(e)}

    
