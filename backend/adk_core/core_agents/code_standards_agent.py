import json
import logging
from typing import Dict, Any
from pathlib import Path

from ..base_agent import BaseConstructionAgent
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class CodeStandardsAgent(BaseConstructionAgent):
    """
    Core Agent: Code & Standards Agent
    Parses regulations and performs automated compliance checks.
    """
    def __init__(self):
        super().__init__(
            name="Code & Standards Agent",
            description="Simulates compliance checks against relevant building codes and standards."
        )
        self.gemini_service = GeminiService()

    async def process_request(self, user_input: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """
        Simulates compliance checks and generates a report.
        """
        logger.info(f"{self.name}: Simulating compliance check for {project_path.name}")

        try:
            # 1. Extract data gathered by the workflow engine from previous stages
            project_charter = user_input.get('project_charter', {})
            constraints = user_input.get('constraints', {})
            geospatial_analysis = user_input.get('geospatial_analysis', {})
            bim_cad_documentation_plan = user_input.get('bim_cad_documentation_detailed_plan', {})

            if not all([project_charter, constraints, geospatial_analysis, bim_cad_documentation_plan]):
                raise ValueError("Missing required artifacts from previous stages for compliance check.")

            # Extract relevant details for the prompt
            project_type = project_charter.get('project_type', 'building')
            location = project_charter.get('location', 'a site')
            geospatial_summary = geospatial_analysis.get('environmental_risks', 'N/A')
            documentation_types = bim_cad_documentation_plan.get('documentation_plan', {}).get('documentation_types', [])

            # 2. Construct a detailed prompt for Gemini
            prompt = (
                f"As a building code and standards compliance officer, simulate a compliance check report for a {project_type} project. "
                f"Consider the project's location ({location}), potential environmental risks ({geospatial_summary}), and the types of documentation available ({', '.join(documentation_types)}). "
                f"Identify common compliance areas (e.g., fire safety, accessibility, energy efficiency, zoning) and potential challenges. "
                f"Format the output STRICTLY as a JSON object with keys 'compliance_summary', 'identified_areas' (list of strings), 'potential_challenges' (list of strings), and 'recommendations' (list of strings)."
            )
            logger.info(f"{self.name}: Calling Gemini for compliance check simulation...")
            gemini_response_str = await self.gemini_service.generate_text(prompt, temperature=0.6)

            if gemini_response_str is None:
                raise ValueError("LLM did not generate a valid response for compliance check.")

            try:
                gemini_parsed = json.loads(gemini_response_str)
            except json.JSONDecodeError:
                logger.error(f"{self.name}: Gemini response was not valid JSON: {gemini_response_str}. Using fallback data.")
                gemini_parsed = {
                    "compliance_summary": "Simulated compliance report. Manual review needed.",
                    "identified_areas": ["Fire Safety", "Accessibility"],
                    "potential_challenges": ["Local zoning variations"],
                    "recommendations": ["Consult local building authority."]
                }

            output_path = project_path / "stage_10" / "compliance_check_report.json"
            with open(output_path, "w") as f:
                json.dump(gemini_parsed, f, indent=4)

            logger.info(f"{self.name}: Generated compliance check report for {project_path.name}.")

            return {
                "agent_name": self.name,
                "status": "success",
                "details": "Generated simulated compliance check report.",
                "artifacts": [{"type": "compliance_check_report", "path": str(output_path)}]
            }

        except Exception as e:
            logger.error(f"{self.name}: Error during compliance check simulation: {e}", exc_info=True)
            return {"agent_name": self.name, "status": "error", "message": str(e)}