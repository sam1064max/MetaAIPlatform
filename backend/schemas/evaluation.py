from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class EvaluationCreate(BaseModel):
    agent_id: str
    execution_id: Optional[str] = None
    accuracy: Optional[float] = None
    groundedness: Optional[float] = None
    hallucination_rate: Optional[float] = None
    latency: Optional[float] = None
    cost: Optional[float] = None
    faithfulness: Optional[float] = None
    relevancy: Optional[float] = None
    answer_correctness: Optional[float] = None


class EvaluationResponse(BaseModel):
    id: str
    agent_id: Optional[str] = None
    execution_id: Optional[str] = None
    accuracy: Optional[float] = None
    groundedness: Optional[float] = None
    hallucination_rate: Optional[float] = None
    latency: Optional[float] = None
    cost: Optional[float] = None
    faithfulness: Optional[float] = None
    relevancy: Optional[float] = None
    answer_correctness: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class EvaluationRunRequest(BaseModel):
    agent_id: str
    test_inputs: list[str] = Field(..., min_length=1)
    expected_outputs: list[str] = Field(..., min_length=1)
