"""
This file dynamically initializes the ADK system and registers all agents
found in the 'core_agents' and 'specialist_agents' directories.
"""

import os
import importlib
from typing import Dict, Optional

# Assuming BaseConstructionAgent is now in adk_core.base_agent
from .base_agent import BaseConstructionAgent

# Global variable to hold initialized agents
_adk_agents: Optional[Dict[str, BaseConstructionAgent]] = None

def to_camel_case(snake_str: str) -> str:
    """Converts a snake_case string to CamelCase."""
    return "".join(word.capitalize() for word in snake_str.split('_'))

def initialize_adk_system_with_agents():
    """
    Dynamically discovers, imports, and initializes all agents from the
    'core_agents' and 'specialist_agents' directories.
    """
    global _adk_agents
    if _adk_agents is not None:
        return _adk_agents

    _adk_agents = {}
    agent_dirs = ['core_agents', 'specialist_agents']
    base_path = os.path.dirname(__file__)

    for agent_dir in agent_dirs:
        dir_path = os.path.join(base_path, agent_dir)
        if not os.path.exists(dir_path):
            continue

        for filename in os.listdir(dir_path):
            if filename.endswith('_agent.py') and filename != '__init__.py':
                module_name = filename[:-3]  # Remove .py
                # Convert file name (snake_case) to class name (CamelCase)
                class_name = to_camel_case(module_name)
                
                try:
                    # Dynamically import the module
                    module = importlib.import_module(f".{agent_dir}.{module_name}", package='adk_core')
                    # Get the class from the module
                    agent_class = getattr(module, class_name)
                    # Instantiate the agent and add it to the dictionary
                    agent_instance = agent_class()
                    # The key will be the module name (e.g., 'briefing_constraint_extraction_agent')
                    _adk_agents[module_name] = agent_instance
                    print(f"Successfully loaded agent: {module_name}")
                except (ImportError, AttributeError) as e:
                    print(f"Failed to load agent {module_name} from {filename}: {e}")
    
    print(f"Successfully registered ADK agents: {list(_adk_agents.keys())}")
    return _adk_agents

def get_adk_system() -> Dict[str, BaseConstructionAgent]:
    """
    Provides access to the initialized ADK agents map.
    """
    if _adk_agents is None:
        initialize_adk_system_with_agents()
    return _adk_agents