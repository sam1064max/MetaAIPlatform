from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    name: str = ""
    description: str = ""
    parameters: Dict[str, Any] = {}

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        ...

    @abstractmethod
    async def validate(self, **kwargs) -> bool:
        ...

    def get_discovery_metadata(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


class ToolExecutionError(Exception):
    def __init__(self, tool_name: str, message: str, details: Dict[str, Any] | None = None):
        self.tool_name = tool_name
        self.details = details or {}
        super().__init__(f"[{tool_name}] {message}")
