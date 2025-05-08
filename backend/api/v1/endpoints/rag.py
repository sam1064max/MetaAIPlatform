from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from backend.schemas.rag import (
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
    DocumentResponse,
    RAGQueryRequest,
    RAGQueryResponse,
    RetrievalMetrics,
)
from backend.security.auth import get_current_user
from backend.services.rag_service import RAGService

router = APIRouter()


@router.get("/knowledge-bases", response_model=list[KnowledgeBaseResponse])
async def list_knowledge_bases(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = RAGService(db)
    return await service.list_knowledge_bases(skip=skip, limit=limit)


@router.post("/knowledge-bases", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(
    body: KnowledgeBaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = RAGService(db)
    return await service.create_knowledge_base(body, user_id=current_user["sub"])


@router.get("/knowledge-bases/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    kb_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = RAGService(db)
    kb = await service.get_knowledge_base(kb_id)
    if not kb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge base not found")
    return kb


@router.post("/knowledge-bases/{kb_id}/upload", response_model=DocumentResponse)
async def upload_document(
    kb_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = RAGService(db)
    content = await file.read()
    return await service.process_document(kb_id, file.filename or "unknown", content)


@router.get("/knowledge-bases/{kb_id}/documents", response_model=list[DocumentResponse])
async def list_documents(
    kb_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = RAGService(db)
    return await service.list_documents(kb_id)


@router.post("/knowledge-bases/{kb_id}/query", response_model=RAGQueryResponse)
async def query_knowledge_base(
    kb_id: str,
    body: RAGQueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = RAGService(db)
    return await service.query_knowledge_base(kb_id, body)


@router.delete("/knowledge-bases/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_base(
    kb_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = RAGService(db)
    deleted = await service.delete_knowledge_base(kb_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge base not found")


@router.get("/knowledge-bases/{kb_id}/retrieval-metrics", response_model=RetrievalMetrics)
async def get_retrieval_metrics(
    kb_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = RAGService(db)
    return await service.get_retrieval_metrics(kb_id)
