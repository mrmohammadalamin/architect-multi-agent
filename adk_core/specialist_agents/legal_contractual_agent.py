import json
import logging
from typing import Dict, Any
from pathlib import Path

from ..base_agent import BaseConstructionAgent
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class LegalContractualAgent(BaseConstructionAgent):
    """
    Specialist Agent: Legal & Contractual Agent
    Analyzes contracts and ensures legal compliance.
    """
    def __init__(self):
        super().__init__(
            name="Legal & Contractual Agent",
            description="Analyzes contracts and ensures legal compliance."
        )
        self.gemini_service = GeminiService()

    async def process_request(self, user_input: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """
        Provides high-level legal and contract considerations for the project.
        """
        logger.info(f"{self.name}: Assessing legal and contract aspects for project {project_path.name}")

        try:
            # 1. Extract data gathered by the workflow engine from previous stages
            project_charter = user_input.get('project_charter', {})
            constraints = user_input.get('constraints', {})
            bim_cad_documentation_plan = user_input.get('bim_cad_documentation_plan', {})
            compliance_check_report = user_input.get('compliance_check_report', {})

            if not all([project_charter, constraints, bim_cad_documentation_plan, compliance_check_report]):
                raise ValueError("Missing required artifacts from previous stages for legal review.")

            # Extract relevant details for the prompt
            project_type = project_charter.get('project_type', 'building')
            location = project_charter.get('location', 'unspecified')
            documentation_types = bim_cad_documentation_plan.get('documentation_plan', {}).get('documentation_types', [])
            compliance_summary = compliance_check_report.get('compliance_summary', 'N/A')

            # 2. Construct a detailed prompt for Gemini
            prompt = (
                f"As a construction legal and contract management expert, outline key legal considerations "
                f"and common contract types for a '{project_type}' project in '{location}'. "
                f"Consider the documentation types available: {documentation_types.join(', ')}. "
                f"Also, consider the compliance summary: '{compliance_summary}'. "
                f"Suggest important contract clauses and necessary permits/licenses. "
                f"Format output STRICTLY as a JSON object with keys 'legal_overview' (string summary), "
                f"'common_contract_types' (list of strings), 'key_contract_clauses' (list of strings), "
                f"'required_permits_licenses' (list of strings)."
            )
            logger.info(f"{self.name}: Calling Gemini for legal/contract review...")
            gemini_response_str = await self.gemini_service.generate_text(prompt, temperature=0.5)

            if gemini_response_str is None:
                raise ValueError("LLM did not generate a valid response for legal/contract management.")

            try:
                gemini_parsed = json.loads(gemini_response_str)
            except json.JSONDecodeError:
                logger.error(f"{self.name}: Gemini response was not valid JSON: {gemini_response_str}. Using fallback data.")
                gemini_parsed = {
                    "legal_overview": "Legal assessment failed due to parsing error.",
                    "common_contract_types": ["Fixed Price", "Cost-Plus"],
                    "key_contract_clauses": ["Scope of Work", "Payment Terms"],
                    "required_permits_licenses": ["Building Permit", "Zoning Approval"]
                }

            output_path = project_path / "stage_10" / "legal_contract_review.json"
            with open(output_path, "w") as f:
                json.dump(gemini_parsed, f, indent=4)

            logger.info(f"{self.name}: Completed legal and contract assessment for {project_path.name}.")

            return {
                "agent_name": self.name,
                "status": "success",
                "details": "Generated legal and contract review.",
                "artifacts": [{"type": "legal_contract_review", "path": str(output_path)}]
            }

        except Exception as e:
            logger.error(f"{self.name}: Error during legal/contract assessment: {e}", exc_info=True)
            return {"agent_name": self.name, "status": "error", "message": str(e)}