import json
from typing import Dict, Any

def format_output_json(data: Dict[str, Any]) -> str:
    """Formats a dictionary into a pretty-printed JSON string."""
    return json.dumps(data, indent=2)

def parse_user_input_for_agents(user_input_raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processes raw user input (e.g., from a Pydantic model) into a standardized format
    that individual agents can easily consume. This acts as a central data hub for agents.
    """
    # This structure can be expanded as your project input becomes more complex.
    # For now, it directly passes the structured input.
    return {
        "project_description": user_input_raw.get("project_description", ""),
        "client_name": user_input_raw.get("client_name", "N/A"),
        "budget_range": user_input_raw.get("budget_range", "N/A"),
        "location": user_input_raw.get("location", "unspecified"),
        "desired_features": user_input_raw.get("desired_features", []),
        "initial_ideas_url": user_input_raw.get("initial_ideas_url", None),
        "project_type": user_input_raw.get("project_type", "residential"), # Ensure project_type is passed
        "project_size": user_input_raw.get("project_size", "medium") # Also pass project_size
    }