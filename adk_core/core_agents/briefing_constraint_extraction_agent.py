import json
import logging
from typing import Dict, Any
from pathlib import Path

from ..base_agent import BaseConstructionAgent
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class BriefingConstraintExtractionAgent(BaseConstructionAgent):
    """
    Core Agent: Briefing & Constraint-Extraction Agent
    Processes raw client inquiries, refines requirements, and extracts constraints.
    Saves the output as project_charter.json and constraints.json.
    """
    def __init__(self):
        super().__init__(
            name="Briefing & Constraint-Extraction Agent",
            description="Processes initial client data and extracts core requirements and constraints."
        )
        self.gemini_service = GeminiService()

    async def process_request(self, user_input: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """
        Processes the initial project inquiry, extracts key information, and saves it
        as structured artifacts in the project store.
        """
        logger.info(f"{self.name}: Processing new project inquiry for project at {project_path.name}")

        try:
            # Use Gemini to parse and refine requirements
            prompt = (
                f"Analyze the following client inquiry for a construction project. Extract key, "
                f"structured requirements for a project charter and a separate list of constraints. "
                f"The charter should include: 'client_name', 'project_type', 'location', and a brief 'project_summary'. "
                f"The constraints should include: 'budget_range', 'desired_features', and any other specified limitations. "
                f"Client Inquiry: {json.dumps(user_input, indent=2)}\n\n"
                f"Format the output STRICTLY as a JSON object with two top-level keys: 'project_charter' and 'constraints'."
            )
            
            gemini_response_str = await self.gemini_service.generate_text(prompt, temperature=0.2)
            if gemini_response_str is None:
                raise ValueError("Gemini returned no response.")

            # Remove markdown code block fences if present
            if gemini_response_str.startswith("```json\n") and gemini_response_str.endswith("\n```"):
                gemini_response_str = gemini_response_str[len("```json\n"):-len("\n```")]

            parsed_response = json.loads(gemini_response_str)
            project_charter = parsed_response.get("project_charter", {})
            constraints = parsed_response.get("constraints", {})

            if not project_charter or not constraints:
                raise ValueError("Parsed response from Gemini is missing required keys.")

            # Define output paths
            stage_path = project_path / "stage_1"
            stage_path.mkdir(exist_ok=True)
            charter_path = stage_path / "project_charter.json"
            constraints_path = stage_path / "constraints.json"

            logger.info(f"{self.name}: Attempting to write project_charter.json to {charter_path}")
            with open(charter_path, "w") as f:
                json.dump(project_charter, f, indent=4)
            logger.info(f"{self.name}: Successfully wrote project_charter.json.")

            logger.info(f"{self.name}: Attempting to write constraints.json to {constraints_path}")
            with open(constraints_path, "w") as f:
                json.dump(constraints, f, indent=4)
            logger.info(f"{self.name}: Successfully wrote constraints.json.")

            return {
                "agent_name": self.name,
                "status": "success",
                "details": "Client inquiry processed and artifacts saved.",
                "artifacts": [
                    {"type": "project_charter", "path": str(charter_path)},
                    {"type": "constraints", "path": str(constraints_path)}
                ]
            }

        except Exception as e:
            logger.info(f"{self.name}: Error processing request: {e}", exc_info=True)
            return {
                "agent_name": self.name,
                "status": "error",
                "message": str(e)
            }
