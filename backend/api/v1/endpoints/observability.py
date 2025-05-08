import uuid
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from backend.db.models import Execution, AuditLog
from backend.security.auth import get_current_user

router = APIRouter()


@router.get("/traces")
async def list_traces(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    query = select(Execution).order_by(Execution.created_at.desc())
    if status:
        query = query.where(Execution.status == status)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    executions = result.scalars().all()
    return [
        {
            "trace_id": e.trace_id or str(e.id),
            "execution_id": str(e.id),
            "agent_id": str(e.agent_id) if e.agent_id else None,
            "user_id": str(e.user_id) if e.user_id else None,
            "status": e.status,
            "latency_ms": e.latency_ms,
            "tokens_used": e.tokens_used,
            "cost": e.cost,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in executions
    ]


@router.get("/traces/{trace_id}")
async def get_trace_detail(
    trace_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(
        select(Execution).where(
            (Execution.trace_id == trace_id) | (Execution.id == uuid.UUID(trace_id))
        )
    )
    execution = result.scalar_one_or_none()
    if not execution:
        return {"detail": "Trace not found"}, 404
    return {
        "trace_id": execution.trace_id or str(execution.id),
        "execution_id": str(execution.id),
        "agent_id": str(execution.agent_id) if execution.agent_id else None,
        "user_id": str(execution.user_id) if execution.user_id else None,
        "input": execution.input,
        "output": execution.output,
        "status": execution.status,
        "error": execution.error,
        "tokens_used": execution.tokens_used,
        "cost": execution.cost,
        "latency_ms": execution.latency_ms,
        "created_at": execution.created_at.isoformat() if execution.created_at else None,
    }


@router.get("/agent-calls")
async def get_agent_calls(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(
            Execution.agent_id,
            func.count(Execution.id).label("total_calls"),
            func.avg(Execution.latency_ms).label("avg_latency"),
            func.avg(Execution.tokens_used).label("avg_tokens"),
            func.sum(Execution.cost).label("total_cost"),
        )
        .where(Execution.created_at >= cutoff)
        .group_by(Execution.agent_id)
        .order_by(func.count(Execution.id).desc())
    )
    rows = result.all()
    return [
        {
            "agent_id": str(r.agent_id) if r.agent_id else None,
            "total_calls": r.total_calls,
            "avg_latency_ms": round(float(r.avg_latency), 2) if r.avg_latency else 0,
            "avg_tokens": round(float(r.avg_tokens), 0) if r.avg_tokens else 0,
            "total_cost": round(float(r.total_cost), 4) if r.total_cost else 0,
        }
        for r in rows
    ]


@router.get("/tool-calls")
async def get_tool_calls(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    audit_result = await db.execute(
        select(
            AuditLog.resource_type,
            func.count(AuditLog.id).label("count"),
        )
        .where(
            AuditLog.created_at >= cutoff,
            AuditLog.action == "tool_call",
        )
        .group_by(AuditLog.resource_type)
    )
    rows = audit_result.all()
    return [{"tool_type": r.resource_type, "call_count": r.count} for r in rows]


@router.get("/failure-analysis")
async def get_failure_analysis(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    total = await db.execute(
        select(func.count(Execution.id)).where(Execution.created_at >= cutoff)
    )
    total_count = total.scalar() or 1
    failed = await db.execute(
        select(func.count(Execution.id)).where(
            Execution.created_at >= cutoff,
            Execution.status == "failed",
        )
    )
    failed_count = failed.scalar() or 0
    return {
        "total_executions": total_count,
        "failed_executions": failed_count,
        "failure_rate": round(failed_count / total_count * 100, 2),
        "period_days": days,
    }


@router.get("/cost-analysis")
async def get_cost_analysis(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(
            func.sum(Execution.cost).label("total_cost"),
            func.sum(Execution.tokens_used).label("total_tokens"),
        ).where(Execution.created_at >= cutoff)
    )
    row = result.one()
    return {
        "total_cost": round(float(row.total_cost or 0), 4),
        "total_tokens": row.total_tokens or 0,
        "period_days": days,
        "avg_cost_per_day": round(float(row.total_cost or 0) / max(days, 1), 4),
    }
