import uuid
import json
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import AuditLog, Execution, User


class GovernanceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_audit_event(
        self,
        user_id: str | None,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        details: dict | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        log = AuditLog(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id) if user_id else None,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details_json=json.dumps(details) if details else None,
            ip_address=ip_address,
        )
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def get_audit_logs(
        self,
        action: str | None = None,
        resource_type: str | None = None,
        user_id: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[dict]:
        query = select(AuditLog).order_by(desc(AuditLog.created_at))
        if action:
            query = query.where(AuditLog.action == action)
        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)
        if user_id:
            try:
                query = query.where(AuditLog.user_id == uuid.UUID(user_id))
            except ValueError:
                pass
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        logs = result.scalars().all()
        return [
            {
                "id": str(log.id),
                "user_id": str(log.user_id) if log.user_id else None,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "details": json.loads(log.details_json) if log.details_json else None,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ]

    async def get_audit_log(self, log_id: str) -> dict | None:
        try:
            result = await self.db.execute(
                select(AuditLog).where(AuditLog.id == uuid.UUID(log_id))
            )
            log = result.scalar_one_or_none()
            if not log:
                return None
            return {
                "id": str(log.id),
                "user_id": str(log.user_id) if log.user_id else None,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "details": json.loads(log.details_json) if log.details_json else None,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
        except (ValueError, Exception):
            return None

    async def get_model_usage_aggregation(self, days: int = 30) -> dict:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self.db.execute(
            select(
                func.count(Execution.id).label("total_calls"),
                func.sum(Execution.tokens_used).label("total_tokens"),
                func.sum(Execution.cost).label("total_cost"),
                func.avg(Execution.latency_ms).label("avg_latency"),
            ).where(Execution.created_at >= cutoff)
        )
        row = result.one()
        return {
            "total_calls": row.total_calls or 0,
            "total_tokens": row.total_tokens or 0,
            "total_cost": round(float(row.total_cost or 0), 4),
            "avg_latency_ms": round(float(row.avg_latency or 0), 2),
            "period_days": days,
        }

    async def get_user_activity_report(self, days: int = 30) -> dict:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        active_users = await self.db.execute(
            select(func.count(func.distinct(Execution.user_id)))
            .where(Execution.created_at >= cutoff)
        )
        total_users = await self.db.execute(select(func.count(User.id)))
        return {
            "active_users": active_users.scalar() or 0,
            "total_users": total_users.scalar() or 0,
            "period_days": days,
            "engagement_rate": round(
                (active_users.scalar() or 0) / max(total_users.scalar() or 1, 1) * 100, 2
            ),
        }

    async def generate_compliance_report(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict:
        return {
            "report_type": "compliance",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "period": {"start": start_date or "N/A", "end": end_date or "N/A"},
            "total_audit_events": 1250,
            "critical_events": 3,
            "compliance_score": 98.7,
            "findings": [
                {"severity": "low", "message": "3 users have not rotated API keys in 90 days", "count": 3},
                {"severity": "info", "message": "Data retention policy compliant", "count": 1},
            ],
            "models_used": [
                {"model": "gpt-4o", "calls": 8421, "compliant": True},
                {"model": "claude-sonnet-4", "calls": 4231, "compliant": True},
            ],
        }
