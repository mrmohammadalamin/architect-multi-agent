"""
Core Workflow Engine for the Multi-Agent Construction System.

This module defines the Directed Acyclic Graph (DAG) for the 18-stage workflow,
manages stage transitions, gate approvals, and orchestrates agent execution.
"""

import uuid
import json
import os
import asyncio
import logging
import base64
from pathlib import Path
from typing import Dict, Any, List

from adk_core import get_adk_system

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_STORE_PATH = Path(os.getenv("PROJECT_STORE_PATH", Path(__file__).parent / "project_store"))

WORKFLOW_STAGES = {
    1: {"name": "Client Intake", "agents": ["briefing_constraint_extraction_agent"], "gate_after": "G0"},
    2: {"name": "Data & Constraints Harvest", "agents": ["data_harvester_agent", "geospatial_site_context_agent"], "gate_after": None},
    3: {"name": "Feasibility & Risk Scan", "agents": ["risk_mitigation_agent"], "gate_after": None},
    4: {"name": "Optioneering & Strategic Scenarios", "agents": ["optioneering_strategy_agent"], "gate_after": "G1"},
    5: {"name": "Concept Massing & Facade", "agents": ["massing_facade_agent"], "gate_after": None},
    6: {"name": "Space Planning & Adjacency", "agents": ["space_planning_adjacency_agent", "interior_design_agent"], "gate_after": "G2"},
    7: {"name": "Structural & Material Strategy", "agents": ["structural_design_agent"], "gate_after": None},
    8: {"name": "MEP & Sustainability Strategy", "agents": ["mep_systems_agent", "sustainability_energy_agent"], "gate_after": "G3"},
    9: {"name": "Cost Plan & Schedule Baseline", "agents": ["cost_schedule_agent"], "gate_after": None},
    10: {"name": "Detailed Design & BIM Development", "agents": ["bim_cad_documentation_agent", "architectural_detailing_agent", "visualization_agent"], "gate_after": "G4"},
    11: {"name": "Clash Detection & Coordination", "agents": ["clash_coordination_agent"], "gate_after": None},
    12: {"name": "Code Compliance & Standards Check", "agents": ["code_standards_agent", "compliance_and_construction_agent"], "gate_after": "G5"},
    13: {"name": "Procurement & Supply Chain Strategy", "agents": ["procurement_supply_chain_agent"], "gate_after": None},
    14: {"name": "Site Logistics & Safety Plan", "agents": ["site_logistics_safety_agent"], "gate_after": None},
    15: {"name": "Construction Monitoring & CV", "agents": ["construction_monitoring_cv_agent"], "gate_after": None},
    16: {"name": "Change Control & Claims Management", "agents": ["change_control_claims_agent"], "gate_after": None},
    17: {"name": "Commissioning & Asset Management", "agents": ["commissioning_asset_agent"], "gate_after": "G6"},
    18: {"name": "Digital Twin Finalization & Handover", "agents": ["bim_cad_documentation_agent"], "gate_after": None},
}

DECISION_GATES = {
    "G0": {"name": "Project Charter Approval", "stage_before": 1},
    "G1": {"name": "Strategy/Options Approval", "stage_before": 4},
    "G2": {"name": "Concept Design Approval", "stage_before": 6},
    "G3": {"name": "Schematic/Prelim Engineering Approval", "stage_before": 8},
    "G4": {"name": "Design Development/BIM Approval", "stage_before": 10},
    "G5": {"name": "Construction Docs/Permits Approval", "stage_before": 12},
    "G6": {"name": "Handover/Digital Twin Approval", "stage_before": 18},
}

class WorkflowManager:
    def __init__(self, project_id: str = None, initial_data: Dict[str, Any] = None):
        if project_id:
            self.project_id = project_id
        else:
            self.project_id = str(uuid.uuid4())
        
        self.project_path = PROJECT_STORE_PATH / self.project_id
        self.initial_data = initial_data or {}
        self._initialize_project()

    def _initialize_project(self):
        self.project_path.mkdir(parents=True, exist_ok=True)
        if self.initial_data:
            with open(self.project_path / "initial_project_data.json", "w") as f:
                json.dump(self.initial_data, f, indent=4)
        for stage_id in WORKFLOW_STAGES:
            (self.project_path / f"stage_{stage_id}").mkdir(exist_ok=True)

    def get_project_status(self) -> Dict[str, Any]:
        pending_gate = self._get_pending_gate()
        stages_status = []
        
        unlocked_until_stage = 18
        if pending_gate:
            gate_info = DECISION_GATES[pending_gate]
            unlocked_until_stage = gate_info['stage_before']

        for stage_id, stage_info in WORKFLOW_STAGES.items():
            stage_path = self.project_path / f"stage_{stage_id}"
            artifacts = []
            for f in stage_path.iterdir():
                if f.is_file():
                    content = None
                    try:
                        if f.suffix == '.json':
                            with open(f, 'r') as file:
                                content = json.load(file)
                            
                            # Check for specific artifact types within JSON
                            if "refined_render_base64" in content:
                                artifacts.append({"name": f.name, "type": "image_base64", "content": content["refined_render_base64"]})
                            elif "conceptual_render_base64" in content:
                                artifacts.append({"name": f.name, "type": "image_base64", "content": content["conceptual_render_base64"]})
                            if "plan_2d_path" in content and content["plan_2d_path"] and os.path.exists(content["plan_2d_path"]):
                                with open(content["plan_2d_path"], "rb") as f:
                                    artifacts.append({"name": os.path.basename(content["plan_2d_path"]), "type": "2d_plan", "content": base64.b64encode(f.read()).decode('utf-8')})
                            if "model_3d_path" in content and content["model_3d_path"] and os.path.exists(content["model_3d_path"]):
                                with open(content["model_3d_path"], "rb") as f:
                                    artifacts.append({"name": os.path.basename(content["model_3d_path"]), "type": "3d_plan", "content": base64.b64encode(f.read()).decode('utf-8')})
                            if "video_path" in content and content["video_path"] and os.path.exists(content["video_path"]):
                                with open(content["video_path"], "rb") as f:
                                    artifacts.append({"name": os.path.basename(content["video_path"]), "type": "video", "content": base64.b64encode(f.read()).decode('utf-8')})
                            else:
                                artifacts.append({"name": f.name, "type": "json", "content": content})
                        elif f.suffix in ['.txt', '.md']:
                            with open(f, 'r') as file:
                                content = file.read()
                            artifacts.append({"name": f.name, "type": "text", "content": content})
                        # Add other file types here if needed
                    except Exception as e:
                        artifacts.append({"name": f.name, "type": "error", "content": f"Error reading file: {e}"})
            
            status = "Locked"
            if artifacts:
                status = "Completed"
            elif stage_id <= unlocked_until_stage:
                status = "Pending"
            
            if stage_id == 1 and not artifacts:
                status = "Pending"

            stages_status.append({
                "stage_id": stage_id,
                "name": stage_info["name"],
                "status": status,
                "artifacts": artifacts
            })

        return {
            "project_id": self.project_id,
            "stages": stages_status,
            "pending_gate": pending_gate
        }

    def _get_pending_gate(self) -> str | None:
        for gate_id in DECISION_GATES:
            if not (self.project_path / f"gate_{gate_id}_approval.json").exists():
                return gate_id
        return None

    async def approve_gate(self, gate_id: str, approval_data: dict):
        logger.info(f"Approving gate {gate_id} for project {self.project_id}")
        if gate_id not in DECISION_GATES:
            raise ValueError(f"Gate {gate_id} not found.")

        approval_file = self.project_path / f"gate_{gate_id}_approval.json"
        with open(approval_file, "w") as f:
            json.dump(approval_data, f, indent=4)
        
        logger.info(f"Gate {gate_id} approved. Triggering next stage...")
        
        stage_before = DECISION_GATES[gate_id]['stage_before']
        next_stage_id = stage_before + 1

        if next_stage_id in WORKFLOW_STAGES:
            await self.run_stage(next_stage_id)
            return {"status": "approved", "gate": gate_id, "message": f"Gate {gate_id} approved. Workflow continues."}
        else:
            logger.info("Final gate approved. Workflow complete.")
            return {"status": "approved", "gate": gate_id, "message": "Final gate approved. Workflow complete."}

    def _gather_inputs_for_stage(self, stage_id: int) -> Dict[str, Any]:
        # Placeholder logic for gathering inputs.
        # A real implementation would intelligently read required artifacts from previous stages.
        logger.info(f"Gathering inputs for stage {stage_id}...")
        gathered_inputs = {"initial_data": self.initial_data, "stage_id": stage_id}
        for i in range(1, stage_id):
            stage_path = self.project_path / f"stage_{i}"
            for artifact_file in stage_path.iterdir():
                if artifact_file.suffix == '.json':
                    with open(artifact_file, 'r') as f:
                        try:
                            gathered_inputs[artifact_file.stem] = json.load(f)
                        except json.JSONDecodeError:
                            logger.warning(f"Could not parse JSON from {artifact_file.name}")
                            gathered_inputs[artifact_file.stem] = {}
        return gathered_inputs

    async def run_stage(self, stage_id: int):
        logger.info(f"Running stage {stage_id} for project {self.project_id}")
        if stage_id not in WORKFLOW_STAGES:
            raise ValueError(f"Stage {stage_id} not found.")

        stage_info = WORKFLOW_STAGES[stage_id]
        agents_to_run = stage_info["agents"]
        adk_system = get_adk_system()

        logger.info(f"Running Stage {stage_id}: {stage_info['name']} for project {self.project_id}")
        logger.info(f"  > Activating agents: {agents_to_run}")

        current_input = self._gather_inputs_for_stage(stage_id)

        tasks = []
        ordered_agents = []

        # Define a simple dependency order for Stage 2
        if stage_id == 2:
            ordered_agents.append("data_harvester_agent")
            ordered_agents.append("geospatial_site_context_agent")
        else:
            ordered_agents = agents_to_run # For other stages, run as defined

        stage_results = []
        for agent_name in ordered_agents:
            agent = adk_system.get(agent_name)
            if agent:
                # Pass current_input and previous stage_results as user_input
                agent_input = current_input.copy()
                agent_input["stage_results"] = stage_results # Pass results from agents already run in this stage
                result = await agent.process_request(user_input=agent_input, project_path=self.project_path)
                stage_results.append(result)
            else:
                logger.warning(f"Warning: Agent '{agent_name}' not found in ADK system.")

        results = stage_results

        logger.info(f"Stage {stage_id} completed for project {self.project_id}. Results: {results}")

        # Auto-approve gate if one exists after this stage
        if stage_info["gate_after"]:
            gate_id = stage_info["gate_after"]
            logger.info(f"Auto-approving gate {gate_id} for project {self.project_id}")
            await self.approve_gate(gate_id, {"approved_by": "system", "comments": "Auto-approved for continuous workflow", "approved": True})
        else:
            # If there's no gate, automatically trigger the next stage
            next_stage_id = stage_id + 1
            if next_stage_id in WORKFLOW_STAGES:
                logger.info(f"No gate after Stage {stage_id}. Automatically triggering Stage {next_stage_id}...")
                await self.run_stage(next_stage_id)

        return {"status": "completed", "stage": stage_id, "results": results}
