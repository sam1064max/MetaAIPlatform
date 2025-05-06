from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class KnowledgeBaseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    embedding_model: str = "BAAI/bge-base-en-v1.5"


class KnowledgeBaseResponse(BaseModel):
    id: str
    name: str
    description: str
    document_count: int
    chunk_count: int
    embedding_model: str
    status: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: str
    knowledge_base_id: str
    filename: str
    file_type: str
    file_size: int
    chunk_count: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class RAGQueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)
    retrieval_strategy: str = "hybrid"
    rerank: bool = True


class RAGQueryResponse(BaseModel):
    query: str
    results: list[dict]
    total_chunks: int
    retrieval_time_ms: int
    strategy_used: str


class RetrievalMetrics(BaseModel):
    knowledge_base_id: str
    total_documents: int
    total_chunks: int
    avg_chunk_size: int
    embedding_model: str
    retrieval_count_24h: int
    avg_retrieval_latency_ms: float
