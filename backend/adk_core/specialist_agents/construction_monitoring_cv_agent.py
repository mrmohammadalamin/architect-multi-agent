import json
import logging
from typing import Dict, Any
from pathlib import Path

from ..base_agent import BaseConstructionAgent
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class ConstructionMonitoringCvAgent(BaseConstructionAgent):
    """
    Specialist Agent: Construction Monitoring CV
    Tracks progress from photos and LiDAR data.
    """
    def __init__(self):
        super().__init__(
            name="Construction Monitoring CV Agent",
            description="Simulates construction progress tracking and reporting."
        )
        self.gemini_service = GeminiService()

    async def process_request(self, user_input: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """
        Simulates construction progress tracking and generates a report.
        """
        logger.info(f"{self.name}: Simulating construction progress for {project_path.name}")

        try:
            # 1. Extract data gathered by the workflow engine from previous stages
            project_charter = user_input.get('project_charter', {})
            conceptual_massing_plan = user_input.get('conceptual_massing_plan', {})
            conceptual_floor_plan = user_input.get('conceptual_floor_plan', {})
            bim_cad_documentation_plan = user_input.get('bim_cad_documentation_detailed_plan', {})

            if not all([project_charter, conceptual_massing_plan, conceptual_floor_plan, bim_cad_documentation_plan]):
                raise ValueError("Missing required artifacts from previous stages for construction monitoring.")

            # Extract relevant details for the prompt
            project_type = project_charter.get('project_type', 'building')
            location = project_charter.get('location', 'a site')
            massing_summary = conceptual_massing_plan.get('design_style_summary', 'N/A')
            floor_plan_summary = conceptual_floor_plan.get('layout_summary', 'N/A')
            bim_key_deliverables = bim_cad_documentation_plan.get('documentation_plan', {}).get('key_deliverables', [])

            # 2. Construct a detailed prompt for Gemini
            prompt = (
                f"As a construction monitoring specialist, simulate a progress report for a {project_type} project at {location}. "
                f"Assume the project is currently 30% complete. "
                f"Based on the conceptual massing ({massing_summary}), floor plan ({floor_plan_summary}), and BIM deliverables ({', '.join(bim_key_deliverables)}), "
                f"describe the current state of construction, identify any potential deviations or delays, and suggest next steps. "
                f"Format the output STRICTLY as a JSON object with keys 'progress_summary', 'current_status', 'identified_deviations' (list of strings), 'next_steps' (list of strings)."
            )
            logger.info(f"{self.name}: Calling Gemini for construction progress simulation...")
            gemini_response_str = await self.gemini_service.generate_text(prompt, temperature=0.6)

            if gemini_response_str is None:
                raise ValueError("LLM did not generate a valid response for construction progress.")

            try:
                gemini_parsed = json.loads(gemini_response_str)
            except json.JSONDecodeError:
                logger.error(f"{self.name}: Gemini response was not valid JSON: {gemini_response_str}. Using fallback data.")
                gemini_parsed = {
                    "progress_summary": "Simulated progress report. Manual verification needed.",
                    "current_status": "30% complete, on track.",
                    "identified_deviations": [],
                    "next_steps": ["Continue with structural framing."]
                }

            output_path = project_path / "stage_13" / "construction_progress_report.json"
            with open(output_path, "w") as f:
                json.dump(gemini_parsed, f, indent=4)

            logger.info(f"{self.name}: Generated construction progress report for {project_path.name}.")

            return {
                "agent_name": self.name,
                "status": "success",
                "details": "Generated simulated construction progress report.",
                "artifacts": [
                    {"type": "construction_progress_report", "path": str(output_path)},
                    {"type": "video_url", "url": "https://www.learningcontainer.com/wp-content/uploads/2020/05/sample-mp4-file.mp4"} # Simulated video URL
                ]
            }

        except Exception as e:
            logger.error(f"{self.name}: Error during construction progress simulation: {e}", exc_info=True)
            return {"agent_name": self.name, "status": "error", "message": str(e)}