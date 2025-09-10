import logging
import json
from typing import Dict, Any

from ..base_agent import BaseConstructionAgent
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class GovernanceQaExplainabilityAgent(BaseConstructionAgent):
    """
    Monitors and assures the quality of construction work, identifying deviations
    from design specifications and industry standards.
    """
    def __init__(self):
        super().__init__(
            name="Governance, QA & Explainability Agent",
            description="Monitors and assures the quality of construction work."
        )
        self.gemini_service = GeminiService()

    async def process_request(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provides a preliminary quality assurance plan and identifies key quality checkpoints.
        """
        project_id = user_input.get("project_id")
        architectural_concept = user_input.get("architectural_concept", {})
        system_design = user_input.get("system_design", {})
        experiential_design = user_input.get("experiential_design", {})
        project_type = user_input.get("project_type", "residential")

        logger.info(f"Quality Assurance Agent: Generating QA plan for project {project_id}.")

        try:
            prompt = (
                f"As an AI-driven quality assurance expert for construction, create a preliminary QA plan "
                f"for a '{project_type}' project with architectural style '{architectural_concept.get('design_style_summary')}' "
                f"and key design elements '{', '.join(architectural_concept.get('key_design_elements', []))}'. "
                f"Consider structural notes '{system_design.get('structural_notes')}' and MEP notes '{system_design.get('mep_notes')}', "
                f"and desired interior materials '{experiential_design.get('material_palette_notes')}'. "
                f"Identify key quality checkpoints during construction (e.g., foundation, framing, finishes) "
                f"and suggest potential quality challenges. "
                f"Output STRICTLY as a JSON object with keys 'qa_plan_summary' (string), 'quality_checkpoints' (list of strings), "
                f"'potential_qa_challenges' (list of strings)."
            )
            llm_response = await self.gemini_service.generate_text(prompt, temperature=0.4)

            if llm_response is None:
                return {
                    "agent_name": self.name,
                    "status": "error",
                    "message": "LLM did not generate a valid response for quality assurance."
                }

            try:
                parsed_response = json.loads(llm_response)
                if not isinstance(parsed_response, dict) or \
                   'qa_plan_summary' not in parsed_response or \
                   'quality_checkpoints' not in parsed_response or \
                   'potential_qa_challenges' not in parsed_response:
                    raise ValueError("LLM response JSON is not in the expected quality assurance format.")
            except json.JSONDecodeError:
                logger.error(f"Quality Assurance Agent: Gemini response was not valid JSON: {llm_response}. Using fallback data.")
                parsed_response = {
                    "qa_plan_summary": "Generic QA plan due to parsing error.",
                    "quality_checkpoints": ["Foundation", "Framing", "Finishes"],
                    "potential_qa_challenges": ["Material defects", "Workmanship errors"]
                }

            simulated_qa_plan = {
                "project_id": project_id,
                "status": "qa_plan_drafted",
                "qa_plan_summary": parsed_response.get("qa_plan_summary"),
                "quality_checkpoints": parsed_response.get("quality_checkpoints"),
                "potential_qa_challenges": parsed_response.get("potential_qa_challenges")
            }
            logger.info(f"Quality Assurance Agent: Completed QA plan for {project_id}.")

            return {
                "agent_name": self.name,
                "status": "success",
                "quality_assurance_plan": simulated_qa_plan
            }

        except Exception as e:
            logger.error(f"Quality Assurance Agent: Error during QA plan generation: {e}", exc_info=True)
            return {
                "agent_name": self.name,
                "status": "error",
                "message": f"Failed QA plan generation for {project_id}: {str(e)}"
            }