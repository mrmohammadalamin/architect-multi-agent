import json
import logging
from typing import Dict, Any
from pathlib import Path

from ..base_agent import BaseConstructionAgent
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class OptioneeringStrategyAgent(BaseConstructionAgent):
    """
    Core Agent: Optioneering & Strategy Agent
    Generates multi-objective project strategies based on project data.
    """
    def __init__(self):
        super().__init__(
            name="Optioneering & Strategy Agent",
            description="Generates multiple strategic options for the project."
        )
        self.gemini_service = GeminiService()

    async def process_request(self, user_input: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """
        Generates strategic options for the project based on gathered data.
        """
        logger.info(f"{self.name}: Generating strategic options for {project_path.name}")

        try:
            # 1. Extract data gathered by the workflow engine from previous stages
            project_charter = user_input.get('project_charter', {})
            constraints = user_input.get('constraints', {})
            geospatial_analysis = user_input.get('geospatial_analysis', {})
            risk_assessment_report = user_input.get('risk_assessment_report', {})

            if not all([project_charter, constraints, geospatial_analysis, risk_assessment_report]):
                raise ValueError("Missing required artifacts from previous stages for strategy generation.")

            # 2. Construct a detailed prompt for Gemini
            prompt = (
                f"As a strategic consultant for construction projects, propose 3-5 distinct strategic options for the following project. "
                f"Each option should have a brief description and highlight its primary focus (e.g., 'Cost Optimization', 'Speed to Market', 'Sustainability Leadership', 'Risk Minimization'). "
                f"Consider the project charter, constraints, geospatial analysis, and initial risk assessment.\n\n"
                f"--- Project Charter ---\n{json.dumps(project_charter, indent=2)}\n\n"
                f"--- Constraints ---\n{json.dumps(constraints, indent=2)}\n\n"
                f"--- Geospatial Analysis ---\n{json.dumps(geospatial_analysis, indent=2)}\n\n"
                f"--- Risk Assessment Summary ---\n{json.dumps(risk_assessment_report, indent=2)}\n\n"
                f"Format the output STRICTLY as a JSON object with a single key 'strategic_options', which is a list of objects. "
                f"Each object in the list should have three keys: 'option_name', 'focus', and 'description'."
            )

            # 3. Call Gemini and save the analysis
            options_str = await self.gemini_service.generate_text(prompt, temperature=0.7)
            if not options_str:
                raise ValueError("Gemini returned no response for strategic options.")

            # Remove markdown code block fences if present
            if options_str.startswith("```json\n") and options_str.endswith("\n```"):
                options_str = options_str[len("```json\n"):-len("\n```")]

            options_data = json.loads(options_str)

            output_path = project_path / "stage_4" / "strategic_options.json"
            with open(output_path, "w") as f:
                json.dump(options_data, f, indent=4)

            logger.info(f"{self.name}: Successfully generated and saved strategic options.")

            return {
                "agent_name": self.name,
                "status": "success",
                "details": "Generated strategic options for the project.",
                "artifacts": [{"type": "strategic_options", "path": str(output_path)}]
            }

        except Exception as e:
            logger.error(f"{self.name}: Error during strategic options generation: {e}", exc_info=True)
            return {"agent_name": self.name, "status": "error", "message": str(e)}