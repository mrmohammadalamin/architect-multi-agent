import json
import logging
from typing import Dict, Any
from pathlib import Path

from ..base_agent import BaseConstructionAgent
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class RiskMitigationAgent(BaseConstructionAgent):
    """
    Specialist Agent: Risk Mitigation Agent
    Identifies, assesses, and mitigates project risks based on available data.
    """
    def __init__(self):
        super().__init__(
            name="Risk Mitigation Agent",
            description="Identifies and assesses project risks based on early-stage data."
        )
        self.gemini_service = GeminiService()

    async def process_request(self, user_input: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """
        Performs a preliminary risk assessment based on data from stages 1 and 2.
        """
        logger.info(f"{self.name}: Starting preliminary risk assessment for {project_path.name}")

        try:
            # 1. Extract data gathered by the workflow engine from previous stages
            project_charter = user_input.get('project_charter', {})
            constraints = user_input.get('constraints', {})
            geospatial_analysis = user_input.get('geospatial_analysis', {})
            climate_data = user_input.get('climate_data', {})

            if not all([project_charter, constraints, geospatial_analysis]):
                raise ValueError("Missing required artifacts from previous stages for risk assessment.")

            # 2. Construct a detailed prompt for Gemini
            prompt = (
                f"As a construction project risk manager, conduct a preliminary risk assessment for the following project. "
                f"Your analysis should be based ONLY on the provided data.\n\n"
                f"--- Project Charter ---\n{json.dumps(project_charter, indent=2)}\n\n"
                f"--- Constraints ---\n{json.dumps(constraints, indent=2)}\n\n"
                f"--- Geospatial Analysis ---\n{json.dumps(geospatial_analysis, indent=2)}\n\n"
                f"--- Climate Data Summary ---\nDaily Max Temp Avg: {climate_data.get('daily', {}).get('temperature_2m_max', ['N/A'])[0]} C"
                f"Daily Precip Sum Avg: {climate_data.get('daily', {}).get('precipitation_sum', ['N/A'])[0]} mm\n\n"
                f"Based on this data, identify potential risks. Categorize each risk into one of the following types: "
                f"'Financial', 'Schedule', 'Technical', 'Environmental', or 'Regulatory'. "
                f"For each risk, provide a brief description and a suggested mitigation strategy.\n\n"
                f"Format the output STRICTLY as a JSON object with a single key 'risk_register', which is a list of objects. "
                f"Each object in the list should have three keys: 'risk_description', 'risk_category', and 'mitigation_strategy'."
            )

            # 3. Call Gemini and save the analysis
            analysis_str = await self.gemini_service.generate_text(prompt, temperature=0.5)
            if not analysis_str:
                raise ValueError("Gemini returned no response for risk assessment.")

            # Remove markdown code block fences if present
            if analysis_str.startswith("```json\n") and analysis_str.endswith("\n```"):
                analysis_str = analysis_str[len("```json\n"):-len("\n```")]

            analysis_data = json.loads(analysis_str)

            output_path = project_path / "stage_3" / "risk_assessment_report.json"
            with open(output_path, "w") as f:
                json.dump(analysis_data, f, indent=4)

            logger.info(f"{self.name}: Successfully generated and saved risk assessment report.")

            return {
                "agent_name": self.name,
                "status": "success",
                "details": "Generated preliminary risk assessment report.",
                "artifacts": [{"type": "risk_assessment_report", "path": str(output_path)}]
            }

        except Exception as e:
            logger.error(f"{self.name}: Error during risk assessment: {e}", exc_info=True)
            return {"agent_name": self.name, "status": "error", "message": str(e)}
