import json
import logging
from typing import Dict, Any
from pathlib import Path

from ..base_agent import BaseConstructionAgent
from ..services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

class BimCadDocumentationAgent(BaseConstructionAgent):
    """
    Core Agent: BIM/CAD Documentation Agent
    Creates 2D/3D drawings and BIM models.
    """
    def __init__(self):
        super().__init__(
            name="BIM/CAD Documentation Agent",
            description="Generates BIM/CAD documentation plans and refined 3D renders."
        )
        self.gemini_service = GeminiService()

    async def process_request(self, user_input: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """
        Generates BIM/CAD documentation plans and refined 3D renders based on project data.
        Behaves differently based on the stage (Stage 9 vs. Stage 18).
        """
        stage_id = user_input.get('stage_id') # Get the current stage ID from user_input
        if not stage_id:
            raise ValueError("Stage ID not provided in user_input.")

        logger.info(f"{self.name}: Processing for Stage {stage_id} for {project_path.name}")

        try:
            if stage_id == 10:
                # Existing Stage 10 logic
                project_charter = user_input.get('project_charter', {})
                conceptual_massing_plan = user_input.get('conceptual_massing_plan', {})
                conceptual_floor_plan = user_input.get('conceptual_floor_plan', {})
                preliminary_structural_design = user_input.get('preliminary_structural_design', {})
                preliminary_mep_design = user_input.get('preliminary_mep_design', {})
                cost_schedule_baseline = user_input.get('cost_schedule_baseline', {})

                if not all([project_charter, conceptual_massing_plan, conceptual_floor_plan,
                            preliminary_structural_design, preliminary_mep_design, cost_schedule_baseline]):
                    raise ValueError("Missing required artifacts for Stage 10 BIM/CAD documentation.")

                project_type = project_charter.get('project_type', 'building')
                location = project_charter.get('location', 'a site')
                massing_summary = conceptual_massing_plan.get('design_style_summary', 'N/A')
                floor_plan_summary = conceptual_floor_plan.get('layout_summary', 'N/A')
                structural_notes = preliminary_structural_design.get('notes', 'N/A')
                mep_notes = preliminary_mep_design.get('notes', 'N/A')

                doc_prompt = (
                    f"As a BIM/CAD manager, outline the key documentation (2D drawings, 3D models, specifications) required for a {project_type} project. "
                    f"Consider the conceptual massing ({massing_summary}), floor plan ({floor_plan_summary}), structural notes ({structural_notes}), and MEP notes ({mep_notes}). "
                    f"Suggest appropriate LOD (Level of Detail) for the BIM models at this stage. "
                    f"Format output STRICTLY as a JSON object with keys 'documentation_types' (list of strings), 'suggested_lod' (string), 'key_deliverables' (list of strings)."
                )
                logger.info(f"{self.name}: Calling Gemini for Stage 10 documentation plan...")
                gemini_doc_response_str = await self.gemini_service.generate_text(doc_prompt, temperature=0.5)

                if gemini_doc_response_str is None:
                    raise ValueError("LLM did not generate a valid response for Stage 10 documentation plan.")

                try:
                    gemini_doc_parsed = json.loads(gemini_doc_response_str)
                except json.JSONDecodeError:
                    logger.error(f"{self.name}: Stage 10 Gemini doc response was not valid JSON: {gemini_doc_response_str}. Using fallback data.")
                    gemini_doc_parsed = {
                        "documentation_types": ["Architectural Plans", "Structural Plans", "MEP Plans"],
                        "suggested_lod": "LOD 200",
                        "key_deliverables": ["Preliminary BIM Model", "Concept Drawings"]
                    }

                render_prompt = (
                    f"High-detail 3D render of a {project_type} building at {location}. "
                    f"Style: {massing_summary}. Incorporate elements from the floor plan ({floor_plan_summary}). "
                    f"Show exterior view, realistic lighting, and context. Focus on architectural details and materials."
                )
                logger.info(f"{self.name}: Calling Imagen for Stage 10 refined 3D render...")
                refined_render_base64 = await self.gemini_service.generate_image(render_prompt)

                simulated_bim_cad_plan = {
                    "project_id": project_path.name,
                    "documentation_plan": gemini_doc_parsed,
                    "refined_render_base64": refined_render_base64,
                    "3d_plan_url": "https://modelviewer.dev/shared-assets/models/Astronaut.glb", # Simulated 3D plan URL
                    "status": "bim_cad_plan_generated",
                    "details": "BIM/CAD documentation plan, refined 3D render, and simulated 3D plan generated."
                }

                output_path = project_path / "stage_10" / "bim_cad_documentation_plan.json"
                with open(output_path, "w") as f:
                    json.dump(simulated_bim_cad_plan, f, indent=4)

                return {
                    "agent_name": self.name,
                    "status": "success",
                    "details": "Generated BIM/CAD documentation plan and refined 3D render.",
                    "artifacts": [{"type": "bim_cad_documentation_plan", "path": str(output_path)}]
                }

            elif stage_id == 18:
                # Stage 18 logic: Digital Twin Finalization & Handover
                project_charter = user_input.get('project_charter', {})
                bim_cad_documentation_plan = user_input.get('bim_cad_documentation_detailed_plan', {})
                commissioning_asset_plan = user_input.get('commissioning_asset_plan', {})

                if not all([project_charter, bim_cad_documentation_plan, commissioning_asset_plan]):
                    logger.warning(f"{self.name}: Missing required artifacts for Stage 18 Digital Twin Finalization.")
                    gemini_handover_parsed = {
                        "digital_twin_components": ["As-built BIM model", "Asset Register"],
                        "handover_documents": ["O&M Manuals", "Warranties"],
                        "final_summary": "Digital twin and handover documentation generated with fallback data."
                    }
                else:
                    project_type = project_charter.get('project_type', 'building')
                    location = project_charter.get('location', 'a site')
                    bim_key_deliverables = bim_cad_documentation_plan.get('documentation_plan', {}).get('key_deliverables', [])
                    commissioning_summary = commissioning_asset_plan.get('commissioning_summary', 'N/A') if commissioning_asset_plan else 'N/A'

                    # Prompt for final digital twin and handover documentation
                    handover_prompt = (
                        f"As a digital twin and handover specialist, describe the final digital twin deliverables and handover documentation for a completed {project_type} project. "
                        f"Consider the BIM key deliverables ({', '.join(bim_key_deliverables)}) and the commissioning summary ({commissioning_summary}). "
                        f"Outline the key components of the digital twin (e.g., as-built models, asset data, O&M manuals) and the essential handover documents. "
                        f"Format output STRICTLY as a JSON object with keys 'digital_twin_components' (list of strings), 'handover_documents' (list of strings), 'final_summary' (string)."
                    )
                    logger.info(f"{self.name}: Calling Gemini for Stage 18 handover plan...")
                    gemini_handover_response_str = await self.gemini_service.generate_text(handover_prompt, temperature=0.5)

                    if gemini_handover_response_str is None:
                        raise ValueError("LLM did not generate a valid response for Stage 18 handover plan.")

                    try:
                        gemini_handover_parsed = json.loads(gemini_handover_response_str)
                    except json.JSONDecodeError:
                        logger.error(f"{self.name}: Stage 18 Gemini handover response was not valid JSON: {gemini_handover_response_str}. Using fallback data.")
                        gemini_handover_parsed = {
                            "digital_twin_components": ["As-built BIM model", "Asset Register"],
                            "handover_documents": ["O&M Manuals", "Warranties"],
                            "final_summary": "Digital twin and handover documentation generated."
                        }

                # Generate a final high-fidelity render of the completed project
                final_render_prompt = (
                    f"Photorealistic 3D render of a completed {project_type} building at {location}. "
                    f"Show exterior view, realistic lighting, landscaping, and a sense of completion. High detail."
                )
                logger.info(f"{self.name}: Calling Imagen for Stage 18 final render...")
                final_render_base64 = await self.gemini_service.generate_image(final_render_prompt)

                final_digital_twin_handover = {
                    "project_id": project_path.name,
                    "handover_plan": gemini_handover_parsed,
                    "final_render_base64": final_render_base64,
                    "3d_plan_url": "https://modelviewer.dev/shared-assets/models/RobotExpressive.glb", # Simulated 3D plan URL
                    "status": "digital_twin_finalized",
                    "details": "Digital twin finalized and handover documentation prepared."
                }

                output_path = project_path / "stage_18" / "final_digital_twin_handover.json"
                with open(output_path, "w") as f:
                    json.dump(final_digital_twin_handover, f, indent=4)

                return {
                    "agent_name": self.name,
                    "status": "success",
                    "details": "Generated final digital twin and handover documentation.",
                    "artifacts": [{"type": "final_digital_twin_handover", "path": str(output_path)}]
                }

            else:
                raise ValueError(f"BimCadDocumentationAgent does not have logic for stage {stage_id}.")

        except Exception as e:
            logger.error(f"{self.name}: Error during BIM/CAD documentation/handover generation: {e}", exc_info=True)
            return {"agent_name": self.name, "status": "error", "message": str(e)}