import json
import logging
from typing import Dict, Any
from pathlib import Path

from ..base_agent import BaseConstructionAgent
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class ProcurementSupplyChainAgent(BaseConstructionAgent):
    """
    Specialist Agent: Procurement & Supply Chain
    Handles procurement, bids, and lead times.
    """
    def __init__(self):
        super().__init__(
            name="Procurement & Supply Chain Agent",
            description="Generates preliminary procurement plans and analyzes supply chain."
        )
        self.gemini_service = GeminiService()

    async def process_request(self, user_input: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """
        Generates preliminary procurement plans based on project data.
        """
        logger.info(f"{self.name}: Generating preliminary procurement plan for {project_path.name}")

        try:
            # 1. Extract data gathered by the workflow engine from previous stages
            project_charter = user_input.get('project_charter', {})
            constraints = user_input.get('constraints', {})
            cost_schedule_baseline = user_input.get('cost_schedule_baseline', {})
            legal_contract_review = user_input.get('legal_contract_review', {})

            if not all([project_charter, constraints, cost_schedule_baseline]):
                raise ValueError("Missing required artifacts from previous stages for procurement plan.")

            # Extract relevant details for the prompt
            project_type = project_charter.get('project_type', 'building')
            total_cost = cost_schedule_baseline.get('total_estimated_cost_usd', 'N/A')
            key_phases = cost_schedule_baseline.get('key_phases', [])
            key_contract_clauses = legal_contract_review.get('key_contract_clauses', []) if legal_contract_review else []

            # 2. Construct a detailed prompt for Gemini
            prompt = (
                f"As a procurement and supply chain specialist for a {project_type} project with an estimated cost of {total_cost}, "
                f"and key phases {', '.join(key_phases)}, propose a preliminary procurement plan. "
                f"Consider key contract clauses: {', '.join(key_contract_clauses)}. "
                f"Outline strategies for material sourcing, vendor selection, and lead time management. "
                f"Format the output STRICTLY as a JSON object with keys 'procurement_strategy_summary', 'material_sourcing_approach', 'vendor_selection_criteria', 'lead_time_management_notes'."
            )
            logger.info(f"{self.name}: Calling Gemini for procurement plan generation...")
            gemini_response_str = await self.gemini_service.generate_text(prompt, temperature=0.6)

            if gemini_response_str is None:
                raise ValueError("LLM did not generate a valid response for procurement plan.")

            try:
                gemini_parsed = json.loads(gemini_response_str)
            except json.JSONDecodeError:
                logger.error(f"{self.name}: Gemini response was not valid JSON: {gemini_response_str}. Using fallback data.")
                gemini_parsed = {
                    "procurement_strategy_summary": "Generic procurement plan due to parsing error.",
                    "material_sourcing_approach": "Local suppliers, competitive bidding.",
                    "vendor_selection_criteria": "Cost, quality, reliability.",
                    "lead_time_management_notes": "Monitor critical path items."
                }

            output_path = project_path / "stage_11" / "preliminary_procurement_plan.json"
            with open(output_path, "w") as f:
                json.dump(gemini_parsed, f, indent=4)

            logger.info(f"{self.name}: Generated preliminary procurement plan for {project_path.name}.")

            return {
                "agent_name": self.name,
                "status": "success",
                "details": "Generated preliminary procurement plan.",
                "artifacts": [{"type": "preliminary_procurement_plan", "path": str(output_path)}]
            }

        except Exception as e:
            logger.error(f"{self.name}: Error during procurement plan generation: {e}", exc_info=True)
            return {"agent_name": self.name, "status": "error", "message": str(e)}