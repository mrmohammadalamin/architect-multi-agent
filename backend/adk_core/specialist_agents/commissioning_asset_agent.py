import json
import logging
from typing import Dict, Any
from pathlib import Path

from ..base_agent import BaseConstructionAgent
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class CommissioningAssetAgent(BaseConstructionAgent):
    """
    Specialist Agent: Commissioning & Asset Agent
    Integrates as-built data, digital twin, and O&M.
    """
    def __init__(self):
        super().__init__(
            name="Commissioning & Asset Agent",
            description="Generates preliminary commissioning and asset tagging plans."
        )
        self.gemini_service = GeminiService()

    async def process_request(self, user_input: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """
        Generates preliminary commissioning and asset tagging plans based on project data.
        """
        logger.info(f"{self.name}: Generating preliminary commissioning and asset tagging plan for {project_path.name}")

        try:
            # 1. Extract data gathered by the workflow engine from previous stages
            project_charter = user_input.get('project_charter', {})
            bim_cad_documentation_plan = user_input.get('bim_cad_documentation_detailed_plan', {})
            sustainability_energy_analysis = user_input.get('sustainability_energy_analysis', {})

            if not all([project_charter, bim_cad_documentation_plan]):
                logger.warning(f"{self.name}: Missing required artifacts from previous stages for commissioning/asset plan.")
                gemini_parsed = {
                    "commissioning_summary": "Generic commissioning plan due to missing inputs.",
                    "system_testing_approach": "Standard functional tests.",
                    "handover_documentation": "O&M manuals, as-builts.",
                    "asset_tagging_strategy": "QR codes, digital database.",
                    "digital_twin_integration": "Basic data sync."
                }
            else:
                # Extract relevant details for the prompt
                project_type = project_charter.get('project_type', 'building')
                bim_key_deliverables = bim_cad_documentation_plan.get('documentation_plan', {}).get('key_deliverables', [])
                energy_efficiency_opportunities = ", ".join([o.get('title', '') for o in sustainability_energy_analysis.get('energy_efficiency_opportunities', [])]) if sustainability_energy_analysis else 'N/A'

                # 2. Construct a detailed prompt for Gemini
                prompt = (
                    f"As a commissioning and asset management specialist, propose a preliminary plan for a {project_type} project. "
                    f"Consider the BIM key deliverables ({', '.join(bim_key_deliverables)}) and energy efficiency opportunities ({', '.join(energy_efficiency_opportunities)}). "
                    f"Outline strategies for system testing, handover documentation, asset tagging, and integration with a digital twin for operations and maintenance. "
                    f"Format the output STRICTLY as a JSON object with keys 'commissioning_summary', 'system_testing_approach', 'handover_documentation', 'asset_tagging_strategy', 'digital_twin_integration'."
                )
                logger.info(f"{self.name}: Calling Gemini for commissioning and asset tagging plan generation...")
                gemini_response_str = await self.gemini_service.generate_text(prompt, temperature=0.6)

                if gemini_response_str is None:
                    raise ValueError("LLM did not generate a valid response for commissioning/asset plan.")

                try:
                    gemini_parsed = json.loads(gemini_response_str)
                except json.JSONDecodeError:
                    logger.error(f"{self.name}: Gemini response was not valid JSON: {gemini_response_str}. Using fallback data.")
                    gemini_parsed = {
                        "commissioning_summary": "Generic commissioning plan due to parsing error.",
                        "system_testing_approach": "Standard functional tests.",
                        "handover_documentation": "O&M manuals, as-builts.",
                        "asset_tagging_strategy": "QR codes, digital database.",
                        "digital_twin_integration": "Basic data sync."
                    }

            output_path = project_path / "stage_17" / "commissioning_asset_plan.json"
            with open(output_path, "w") as f:
                json.dump(gemini_parsed, f, indent=4)

            logger.info(f"{self.name}: Generated preliminary commissioning and asset tagging plan for {project_path.name}.")

            return {
                "agent_name": self.name,
                "status": "success",
                "details": "Generated preliminary commissioning and asset tagging plan.",
                "artifacts": [{"type": "commissioning_asset_plan", "path": str(output_path)}]
            }

        except Exception as e:
            logger.error(f"{self.name}: Error during commissioning and asset tagging plan generation: {e}", exc_info=True)
            return {"agent_name": self.name, "status": "error", "message": str(e)}
