import json
import logging
from typing import Dict, Any
from pathlib import Path

from ..base_agent import BaseConstructionAgent
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class ClashCoordinationAgent(BaseConstructionAgent):
    """
    Core Agent: Clash & Coordination Agent
    Federates models and resolves clashes.
    """
    def __init__(self):
        super().__init__(
            name="Clash & Coordination Agent",
            description="Simulates clash detection and coordination based on BIM/CAD documentation."
        )
        self.gemini_service = GeminiService()

    async def process_request(self, user_input: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """
        Simulates clash detection and coordination.
        """
        logger.info(f"{self.name}: Simulating clash detection for {project_path.name}")

        try:
            # 1. Extract data gathered by the workflow engine from previous stages
            bim_cad_documentation_plan = user_input.get('bim_cad_documentation_detailed_plan', {})

            if not bim_cad_documentation_plan:
                raise ValueError("Missing BIM/CAD documentation plan for clash detection.")

            # Extract relevant details for the prompt
            documentation_types = bim_cad_documentation_plan.get('documentation_plan', {}).get('documentation_types', [])
            suggested_lod = bim_cad_documentation_plan.get('documentation_plan', {}).get('suggested_lod', 'N/A')

            # 2. Construct a detailed prompt for Gemini
            prompt = (
                f"As a BIM coordinator and clash detection specialist, simulate a clash detection report for a project with the following documentation plan: "
                f"Documentation Types: {', '.join(documentation_types)}. Suggested LOD: {suggested_lod}. "
                f"Identify potential clashes between disciplines (e.g., MEP vs. Structural, Architectural vs. Structural). "
                f"Suggest a few common clash types and their potential resolutions. "
                f"Format the output STRICTLY as a JSON object with keys 'clash_summary', 'identified_clashes' (list of objects with 'type', 'location', 'disciplines_involved'), and 'suggested_resolutions' (list of strings)."
            )
            logger.info(f"{self.name}: Calling Gemini for clash detection simulation...")
            gemini_response_str = await self.gemini_service.generate_text(prompt, temperature=0.7)

            if gemini_response_str is None:
                raise ValueError("LLM did not generate a valid response for clash detection.")

            try:
                gemini_parsed = json.loads(gemini_response_str)
            except json.JSONDecodeError:
                logger.error(f"{self.name}: Gemini response was not valid JSON: {gemini_response_str}. Using fallback data.")
                gemini_parsed = {
                    "clash_summary": "Simulated clash detection report. Manual review needed.",
                    "identified_clashes": [],
                    "suggested_resolutions": ["Review BIM models for interferences."]
                }

            output_path = project_path / "stage_9" / "clash_detection_report.json"
            with open(output_path, "w") as f:
                json.dump(gemini_parsed, f, indent=4)

            logger.info(f"{self.name}: Generated clash detection report for {project_path.name}.")

            return {
                "agent_name": self.name,
                "status": "success",
                "details": "Generated simulated clash detection report.",
                "artifacts": [{"type": "clash_detection_report", "path": str(output_path)}]
            }

        except Exception as e:
            logger.error(f"{self.name}: Error during clash detection simulation: {e}", exc_info=True)
            return {"agent_name": self.name, "status": "error", "message": str(e)}