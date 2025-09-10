import json
import logging
from typing import Dict, Any
from pathlib import Path

from ..base_agent import BaseConstructionAgent
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class VisualizationAgent(BaseConstructionAgent):
    """
    Specialist Agent: Visualization Agent
    Generates 3D renderings and virtual tours.
    """
    def __init__(self):
        super().__init__(
            name="Visualization Agent",
            description="Generates 3D renderings and virtual tours."
        )
        self.gemini_service = GeminiService()

    async def process_request(self, user_input: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """
        Generates 3D renderings and virtual tours based on project data.
        """
        logger.info(f"{self.name}: Generating visualizations for {project_path.name}")

        try:
            # Inputs from previous stages (placeholders for now)
            conceptual_massing_plan = user_input.get('conceptual_massing_plan', {})
            conceptual_floor_plan = user_input.get('conceptual_floor_plan', {})

            if not all([conceptual_massing_plan, conceptual_floor_plan]):
                raise ValueError("Missing required artifacts for visualization.")

            # Generate Visualizations
            # For now, these will be placeholder images/URLs
            rendering_url = self._create_3d_rendering(conceptual_massing_plan)
            virtual_tour_url = self._create_virtual_tour(conceptual_floor_plan)
            virtual_tour_data = {"url": virtual_tour_url, "description": "Conceptual Virtual Tour"}
            virtual_tour_path = project_path / "stage_10" / "virtual_tour.json"
            with open(virtual_tour_path, "w") as f:
                json.dump(virtual_tour_data, f, indent=4)
            artifacts.append({"type": "virtual_tour", "path": str(virtual_tour_path)})
            details.append("Generated virtual tour.")

            # New Visualization and Presentation Tools
            mood_board_url = self._create_mood_board(conceptual_floor_plan)
            mood_board_data = {"url": mood_board_url, "description": "Conceptual Mood Board"}
            mood_board_path = project_path / "stage_10" / "mood_board.json"
            with open(mood_board_path, "w") as f:
                json.dump(mood_board_data, f, indent=4)
            artifacts.append({"type": "mood_board", "path": str(mood_board_path)})
            details.append("Generated mood board.")

            conceptual_sketch_url = self._create_3d_conceptual_sketch(conceptual_massing_plan)
            conceptual_sketch_data = {"url": conceptual_sketch_url, "description": "3D Conceptual Sketch"}
            conceptual_sketch_path = project_path / "stage_10" / "3d_conceptual_sketch.json"
            with open(conceptual_sketch_path, "w") as f:
                json.dump(conceptual_sketch_data, f, indent=4)
            artifacts.append({"type": "3d_conceptual_sketch", "path": str(conceptual_sketch_path)})
            details.append("Generated 3D conceptual sketch.")

            photorealistic_rendering_url = self._create_photorealistic_rendering(conceptual_massing_plan)
            photorealistic_rendering_data = {"url": photorealistic_rendering_url, "description": "Photorealistic Rendering"}
            photorealistic_rendering_path = project_path / "stage_10" / "photorealistic_rendering.json"
            with open(photorealistic_rendering_path, "w") as f:
                json.dump(photorealistic_rendering_data, f, indent=4)
            artifacts.append({"type": "photorealistic_rendering", "path": str(photorealistic_rendering_path)})
            details.append("Generated photorealistic rendering.")

            vr_walkthrough_url = self._create_vr_walkthrough(conceptual_floor_plan)
            vr_walkthrough_data = {"url": vr_walkthrough_url, "description": "VR Walkthrough"}
            vr_walkthrough_path = project_path / "stage_10" / "vr_walkthrough.json"
            with open(vr_walkthrough_path, "w") as f:
                json.dump(vr_walkthrough_data, f, indent=4)
            artifacts.append({"type": "vr_walkthrough", "path": str(vr_walkthrough_path)})
            details.append("Generated VR walkthrough.")

            return {
                "agent_name": self.name,
                "status": "success",
                "details": " ".join(details),
                "artifacts": artifacts
            }

        except Exception as e:
            logger.error(f"{self.name}: Error during visualization generation: {e}", exc_info=True)
            return {"agent_name": self.name, "status": "error", "message": str(e)}

    def _create_3d_rendering(self, massing_plan: Dict[str, Any]) -> str:
        """Creates a placeholder URL for a 3D rendering."""
        style = massing_plan.get('design_style_summary', 'Modern')
        return f"https://placehold.co/600x400/FF00FF/FFFFFF?text=3D_Rendering_{style.replace(' ', '_')}"

    def _create_virtual_tour(self, floor_plan: Dict[str, Any]) -> str:
        """Creates a placeholder URL for a virtual tour."""
        layout_summary = floor_plan.get('layout_summary', 'Basic layout')
        return f"https://placehold.co/600x400/00FFFF/000000?text=Virtual_Tour_{layout_summary.replace(' ', '_')}"

    def _create_mood_board(self, floor_plan: Dict[str, Any]) -> str:
        """Creates a placeholder URL for a mood board."""
        layout_summary = floor_plan.get('layout_summary', 'Basic layout')
        return f"https://placehold.co/600x400/FFD700/000000?text=Mood_Board_{layout_summary.replace(' ', '_')}"

    def _create_3d_conceptual_sketch(self, massing_plan: Dict[str, Any]) -> str:
        """Creates a placeholder URL for a 3D conceptual sketch."""
        style = massing_plan.get('design_style_summary', 'Modern')
        return f"https://placehold.co/600x400/800080/FFFFFF?text=3D_Conceptual_Sketch_{style.replace(' ', '_')}"

    def _create_photorealistic_rendering(self, massing_plan: Dict[str, Any]) -> str:
        """Creates a placeholder URL for a photorealistic rendering."""
        style = massing_plan.get('design_style_summary', 'Modern')
        return f"https://placehold.co/600x400/008080/FFFFFF?text=Photorealistic_Rendering_{style.replace(' ', '_')}"

    def _create_vr_walkthrough(self, floor_plan: Dict[str, Any]) -> str:
        """Creates a placeholder URL for a VR walkthrough."""
        layout_summary = floor_plan.get('layout_summary', 'Basic layout')
        return f"https://placehold.co/600x400/4682B4/FFFFFF?text=VR_Walkthrough_{layout_summary.replace(' ', '_')}"
