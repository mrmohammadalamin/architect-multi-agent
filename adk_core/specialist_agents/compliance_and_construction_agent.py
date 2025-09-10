import json
import logging
import base64
from typing import Dict, Any
from pathlib import Path

from ..base_agent import BaseConstructionAgent
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class ComplianceAndConstructionAgent(BaseConstructionAgent):
    """
    Specialist Agent: Compliance and Construction Agent
    Generates compliance sheets, shop drawings, demolition plans, and phasing drawings.
    """
    def __init__(self):
        super().__init__(
            name="Compliance and Construction Agent",
            description="Generates specialized and compliance-related drawings."
        )
        self.gemini_service = GeminiService()

    async def process_request(self, user_input: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """
        Generates various specialized and construction-related drawings.
        """
        logger.info(f"{self.name}: Generating specialized drawings for {project_path.name}")

        try:
            # Inputs from previous stages (placeholders for now)
            conceptual_floor_plan = user_input.get('conceptual_floor_plan', {})
            # Add more inputs as needed, e.g., code requirements, structural details

            if not conceptual_floor_plan:
                raise ValueError("Missing conceptual floor plan for specialized drawings.")

            # Generate Drawings (Images)
            artifacts = []
            details = []

            # Code Compliance Sheet
            code_compliance_prompt = (
                f"Generate a conceptual code compliance sheet image based on the following floor plan summary: "
                f"{conceptual_floor_plan.get('layout_summary', 'N/A')}. "
                f"The image should look like a simplified compliance checklist or summary, focusing on key regulations."
            )
            code_compliance_image_base64 = await self.gemini_service.generate_image(code_compliance_prompt)
            if code_compliance_image_base64:
                code_compliance_path = project_path / "stage_12" / "code_compliance_sheet.png"
                with open(code_compliance_path, "wb") as f:
                    f.write(base64.b64decode(code_compliance_image_base64))
                artifacts.append({"type": "code_compliance_sheet_image", "content": code_compliance_image_base64, "path": str(code_compliance_path)})
                details.append("Generated code compliance sheet image.")

            # Shop Drawing
            shop_drawing_prompt = (
                f"Generate a conceptual shop drawing image based on the following floor plan summary: "
                f"{conceptual_floor_plan.get('layout_summary', 'N/A')}. "
                f"The image should show a detailed view of a specific component or assembly, like a cabinet or a window frame, with basic dimensions."
            )
            shop_drawing_image_base64 = await self.gemini_service.generate_image(shop_drawing_prompt)
            if shop_drawing_image_base64:
                shop_drawing_path = project_path / "stage_12" / "shop_drawing.png"
                with open(shop_drawing_path, "wb") as f:
                    f.write(base64.b64decode(shop_drawing_image_base64))
                artifacts.append({"type": "shop_drawing_image", "content": shop_drawing_image_base64, "path": str(shop_drawing_path)})
                details.append("Generated shop drawing image.")

            # Demolition Plan
            demolition_plan_prompt = (
                f"Generate a conceptual demolition plan image based on the following floor plan summary: "
                f"{conceptual_floor_plan.get('layout_summary', 'N/A')}. "
                f"The image should be a top-down view, highlighting elements to be removed or demolished."
            )
            demolition_plan_image_base64 = await self.gemini_service.generate_image(demolition_plan_prompt)
            if demolition_plan_image_base64:
                demolition_plan_path = project_path / "stage_12" / "demolition_plan.png"
                with open(demolition_plan_path, "wb") as f:
                    f.write(base64.b64decode(demolition_plan_image_base64))
                artifacts.append({"type": "demolition_plan_image", "content": demolition_plan_image_base64, "path": str(demolition_plan_path)})
                details.append("Generated demolition plan image.")

            # Phasing Drawing
            phasing_drawing_prompt = (
                f"Generate a conceptual phasing drawing image for a construction project based on the following floor plan summary: "
                f"{conceptual_floor_plan.get('layout_summary', 'N/A')}. "
                f"The image should show different phases of construction or renovation, indicating areas or stages of work."
            )
            phasing_drawing_image_base64 = await self.gemini_service.generate_image(phasing_drawing_prompt)
            if phasing_drawing_image_base64:
                phasing_drawing_path = project_path / "stage_12" / "phasing_drawing.png"
                with open(phasing_drawing_path, "wb") as f:
                    f.write(base64.b64decode(phasing_drawing_image_base64))
                artifacts.append({"type": "phasing_drawing_image", "content": phasing_drawing_image_base64, "path": str(phasing_drawing_path)})
                details.append("Generated phasing drawing image.")

            return {
                "agent_name": self.name,
                "status": "success",
                "details": " ".join(details),
                "artifacts": artifacts
            }

        except Exception as e:
            logger.error(f"{self.name}: Error during specialized drawing generation: {e}", exc_info=True)
            return {"agent_name": self.name, "status": "error", "message": str(e)}

    
