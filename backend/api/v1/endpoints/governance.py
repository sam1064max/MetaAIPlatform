from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from backend.security.auth import get_current_user, require_role
from backend.services.governance_service import GovernanceService

router = APIRouter()
admin_only = require_role(["admin", "superadmin"])


@router.get("/audit-logs")
async def list_audit_logs(
    action: str | None = Query(None),
    resource_type: str | None = Query(None),
    user_id: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(admin_only),
):
    service = GovernanceService(db)
    return await service.get_audit_logs(
        action=action,
        resource_type=resource_type,
        user_id=user_id,
        skip=skip,
        limit=limit,
    )


@router.get("/audit-logs/{log_id}")
async def get_audit_log(
    log_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(admin_only),
):
    service = GovernanceService(db)
    return await service.get_audit_log(log_id)


@router.get("/model-usage")
async def get_model_usage(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(admin_only),
):
    service = GovernanceService(db)
    return await service.get_model_usage_aggregation(days=days)


@router.get("/user-activity")
async def get_user_activity(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(admin_only),
):
    service = GovernanceService(db)
    return await service.get_user_activity_report(days=days)


@router.get("/compliance-report")
async def get_compliance_report(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(admin_only),
):
    service = GovernanceService(db)
    return await service.generate_compliance_report(start_date=start_date, end_date=end_date)
