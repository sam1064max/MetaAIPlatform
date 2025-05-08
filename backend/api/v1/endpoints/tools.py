from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from backend.schemas.tool import ToolCreate, ToolUpdate, ToolResponse, ToolTestRequest
from backend.security.auth import get_current_user
from backend.services.tool_service import ToolService

router = APIRouter()


@router.get("", response_model=list[ToolResponse])
async def list_tools(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = ToolService(db)
    return await service.list_tools(skip=skip, limit=limit)


@router.post("", response_model=ToolResponse, status_code=status.HTTP_201_CREATED)
async def register_tool(
    body: ToolCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = ToolService(db)
    return await service.register_tool(body, user_id=current_user["sub"])


@router.get("/{tool_id}", response_model=ToolResponse)
async def get_tool(
    tool_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = ToolService(db)
    tool = await service.get_tool(tool_id)
    if not tool:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")
    return tool


@router.put("/{tool_id}", response_model=ToolResponse)
async def update_tool(
    tool_id: str,
    body: ToolUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = ToolService(db)
    tool = await service.update_tool(tool_id, body)
    if not tool:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")
    return tool


@router.post("/{tool_id}/test")
async def test_tool(
    tool_id: str,
    body: ToolTestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = ToolService(db)
    return await service.test_tool(tool_id, body.parameters)


@router.post("/{tool_id}/publish", response_model=ToolResponse)
async def publish_tool(
    tool_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = ToolService(db)
    tool = await service.publish_tool(tool_id)
    if not tool:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")
    return tool
