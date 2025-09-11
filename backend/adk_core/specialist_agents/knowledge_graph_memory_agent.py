import json
import logging
from typing import Dict, Any
from pathlib import Path

from ..base_agent import BaseConstructionAgent
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class KnowledgeGraphMemoryAgent(BaseConstructionAgent):
    """
    Specialist Agent: Knowledge Graph/Memory Agent
    Captures lessons learned and builds project IP.
    """
    def __init__(self):
        super().__init__(
            name="Knowledge Graph/Memory Agent",
            description="Captures lessons learned and builds project IP."
        )
        self.gemini_service = GeminiService()

    async def process_request(self, user_input: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """
        Generates a lessons learned report and key project insights.
        """
        logger.info(f"{self.name}: Generating lessons learned report for {project_path.name}")

        try:
            # 1. Extract data gathered by the workflow engine from previous stages
            project_charter = user_input.get('project_charter', {})
            risk_assessment_report = user_input.get('risk_assessment_report', {})
            cost_schedule_baseline = user_input.get('cost_schedule_baseline', {})
            construction_progress_report = user_input.get('construction_progress_report', {})
            commissioning_asset_plan = user_input.get('commissioning_asset_plan', {})

            if not all([project_charter, risk_assessment_report, cost_schedule_baseline,
                        construction_progress_report, commissioning_asset_plan]):
                raise ValueError("Missing required artifacts from previous stages for lessons learned report.")

            # Extract relevant details for the prompt
            project_type = project_charter.get('project_type', 'building')
            project_summary = project_charter.get('project_summary', 'N/A')
            identified_risks = risk_assessment_report.get('risk_register', [])
            total_cost = cost_schedule_baseline.get('total_estimated_cost_usd', 'N/A')
            current_progress = construction_progress_report.get('current_status', 'N/A')
            commissioning_summary = commissioning_asset_plan.get('commissioning_summary', 'N/A')

            # 2. Construct a detailed prompt for Gemini
            prompt = (
                f"As a knowledge manager and project closeout specialist, generate a lessons learned report and key project insights for a {project_type} project. "
                f"Consider the following information:\n\n"
                f"Project Summary: {project_summary}\n"
                f"Identified Risks: {json.dumps(identified_risks, indent=2)}\n"
                f"Estimated Cost: {total_cost}\n"
                f"Construction Progress: {current_progress}\n"
                f"Commissioning Summary: {commissioning_summary}\n\n"
                f"Identify key successes, challenges encountered, and actionable lessons learned that can be applied to future projects. "
                f"Format the output STRICTLY as a JSON object with keys 'lessons_learned_summary', 'key_successes' (list of strings), 'challenges_encountered' (list of strings), 'actionable_lessons' (list of strings)."
            )
            logger.info(f"{self.name}: Calling Gemini for lessons learned report generation...")
            gemini_response_str = await self.gemini_service.generate_text(prompt, temperature=0.6)

            if gemini_response_str is None:
                raise ValueError("LLM did not generate a valid response for lessons learned report.")

            try:
                gemini_parsed = json.loads(gemini_response_str)
            except json.JSONDecodeError:
                logger.error(f"{self.name}: Gemini response was not valid JSON: {gemini_response_str}. Using fallback data.")
                gemini_parsed = {
                    "lessons_learned_summary": "Generic lessons learned report due to parsing error.",
                    "key_successes": ["Project completion."],
                    "challenges_encountered": ["Data parsing issues."],
                    "actionable_lessons": ["Improve data standardization."]
                }

            output_path = project_path / "stage_17" / "lessons_learned_report.json"
            with open(output_path, "w") as f:
                json.dump(gemini_parsed, f, indent=4)

            logger.info(f"{self.name}: Generated lessons learned report for {project_path.name}.")

            return {
                "agent_name": self.name,
                "status": "success",
                "details": "Generated lessons learned report.",
                "artifacts": [{"type": "lessons_learned_report", "path": str(output_path)}]
            }

        except Exception as e:
            logger.error(f"{self.name}: Error during lessons learned report generation: {e}", exc_info=True)
            return {"agent_name": self.name, "status": "error", "message": str(e)}