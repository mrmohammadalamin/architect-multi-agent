from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path

class BaseConstructionAgent(ABC):
    """Abstract base class for all construction-related AI agents."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def process_request(self, user_input: Dict[str, Any], project_path: Path) -> Dict[str, Any]:
        """
        Abstract method to process a user request specific to the agent's domain.
        Each specialized agent *must* implement this method.

        Args:
            user_input: A dictionary containing parsed user request details.
            project_path: The path to the project's directory in the project_store,
                        where all artifacts should be saved.

        Returns:
            A dictionary containing the agent's specific output, including status
            and paths to any generated artifacts.
        """
        pass

    def get_description(self) -> str:
        """Returns the agent's description."""
        return self.description
