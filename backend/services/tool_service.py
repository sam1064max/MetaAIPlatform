import uuid
import json
from datetime import datetime, timezone

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import Tool
from backend.schemas.tool import ToolCreate, ToolUpdate


class ToolService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_tool(self, body: ToolCreate, user_id: str) -> Tool:
        tool = Tool(
            id=uuid.uuid4(),
            name=body.name,
            description=body.description,
            mcp_server=body.mcp_server,
            tool_type=body.tool_type,
            parameters_json=body.parameters_json,
            status="draft",
            created_by=uuid.UUID(user_id) if user_id else None,
        )
        self.db.add(tool)
        await self.db.commit()
        await self.db.refresh(tool)
        return tool

    async def get_tool(self, tool_id: str) -> Tool | None:
        try:
            result = await self.db.execute(select(Tool).where(Tool.id == uuid.UUID(tool_id)))
            return result.scalar_one_or_none()
        except (ValueError, Exception):
            return None

    async def update_tool(self, tool_id: str, body: ToolUpdate) -> Tool | None:
        tool = await self.get_tool(tool_id)
        if not tool:
            return None
        update_data = body.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(tool, field, value)
        await self.db.commit()
        await self.db.refresh(tool)
        return tool

    async def test_tool(self, tool_id: str, parameters: dict) -> dict:
        tool = await self.get_tool(tool_id)
        if not tool:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")

        from backend.tools.registry import ToolRegistry
        registry = ToolRegistry()
        mcp_tool = registry.get_tool(tool.name)
        if mcp_tool:
            try:
                result = await mcp_tool.execute(**parameters)
                return {"tool_id": tool_id, "tool_name": tool.name, "status": "success", "result": result}
            except Exception as e:
                return {"tool_id": tool_id, "tool_name": tool.name, "status": "error", "error": str(e)}

        return {
            "tool_id": tool_id,
            "tool_name": tool.name,
            "status": "mock",
            "result": {"message": f"Mock execution of {tool.name}", "parameters": parameters},
        }

    async def publish_tool(self, tool_id: str) -> Tool | None:
        tool = await self.get_tool(tool_id)
        if not tool:
            return None
        tool.status = "published"
        await self.db.commit()
        await self.db.refresh(tool)
        return tool

    async def list_tools(self, skip: int = 0, limit: int = 100) -> list[Tool]:
        result = await self.db.execute(
            select(Tool).order_by(desc(Tool.created_at)).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
