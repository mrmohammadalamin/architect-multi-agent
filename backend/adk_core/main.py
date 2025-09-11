import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

# --- IMPORTANT: Environment Variable Check & Loading ---
# Load environment variables from .env file at the very beginning
# This must happen before importing modules that depend on these variables (like settings).
from dotenv import load_dotenv
load_dotenv()

# Now it's safe to import settings and ADK components
from adk_core import get_adk_system # Function to get initialized ADK components
from adk_core.utils.common import parse_user_input_for_agents # Utility for input parsing
from adk_core.agents.base_agent import BaseConstructionAgent # For type hinting

# Global variables to store initialized ADK components.
# They will be populated during the FastAPI application's startup event.
adk_agents_map: Dict[str, BaseConstructionAgent] = {}
adk_resolver = None

# --- FastAPI App Setup ---
app = FastAPI(
    title="Construction AI Multi-Agent System",
    description="A multi-agent system for construction project planning and estimation, powered by Google ADK.",
    version="0.1.0",
)

# Configure CORS (Cross-Origin Resource Sharing) to allow requests from your frontend.
# Replace "http://localhost:3000" with the actual URL of your frontend application.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows requests from a React/Next.js app running on localhost:3000
    allow_credentials=True,
    allow_methods=["*"], # Allows all standard HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"], # Allows all headers
)

# --- Request Body Model for /process_project endpoint ---
class ProjectInput(BaseModel):
    """
    Defines the expected structure of the JSON payload sent by the user
    to the /process_project endpoint. This captures the core client inquiry.
    """
    project_type: str
    client_name: str
    budget_range: str
    location: str
    desired_features: List[str]
    initial_ideas_url: Optional[str] = None
    project_description: str # A summary description of the project
    project_size: str = "medium" # e.g., "small", "medium", "large"


# --- FastAPI Lifecycle Events ---
@app.on_event("startup")
async def startup_event():
    """
    This function runs once when the FastAPI application starts.
    It's used to initialize the ADK system and all its agents.
    """
    global adk_agents_map, adk_resolver
    print("FastAPI startup: Attempting to initialize ADK system...")
    try:
        # Call the function from adk_core/__init__.py to get initialized agents and resolver
        adk_agents_map, adk_resolver = get_adk_system()
        if not adk_agents_map:
            print("WARNING: ADK system initialized, but no agents were registered. Check adk_core/__init__.py.")
        print("FastAPI startup: ADK system and agents successfully loaded.")
    except Exception as e:
        print(f"FATAL ERROR: Failed to initialize ADK system during startup: {e}")
        # Raising an exception here will prevent the FastAPI server from starting,
        # which is usually desired if the core AI system components cannot load.
        raise RuntimeError(f"ADK system initialization failed: {e}")

# --- API Endpoints ---
@app.get("/")
async def read_root():
    """
    Basic health check endpoint to confirm the FastAPI server is running.
    """
    return {"message": "Construction AI Multi-Agent System is running! Access /docs for API documentation."}

@app.post("/process_project")
async def process_project(project_input: ProjectInput):
    """
    Receives detailed user input for a construction project and orchestrates
    all 18 AI agents to process it, returning a comprehensive analysis.
    """
    # Ensure agents are initialized before processing requests
    if not adk_agents_map:
        raise HTTPException(
            status_code=500,
            detail="ADK agents are not initialized. Server might have failed to start correctly. Check backend logs."
        )

    # Prepare the incoming structured user input for individual agents
    # This function allows you to transform or refine the input if needed.
    agent_input_data = parse_user_input_for_agents(project_input.model_dump())

    # This dictionary will accumulate outputs from all agents.
    # It starts with the initial user input, which can be enriched by agents.
    consolidated_data: Dict[str, Any] = {
        "project_id": "proj_" + str(hash(frozenset(project_input.model_dump().items())))[:8], # Simple unique ID
        **agent_input_data
    }
    all_agent_outputs: Dict[str, Any] = {}
    successful_agents_count = 0

    print(f"\n--- Orchestration Started for Project: '{consolidated_data['project_description'][:70]}...' ---")
    print(f"Initial Input: {consolidated_data}")

    # Define the order of agents for a structured workflow.
    # The order is crucial as some agents (e.g., Architectural Design) depend on outputs
    # from previous agents (e.g., Site Intelligence).
    agent_execution_order = [
        "strategic_client_engagement_agent",
        "site_intelligence_regulatory_compliance_agent",
        "generative_architectural_design_agent",
        "integrated_systems_engineering_agent",
        "interior_experiential_design_agent",
        "hyper_realistic_3d_digital_twin_agent",
        "predictive_cost_supply_chain_agent",
        "adaptive_project_management_robotics_orchestration_agent",
        "proactive_risk_safety_management_agent",
        "ai_driven_quality_assurance_control_agent",
        "semantic_data_integration_ontology_agent",
        "learning_adaptation_agent",
        "sustainability_green_building_agent",
        "financial_investment_analysis_agent",
        "legal_contract_management_agent",
        "workforce_management_hr_agent",
        "post_construction_facility_management_agent",
        "public_relations_stakeholder_communication_agent",
        "human_ai_collaboration_explainability_agent", # Often last to summarize for humans
    ]

    # Execute agents in defined order, passing consolidated data
    for agent_key in agent_execution_order:
        agent_instance = adk_agents_map.get(agent_key)
        if not agent_instance:
            print(f"WARNING: Agent '{agent_key}' not found in map. Skipping.")
            all_agent_outputs[agent_key] = {
                "agent_name": agent_key,
                "status": "skipped",
                "message": "Agent not found or initialized."
            }
            continue

        print(f"  > Calling {agent_instance.name} ({agent_key})...")
        try:
            # Each agent receives the current `consolidated_data`.
            # Agents are expected to ADD their results to this data.
            agent_output = agent_instance.process_request(consolidated_data.copy()) # Pass a copy to avoid modification issues
            
            # Store the agent's direct output
            all_agent_outputs[agent_key] = agent_output

            if agent_output.get("status") == "success":
                successful_agents_count += 1
                # If an agent successfully produces structured data, add it to consolidated_data
                # This makes the output of one agent available as input to subsequent agents.
                # Example: If a "budget_agent" returns {"estimated_budget": {...}},
                # we update consolidated_data with {"estimated_budget": {...}}.
                for key, value in agent_output.items():
                    if key not in ["agent_name", "status", "message", "raw_llm_response"]: # Exclude metadata keys
                        consolidated_data[key] = value

            print(f"    < {agent_instance.name} status: {agent_output.get('status', 'unknown')}")
        except Exception as e:
            # Catch unexpected errors during agent processing
            print(f"    < ERROR: Unexpected exception processing with {agent_instance.name}: {e}")
            import traceback
            traceback.print_exc() # Print full traceback for debugging
            all_agent_outputs[agent_key] = {
                "agent_name": agent_instance.name,
                "status": "error",
                "message": f"An unexpected error occurred during processing by {agent_instance.name}: {str(e)}"
            }

    # --- Final Aggregation and Response Synthesis ---
    total_executed_agents = len(agent_execution_order)
    overall_status = "success"
    if successful_agents_count == 0:
        overall_status = "failure"
    elif successful_agents_count < total_executed_agents:
        overall_status = "partial_success"

    # Construct the final response sent back to the frontend
    final_response = {
        "overall_status": overall_status,
        "user_input_received": project_input.model_dump(), # Echo back the original user input
        "consolidated_project_data": consolidated_data, # The accumulated data after all agents ran
        "agent_outputs_raw": all_agent_outputs, # Detailed raw output from each agent call
        "summary_message": "Comprehensive project analysis generated by AI agents. Review 'consolidated_project_data' and 'agent_outputs_raw' for details."
    }

    print("--- Orchestration Complete. Response being sent. ---")
    return final_response