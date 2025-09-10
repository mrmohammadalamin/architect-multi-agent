import json
import logging
from typing import Dict, Any
from pathlib import Path

from ..base_agent import BaseConstructionAgent
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class SustainabilityEnergyAgent(BaseConstructionAgent):
    """
    Core Agent: Sustainability & Energy Agent
    Performs energy simulations and carbon tracking.
    """
    def __init__(self):
        super().__init__(
            name="Sustainability & Energy Agent",
            description="Generates preliminary sustainability and energy analysis."
        )
        self.gemini_service = GeminiService()

    async def process_request(self, user_input: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """
        Generates preliminary sustainability and energy analysis based on project data.
        """
        logger.info(f"{self.name}: Generating preliminary sustainability and energy analysis for {project_path.name}")

        try:
            # 1. Extract data gathered by the workflow engine from previous stages
            project_charter = user_input.get('project_charter', {})
            constraints = user_input.get('constraints', {})
            climate_data = user_input.get('climate_data', {})
            conceptual_massing_plan = user_input.get('conceptual_massing_plan', {})
            conceptual_floor_plan = user_input.get('conceptual_floor_plan', {})
            preliminary_mep_design = user_input.get('preliminary_mep_design', {})

            if not all([project_charter, constraints, climate_data, conceptual_massing_plan,
                        conceptual_floor_plan]):
                raise ValueError("Missing required artifacts from previous stages for sustainability analysis.")

            # Extract relevant details for the prompt
            project_type = project_charter.get('project_type', 'building')
            location = project_charter.get('location', 'a site')
            climate_summary = climate_data.get('daily', {}).get('weather_code', ['N/A'])[0]
            massing_summary = conceptual_massing_plan.get('design_style_summary', 'N/A')
            floor_plan_summary = conceptual_floor_plan.get('layout_summary', 'N/A')
            mep_hvac = preliminary_mep_design.get('hvac_recommendations', 'N/A') if preliminary_mep_design else 'N/A'

            # 2. Construct a detailed prompt for Gemini
            prompt = (
                f"As a sustainability and energy consultant, provide a preliminary analysis for a {project_type} project. "
                f"Consider the location ({location}), climate ({climate_summary}), massing ({massing_summary}), "
                f"floor plan ({floor_plan_summary}), and proposed HVAC system ({mep_hvac}). "
                f"Identify key opportunities for energy efficiency, water conservation, and material sustainability. "
                f"Suggest potential green building certifications. "
                f"Format the output STRICTLY as a JSON object with keys 'energy_efficiency_opportunities', 'water_conservation_strategies', 'material_sustainability_notes', 'potential_certifications'."
            )
            logger.info(f"{self.name}: Calling Gemini for sustainability and energy analysis...")
            gemini_response_str = await self.gemini_service.generate_text(prompt, temperature=0.6)

            if gemini_response_str is None:
                raise ValueError("LLM did not generate a valid response for sustainability analysis.")

            try:
                gemini_parsed = json.loads(gemini_response_str)
            except json.JSONDecodeError:
                logger.error(f"{self.name}: Gemini response was not valid JSON: {gemini_response_str}. Using fallback data.")
                gemini_parsed = {
                    "energy_efficiency_opportunities": ["High-performance insulation", "LED lighting"],
                    "water_conservation_strategies": ["Low-flow fixtures", "Rainwater harvesting"],
                    "material_sustainability_notes": ["Recycled content materials", "Locally sourced materials"],
                    "potential_certifications": ["LEED", "BREEAM"]
                }

            output_path = project_path / "stage_15" / "sustainability_energy_analysis.json"
            with open(output_path, "w") as f:
                json.dump(gemini_parsed, f, indent=4)

            logger.info(f"{self.name}: Generated preliminary sustainability and energy analysis for {project_path.name}.")

            return {
                "agent_name": self.name,
                "status": "success",
                "details": "Generated preliminary sustainability and energy analysis.",
                "artifacts": [{"type": "sustainability_energy_analysis", "path": str(output_path)}]
            }

        except Exception as e:
            logger.error(f"{self.name}: Error during sustainability and energy analysis: {e}", exc_info=True)
            return {"agent_name": self.name, "status": "error", "message": str(e)}
