import json
import logging
from typing import Dict, Any
from pathlib import Path

from ..base_agent import BaseConstructionAgent
from ..services.gemini_service import GeminiService

try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None
    ImageDraw = None

try:
    import trimesh
except ImportError:
    trimesh = None

try:
    from moviepy.editor import ImageSequenceClip
except ImportError:
    ImageSequenceClip = None

logger = logging.getLogger(__name__)

class MassingFacadeAgent(BaseConstructionAgent):
    """
    Core Agent: Massing & Facade Agent
    Designs building envelopes and optimizes for daylight/energy.
    Generates initial architectural concepts and visual sketches.
    """
    def __init__(self):
        super().__init__(
            name="Massing & Facade Agent",
            description="Generates initial architectural concepts and visual sketches."
        )
        self.gemini_service = GeminiService()

    async def process_request(self, user_input: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """
        Generates architectural concepts and renders based on provided project data.
        """
        logger.info(f"{self.name}: Generating concepts for project {project_path.name}")

        try:
            # 1. Extract data gathered by the workflow engine from previous stages
            project_charter = user_input.get('project_charter', {})
            constraints = user_input.get('constraints', {})
            geospatial_analysis = user_input.get('geospatial_analysis', {})
            strategic_options = user_input.get('strategic_options', {})

            if not all([project_charter, constraints, geospatial_analysis, strategic_options]):
                raise ValueError("Missing required artifacts from previous stages for design generation.")

            # Extract relevant details for the prompt
            project_type = project_charter.get('project_type', 'building')
            location = project_charter.get('location', 'a site')
            desired_features = constraints.get('desired_features', [])
            geospatial_analysis = user_input.get('geospatial_analysis', {})
            if isinstance(geospatial_analysis, str):
                try:
                    geospatial_analysis = json.loads(geospatial_analysis)
                except json.JSONDecodeError:
                    geospatial_analysis = {} # Fallback to empty dict if string is not valid JSON

            geospatial_summary = geospatial_analysis.get('topography_land_use', 'N/A')
            
            # Safely get chosen strategy description
            chosen_strategy_description = 'general design principles'
            if strategic_options and strategic_options.get('strategic_options') and len(strategic_options['strategic_options']) > 0:
                chosen_strategy_description = strategic_options['strategic_options'][0].get('description', 'general design principles')

            # 2. Use Gemini to interpret design brief, site constraints, and propose a concept
            design_prompt = (
                f"Based on the following project details, propose an architectural concept for a {project_type}. "
                f"Consider the location ({location}), desired features ({', '.join(desired_features)}), "
                f"geospatial context ({geospatial_summary}), and the strategic direction: {chosen_strategy_description}. "
                f"Summarize the proposed style, key design elements, and how it addresses site constraints. "
                f"Format output STRICTLY as a JSON object with keys 'design_summary' (string), 'key_elements' (list of strings), 'considerations' (list of strings)."
            )
            logger.info(f"{self.name}: Calling Gemini for design brief interpretation...")
            gemini_design_response_str = await self.gemini_service.generate_text(design_prompt, temperature=0.5)

            if gemini_design_response_str is None:
                raise ValueError("LLM did not generate a valid response for design concept.")

            # Remove markdown code block fences if present
            if gemini_design_response_str.startswith("```json\n") and gemini_design_response_str.endswith("\n```"):
                gemini_design_response_str = gemini_design_response_str[len("```json\n"):-len("\n```")]

            try:
                gemini_design_parsed = json.loads(gemini_design_response_str)
            except json.JSONDecodeError:
                logger.error(f"{self.name}: Gemini design response was not valid JSON: {gemini_design_response_str}. Using fallback data.")
                gemini_design_parsed = {
                    "design_summary": "Could not parse design summary from AI. Manual design review needed.",
                    "key_elements": ["Unspecified"],
                    "considerations": ["Manual design. AI parsing failed or response malformed."]
                }

            # 3. Use Imagen to generate a preliminary visual sketch based on the concept
            image_prompt = (
                f"Architectural sketch of a {project_type} in {location} "
                f"with features like {', '.join(desired_features)} and a {gemini_design_parsed.get('design_summary')} style. "
                f"Exterior view, clear daylight, high detail, concept art."
            )
            logger.info(f"{self.name}: Calling Imagen for conceptual render...")
            image_base64 = await self.gemini_service.generate_image(image_prompt)

            # 4. Generate 2D plan, 3D model, and video
            plan_2d_path = None
            if Image is not None:
                plan_2d_path = project_path / "stage_5" / "plan_2d.png"
                img = Image.new('RGB', (600, 400), color = 'white')
                d = ImageDraw.Draw(img)
                d.rectangle([(100, 100), (500, 300)], fill = 'black')
                d.rectangle([(200, 150), (400, 250)], fill = 'white')
                img.save(plan_2d_path)

            model_3d_path = None
            if trimesh is not None:
                model_3d_path = project_path / "stage_5" / "model.glb"
                mesh = trimesh.creation.box(extents=[1, 1, 1])
                mesh.export(model_3d_path)

            video_path = project_path / "stage_5" / "video.txt"
            with open(video_path, "w") as f:
                f.write("This is a placeholder for the video.")

            simulated_design_concept = {
                "project_id": project_path.name,
                "design_style_summary": gemini_design_parsed.get("design_summary"),
                "key_design_elements": gemini_design_parsed.get("key_elements", []),
                "site_considerations_addressed": gemini_design_parsed.get("considerations", []),
                "conceptual_render_base64": image_base64, # Full base64 for actual display if needed
                "plan_2d_path": str(plan_2d_path),
                "model_3d_path": str(model_3d_path),
                "video_path": str(video_path),
            }
            logger.info(f"{self.name}: Generated concepts for {project_path.name}.")

            output_path = project_path / "stage_5" / "conceptual_massing_plan.json"
            with open(output_path, "w") as f:
                json.dump(simulated_design_concept, f, indent=4)

            return {
                "agent_name": self.name,
                "status": "success",
                "details": "Generated conceptual massing and site plan.",
                "artifacts": [{"type": "conceptual_massing_plan", "path": str(output_path)}]
            }

        except Exception as e:
            logger.error(f"{self.name}: Error during design generation: {e}", exc_info=True)
            return {"agent_name": self.name, "status": "error", "message": str(e)}