from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ToolCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    mcp_server: str = ""
    tool_type: str = "function"
    parameters_json: str = "{}"


class ToolUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    mcp_server: Optional[str] = None
    tool_type: Optional[str] = None
    parameters_json: Optional[str] = None
    status: Optional[str] = None


class ToolResponse(BaseModel):
    id: str
    name: str
    description: str
    mcp_server: str
    tool_type: str
    parameters_json: str
    status: str
    created_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ToolTestRequest(BaseModel):
    parameters: dict = {}
