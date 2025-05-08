from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from backend.schemas.evaluation import EvaluationCreate, EvaluationResponse, EvaluationRunRequest
from backend.security.auth import get_current_user
from backend.services.evaluation_service import EvaluationService

router = APIRouter()


@router.get("", response_model=list[EvaluationResponse])
async def list_evaluations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = EvaluationService(db)
    return await service.list_evaluations(skip=skip, limit=limit)


@router.post("", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED)
async def create_evaluation(
    body: EvaluationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = EvaluationService(db)
    return await service.create_evaluation(body)


@router.get("/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation(
    evaluation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = EvaluationService(db)
    evaluation = await service.get_evaluation(evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation not found")
    return evaluation


@router.post("/run")
async def run_evaluation(
    body: EvaluationRunRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = EvaluationService(db)
    return await service.run_golden_dataset_eval(body.agent_id, body.test_inputs, body.expected_outputs)


@router.get("/agent/{agent_id}", response_model=list[EvaluationResponse])
async def get_agent_evaluations(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = EvaluationService(db)
    return await service.get_agent_evaluations(agent_id)
