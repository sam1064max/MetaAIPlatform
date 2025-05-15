import logging
from typing import Any

from backend.tools.base import BaseTool, ToolExecutionError
from backend.tools.mcp.server import MarketDataServer, PortfolioServer, ResearchServer, CRMServer

logger = logging.getLogger("metaai.tools.registry")


class ToolRegistry:
    _instance: "ToolRegistry | None" = None
    _tools: dict[str, BaseTool] = {}

    def __new__(cls) -> "ToolRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_defaults()
        return cls._instance

    def _initialize_defaults(self):
        if not self._tools:
            defaults = [
                MarketDataServer(),
                PortfolioServer(),
                ResearchServer(),
                CRMServer(),
            ]
            for tool in defaults:
                self._tools[tool.name] = tool
            logger.info("Initialized %d default tools", len(defaults))

    def register_tool(self, tool: BaseTool):
        self._tools[tool.name] = tool
        logger.info("Registered tool: %s", tool.name)

    def get_tool(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters,
            }
            for t in self._tools.values()
        ]

    async def invoke_tool(self, name: str, **kwargs) -> dict[str, Any]:
        tool = self.get_tool(name)
        if not tool:
            raise ToolExecutionError(name, f"Tool '{name}' not found in registry")

        valid = await tool.validate(**kwargs)
        if not valid:
            raise ToolExecutionError(name, f"Validation failed for arguments: {kwargs}")

        logger.info("Invoking tool: %s with action: %s", name, kwargs.get("action"))
        return await tool.execute(**kwargs)


tool_registry = ToolRegistry()
