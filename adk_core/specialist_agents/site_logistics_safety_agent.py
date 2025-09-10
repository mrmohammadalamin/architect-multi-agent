import json
import logging
from typing import Dict, Any
from pathlib import Path

from ..base_agent import BaseConstructionAgent
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class SiteLogisticsSafetyAgent(BaseConstructionAgent):
    """
    Specialist Agent: Site Logistics & Safety
    Performs site simulations and safety analysis.
    """
    def __init__(self):
        super().__init__(
            name="Site Logistics & Safety Agent",
            description="Generates preliminary site logistics and safety plans."
        )
        self.gemini_service = GeminiService()

    async def process_request(self, user_input: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """
        Generates preliminary site logistics and safety plans based on project data.
        """
        logger.info(f"{self.name}: Generating preliminary site logistics and safety plan for {project_path.name}")

        try:
            # 1. Extract data gathered by the workflow engine from previous stages
            project_charter = user_input.get('project_charter', {})
            constraints = user_input.get('constraints', {})
            geospatial_analysis = user_input.get('geospatial_analysis', {})
            conceptual_massing_plan = user_input.get('conceptual_massing_plan', {})
            conceptual_floor_plan = user_input.get('conceptual_floor_plan', {})
            preliminary_procurement_plan = user_input.get('preliminary_procurement_plan', {})

            if not all([project_charter, constraints, geospatial_analysis, conceptual_massing_plan,
                        conceptual_floor_plan]):
                raise ValueError("Missing required artifacts from previous stages for site logistics/safety plan.")

            # Extract relevant details for the prompt
            project_type = project_charter.get('project_type', 'building')
            location = project_charter.get('location', 'a site')
            geospatial_summary = geospatial_analysis.get('topography_land_use', 'N/A')
            massing_summary = conceptual_massing_plan.get('design_style_summary', 'N/A')
            floor_plan_summary = conceptual_floor_plan.get('layout_summary', 'N/A')
            procurement_strategy = preliminary_procurement_plan.get('procurement_strategy_summary', 'N/A') if preliminary_procurement_plan else 'N/A'

            # 2. Construct a detailed prompt for Gemini
            prompt = (
                f"As a site logistics and safety planner, propose a preliminary plan for a {project_type} project. "
                f"Consider the location ({location}), geospatial context ({geospatial_summary}), massing ({massing_summary}), "
                f"floor plan ({floor_plan_summary}), and procurement strategy ({procurement_strategy}). "
                f"Outline strategies for site access, material laydown, waste management, and key safety considerations. "
                f"Format the output STRICTLY as a JSON object with keys 'logistics_summary', 'site_access_plan', 'material_waste_management', 'safety_considerations'."
            )
            logger.info(f"{self.name}: Calling Gemini for site logistics and safety plan generation...")
            gemini_response_str = await self.gemini_service.generate_text(prompt, temperature=0.6)

            if gemini_response_str is None:
                raise ValueError("LLM did not generate a valid response for site logistics/safety plan.")

            try:
                gemini_parsed = json.loads(gemini_response_str)
            except json.JSONDecodeError:
                logger.error(f"{self.name}: Gemini response was not valid JSON: {gemini_response_str}. Using fallback data.")
                gemini_parsed = {
                    "logistics_summary": "Generic logistics plan due to parsing error.",
                    "site_access_plan": "Standard site access.",
                    "material_waste_management": "Standard waste management.",
                    "safety_considerations": "General safety considerations."
                }

            output_path = project_path / "stage_12" / "site_logistics_safety_plan.json"
            with open(output_path, "w") as f:
                json.dump(gemini_parsed, f, indent=4)

            logger.info(f"{self.name}: Generated preliminary site logistics and safety plan for {project_path.name}.")

            return {
                "agent_name": self.name,
                "status": "success",
                "details": "Generated preliminary site logistics and safety plan.",
                "artifacts": [{"type": "site_logistics_safety_plan", "path": str(output_path)}]
            }

        except Exception as e:
            logger.error(f"{self.name}: Error during site logistics/safety plan generation: {e}", exc_info=True)
            return {"agent_name": self.name, "status": "error", "message": str(e)}