import json
import logging
from typing import Dict, Any
from pathlib import Path

from ..base_agent import BaseConstructionAgent
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class ChangeControlClaimsAgent(BaseConstructionAgent):
    """
    Specialist Agent: Change Control & Claims
    Performs automated impact analysis of changes.
    """
    def __init__(self):
        super().__init__(
            name="Change Control & Claims Agent",
            description="Simulates impact analysis for change orders and claims."
        )
        self.gemini_service = GeminiService()

    async def process_request(self, user_input: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """
        Simulates impact analysis for change orders and claims.
        """
        logger.info(f"{self.name}: Simulating change control and claims analysis for {project_path.name}")

        try:
            # 1. Extract data gathered by the workflow engine from previous stages
            project_charter = user_input.get('project_charter', {})
            cost_schedule_baseline = user_input.get('cost_schedule_baseline', {})
            construction_progress_report = user_input.get('construction_progress_report', {})

            if not all([project_charter, cost_schedule_baseline]):
                logger.warning(f"{self.name}: Missing required artifacts from previous stages for change/claims analysis.")
                gemini_parsed = {
                    "change_type": "Generic Change Order",
                    "impact_analysis": {"cost_impact": "Moderate", "schedule_impact": "Minor", "quality_impact": "None"},
                    "management_process": ["Document change", "Assess impact", "Obtain approval", "Execute change"]
                }
            else:
                # Extract relevant details for the prompt
                project_type = project_charter.get('project_type', 'building')
                total_cost = cost_schedule_baseline.get('total_estimated_cost_usd', 'N/A')
                estimated_duration = cost_schedule_baseline.get('estimated_duration_weeks', 'N/A')
                current_progress = construction_progress_report.get('current_status', 'N/A') if construction_progress_report else 'N/A'

                # 2. Construct a detailed prompt for Gemini
                prompt = (
                    f"As a change control and claims specialist, simulate an impact analysis for a hypothetical change order or claim on a {project_type} project. "
                    f"The project has an estimated cost of {total_cost}, duration of {estimated_duration} weeks, and current progress is {current_progress}. "
                    f"Describe a common type of change order (e.g., scope change, unforeseen condition) and analyze its potential impact on cost, schedule, and quality. "
                    f"Suggest a process for managing this change/claim. "
                    f"Format the output STRICTLY as a JSON object with keys 'change_type', 'impact_analysis' (object with 'cost_impact', 'schedule_impact', 'quality_impact'), and 'management_process' (list of strings)."
                )
                logger.info(f"{self.name}: Calling Gemini for change control/claims simulation...")
                gemini_response_str = await self.gemini_service.generate_text(prompt, temperature=0.7)

                if gemini_response_str is None:
                    raise ValueError("LLM did not generate a valid response for change control/claims.")

                try:
                    gemini_parsed = json.loads(gemini_response_str)
                except json.JSONDecodeError:
                    logger.error(f"{self.name}: Gemini response was not valid JSON: {gemini_response_str}. Using fallback data.")
                    gemini_parsed = {
                        "change_type": "Generic Change Order",
                        "impact_analysis": {"cost_impact": "Moderate", "schedule_impact": "Minor", "quality_impact": "None"},
                        "management_process": ["Document change", "Assess impact", "Obtain approval", "Execute change"]
                    }

            output_path = project_path / "stage_16" / "change_claims_impact_analysis.json"
            with open(output_path, "w") as f:
                json.dump(gemini_parsed, f, indent=4)

            logger.info(f"{self.name}: Generated change control and claims analysis for {project_path.name}.")

            return {
                "agent_name": self.name,
                "status": "success",
                "details": "Generated simulated change control and claims analysis.",
                "artifacts": [{"type": "change_claims_impact_analysis", "path": str(output_path)}]
            }

        except Exception as e:
            logger.error(f"{self.name}: Error during change control/claims simulation: {e}", exc_info=True)
            return {"agent_name": self.name, "status": "error", "message": str(e)}