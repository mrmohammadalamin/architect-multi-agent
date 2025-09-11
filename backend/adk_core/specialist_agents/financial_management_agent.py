import logging
import json
from typing import Dict, Any

from ..base_agent import BaseConstructionAgent
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class FinancialManagementAgent(BaseConstructionAgent):
    """
    Performs financial modeling, investment analysis, and cost-benefit assessments
    to ensure project financial viability and optimal return on investment.
    """
    def __init__(self):
        super().__init__(
            name="Financial Management Agent",
            description="Performs financial modeling and investment analysis for projects."
        )
        self.gemini_service = GeminiService()

    async def process_request(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs a high-level financial viability analysis.
        """
        project_id = user_input.get("project_id")
        budget_info = user_input.get("cost_supply_chain_analysis", {}).get("estimated_budget_usd", {})
        project_description = user_input.get("project_description", "a construction project")
        project_type = user_input.get("project_type", "residential")

        logger.info(f"Financial Agent: Starting financial analysis for project {project_id}.")

        try:
            min_budget = budget_info.get("min_budget", 0)
            max_budget = budget_info.get("max_budget", 0)

            prompt = (
                f"As a construction financial analyst, assess the financial viability "
                f"of a '{project_type}' project described as '{project_description}' "
                f"with an estimated budget range of ${min_budget:,} - ${max_budget:,}. "
                f"Provide a high-level overview of potential revenue streams (if applicable, e.g., sales, rent), "
                f"major cost factors, and key financial risks. "
                f"Suggest basic investment considerations (e.g., ROI potential, funding options). "
                f"Output STRICTLY as a JSON object with keys 'financial_overview' (string summary), "
                f"'revenue_streams' (list of strings), 'cost_factors' (list of strings), "
                f"'financial_risks' (list of strings), 'investment_considerations' (list of strings)."
            )
            llm_response = await self.gemini_service.generate_text(prompt, temperature=0.5)

            if llm_response is None:
                return {
                    "agent_name": self.name,
                    "status": "error",
                    "message": "LLM did not generate a valid response for financial analysis."
                }

            try:
                parsed_response = json.loads(llm_response)
                if not isinstance(parsed_response, dict) or \
                   'financial_overview' not in parsed_response or \
                   'revenue_streams' not in parsed_response or \
                   'cost_factors' not in parsed_response or \
                   'financial_risks' not in parsed_response or \
                   'investment_considerations' not in parsed_response:
                    raise ValueError("LLM response JSON is not in the expected financial analysis format.")
            except json.JSONDecodeError:
                logger.error(f"Financial Agent: Gemini response was not valid JSON: {llm_response}. Using fallback data.")
                parsed_response = {
                    "financial_overview": "Financial analysis failed due to parsing error.",
                    "revenue_streams": ["Sale of property"],
                    "cost_factors": ["Construction costs", "Financing costs"],
                    "financial_risks": ["Market fluctuations"],
                    "investment_considerations": ["Requires significant upfront capital"]
                }

            simulated_financial_analysis = {
                "project_id": project_id,
                "status": "financial_analysis_complete",
                "financial_overview": parsed_response.get("financial_overview"),
                "revenue_streams": parsed_response.get("revenue_streams"),
                "cost_factors": parsed_response.get("cost_factors"),
                "financial_risks": parsed_response.get("financial_risks"),
                "investment_considerations": parsed_response.get("investment_considerations")
            }
            logger.info(f"Financial Agent: Completed financial analysis for {project_id}.")

            return {
                "agent_name": self.name,
                "status": "success",
                "financial_analysis": simulated_financial_analysis
            }

        except Exception as e:
            logger.error(f"Financial Agent: Error during financial analysis: {e}", exc_info=True)
            return {
                "agent_name": self.name,
                "status": "error",
                "message": f"Failed financial analysis for {project_id}: {str(e)}"
            }