"""
Main FastAPI application for the Multi-Agent Construction System.

This file defines the primary API endpoints for interacting with the workflow-driven
construction intelligence platform.
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
from pathlib import Path
import json

# Import the new workflow manager and the dynamic agent initializer
from workflow_engine import WorkflowManager, PROJECT_STORE_PATH
from adk_core import initialize_adk_system_with_agents

# --- Pydantic Models for API Requests ---

class ProjectCreationRequest(BaseModel):
    project_name: str
    client_name: str
    project_description: str
    project_type: str
    budget_range: str
    location: str
    desired_features: list[str]

class GateApprovalRequest(BaseModel):
    approved_by: str
    comments: str
    approved: bool = True # True for approval, False for rejection

# --- FastAPI Application Setup ---

app = FastAPI(
    title="Construction AI Multi-Agent System (V2 - Workflow Edition)",
    description="An API for orchestrating a team of specialized AI agents through a staged construction project workflow.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.on_event("startup")
async def startup_event():
    """
    On application startup, initialize the ADK system with the new dynamic loader.
    """
    print("Application starting up...")
    initialize_adk_system_with_agents()
    print("Application startup complete.")

# --- API Endpoints ---

@app.get("/", tags=["Health Check"])
async def read_root():
    """
    Basic health check endpoint.
    """
    return {"message": "Construction AI Multi-Agent System V2 is running! Access /docs for API documentation."}

@app.post("/projects", tags=["Project Workflow"], status_code=201)
async def create_project(request: ProjectCreationRequest):
    """
    Creates a new project, initializes its workflow, and runs the first stage.
    """
    try:
        manager = WorkflowManager(initial_data=request.dict())
        stage_1_results = await manager.run_stage(1)
        
        return {
            "message": "Project created successfully and Stage 1 (Client Intake) has completed.",
            "project_id": manager.project_id,
            "stage_1_results": stage_1_results,
            "status_url": f"/projects/{manager.project_id}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{project_id}", tags=["Project Workflow"])
async def get_project_status(project_id: str):
    """
    Returns the current status of a project, including completed stages and pending approvals.
    """
    try:
        manager = WorkflowManager(project_id=project_id)
        status = manager.get_project_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found or error: {e}")

@app.get("/projects", tags=["Project Workflow"])
async def list_projects():
    """
    Returns a list of all available project IDs.
    """
    try:
        project_ids = [d.name for d in PROJECT_STORE_PATH.iterdir() if d.is_dir()]
        return {"projects": project_ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing projects: {e}")

@app.post("/projects/{project_id}/approve/{gate_id}", tags=["Project Workflow"])
async def approve_gate(project_id: str, gate_id: str, request: GateApprovalRequest):
    """
    Records a human approval/rejection for a specific decision gate.
    """
    try:
        manager = WorkflowManager(project_id=project_id)
        result = await manager.approve_gate(gate_id, request.dict())
        return result
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/projects/{project_id}/artifacts/{stage_id}/{artifact_name}", tags=["Project Artifacts"])
async def get_artifact_content(project_id: str, stage_id: int, artifact_name: str):
    """
    Fetches the content of a specific artifact file.
    """
    artifact_path = PROJECT_STORE_PATH / project_id / f"stage_{stage_id}" / artifact_name

    if not artifact_path.exists():
        raise HTTPException(status_code=404, detail="Artifact not found.")

    try:
        if artifact_path.suffix == '.json':
            with open(artifact_path, 'r') as f:
                content = json.load(f)
            if isinstance(content, dict) and "refined_render_base64" in content:
                return {"type": "image_base64", "content": content["refined_render_base64"]}
            elif isinstance(content, dict) and "conceptual_render_base64" in content:
                return {"type": "image_base64", "content": content["conceptual_render_base64"]}
            else:
                return {"type": "json", "content": content}
        else:
            return FileResponse(artifact_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading artifact: {e}")

@app.get("/projects/{project_id}/risks", tags=["Dashboards"])
async def get_risk_summary(project_id: str):
    """
    Returns a consolidated risk matrix from the Risk Mitigation Agent.
    """
    risk_report_path = PROJECT_STORE_PATH / project_id / "stage_3" / "risk_assessment_report.json"

    if not risk_report_path.exists():
        raise HTTPException(status_code=404, detail="Risk assessment report not found for this project.")

    try:
        with open(risk_report_path, 'r') as f:
            risk_data = json.load(f)
        
        risk_register = risk_data.get('risk_register', [])
        return {"project_id": project_id, "risk_register": risk_register}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading risk summary: {e}")

@app.get("/projects/{project_id}/financials", tags=["Dashboards"])
async def get_financial_summary(project_id: str):
    """
    Returns real-time CAPEX/OPEX & cash flow from the Financial Agent.
    """
    financial_report_path = PROJECT_STORE_PATH / project_id / "stage_8" / "cost_schedule_baseline.json"

    if not financial_report_path.exists():
        raise HTTPException(status_code=404, detail="Cost and schedule baseline not found for this project.")

    try:
        with open(financial_report_path, 'r') as f:
            financial_data = json.load(f)
        
        return {
            "project_id": project_id,
            "total_estimated_cost_usd": financial_data.get('total_estimated_cost_usd'),
            "cost_breakdown": financial_data.get('cost_breakdown'),
            "estimated_duration_weeks": financial_data.get('estimated_duration_weeks'),
            "key_phases": financial_data.get('key_phases'),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading financial summary: {e}")

@app.get("/projects/{project_id}/knowledge", tags=["Dashboards"])
async def query_knowledge_graph(project_id: str):
    """
    Queries the Knowledge Graph Agent for lessons learned.
    """
    knowledge_report_path = PROJECT_STORE_PATH / project_id / "stage_17" / "lessons_learned_report.json"

    if not knowledge_report_path.exists():
        raise HTTPException(status_code=404, detail="Lessons learned report not found for this project.")

    try:
        with open(knowledge_report_path, 'r') as f:
            knowledge_data = json.load(f)
        
        return {
            "project_id": project_id,
            "lessons_learned_summary": knowledge_data.get('lessons_learned_summary'),
            "key_successes": knowledge_data.get('key_successes'),
            "challenges_encountered": knowledge_data.get('challenges_encountered'),
            "actionable_lessons": knowledge_data.get('actionable_lessons'),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading knowledge summary: {e}")
    
