from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    name: str
    description: str = ""
    version: str = "1.0.0"
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 4096
    system_prompt: str = ""
    tools: list[str] = []
    workflow: str = "react"
    memory_enabled: bool = True
    human_approval: bool = False


class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    config_yaml: str = ""


class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    version: Optional[str] = None
    config_yaml: Optional[str] = None
    status: Optional[str] = None


class AgentResponse(BaseModel):
    id: str
    name: str
    description: str
    version: str
    config_yaml: str
    status: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentExecutionRequest(BaseModel):
    input: str = Field(..., min_length=1)
    session_id: Optional[str] = None
    stream: bool = False


class AgentExecutionResponse(BaseModel):
    execution_id: str
    agent_id: str
    input: str
    output: str
    tokens_used: int
    cost: float
    latency_ms: int
    status: str
    created_at: datetime
