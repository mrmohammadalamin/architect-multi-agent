import json
import logging
from typing import Dict, Any
from pathlib import Path

from ..base_agent import BaseConstructionAgent
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class CostScheduleAgent(BaseConstructionAgent):
    """
    Core Agent: Cost & Schedule (5D/4D) Agent
    Generates cost and schedule baselines.
    """
    def __init__(self):
        super().__init__(
            name="Cost & Schedule (5D/4D) Agent",
            description="Generates preliminary cost estimates and project schedules."
        )
        self.gemini_service = GeminiService()

    async def process_request(self, user_input: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """
        Generates preliminary cost estimates and project schedules based on project data.
        """
        logger.info(f"{self.name}: Generating cost and schedule baseline for {project_path.name}")

        try:
            # 1. Extract data gathered by the workflow engine from previous stages
            project_charter = user_input.get('project_charter', {})
            constraints = user_input.get('constraints', {})
            geospatial_analysis = user_input.get('geospatial_analysis', {})
            conceptual_massing_plan = user_input.get('conceptual_massing_plan', {})
            conceptual_floor_plan = user_input.get('conceptual_floor_plan', {})
            preliminary_structural_design = user_input.get('preliminary_structural_design', {})
            preliminary_mep_design = user_input.get('preliminary_mep_design', {})

            if not all([project_charter, constraints, geospatial_analysis, conceptual_massing_plan,
                        conceptual_floor_plan, preliminary_structural_design, preliminary_mep_design]):
                raise ValueError("Missing required artifacts from previous stages for cost/schedule generation.")

            # Extract relevant details for the prompt
            project_type = project_charter.get('project_type', 'building')
            budget_range = constraints.get('budget_range', 'N/A')
            location = project_charter.get('location', 'a site')
            massing_summary = conceptual_massing_plan.get('design_style_summary', 'N/A')
            floor_plan_summary = conceptual_floor_plan.get('layout_summary', 'N/A')
            structural_notes = preliminary_structural_design.get('notes', 'N/A')
            mep_notes = preliminary_mep_design.get('notes', 'N/A')

            # 2. Construct a detailed prompt for Gemini
            prompt = (
                f"As a construction cost estimator and project scheduler, provide a preliminary cost estimate and project schedule for a {project_type}. "
                f"Consider the following details:\n\n"
                f"Project Type: {project_type}\n"
                f"Location: {location}\n"
                f"Budget Range: {budget_range}\n"
                f"Massing Summary: {massing_summary}\n"
                f"Floor Plan Summary: {floor_plan_summary}\n"
                f"Structural Design Notes: {structural_notes}\n"
                f"MEP Design Notes: {mep_notes}\n\n"
                f"Break down costs into major categories (e.g., materials, labor, equipment, permits, contingency). "
                f"Provide a high-level schedule with key phases (e.g., design, permitting, procurement, construction, commissioning). "
                f"Format output STRICTLY as a JSON object with keys 'total_estimated_cost_usd', 'cost_breakdown' (object), 'estimated_duration_weeks', 'key_phases' (list of strings)."
            )
            logger.info(f"{self.name}: Calling Gemini for cost and schedule estimation...")
            gemini_response_str = await self.gemini_service.generate_text(prompt, temperature=0.5)

            if gemini_response_str is None:
                raise ValueError("LLM did not generate a valid response for cost/schedule.")

            try:
                gemini_parsed = json.loads(gemini_response_str)
            except json.JSONDecodeError:
                logger.error(f"{self.name}: Gemini response was not valid JSON: {gemini_response_str}. Using fallback data.")
                gemini_parsed = {
                    "total_estimated_cost_usd": 1000000,
                    "cost_breakdown": {"materials": "N/A", "labor": "N/A", "equipment": "N/A", "permits": "N/A", "contingency": "N/A"},
                    "estimated_duration_weeks": 52,
                    "key_phases": ["Design", "Permitting", "Construction", "Commissioning"],
                }

            output_path = project_path / "stage_8" / "cost_schedule_baseline.json"
            with open(output_path, "w") as f:
                json.dump(gemini_parsed, f, indent=4)

            logger.info(f"{self.name}: Generated cost and schedule baseline for {project_path.name}.")

            return {
                "agent_name": self.name,
                "status": "success",
                "details": "Generated preliminary cost estimate and project schedule.",
                "artifacts": [{"type": "cost_schedule_baseline", "path": str(output_path)}]
            }

        except Exception as e:
            logger.error(f"{self.name}: Error during cost/schedule generation: {e}", exc_info=True)
            return {"agent_name": self.name, "status": "error", "message": str(e)}
