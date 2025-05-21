import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from backend.db.models import AuditLog

logger = logging.getLogger("metaai.audit")


class AuditLogger:
    def __init__(self, db_session_factory=None):
        self._db_session_factory = db_session_factory
        self._pending: list[dict] = []

    async def log_action(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None,
    ) -> dict:
        log_entry = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details,
            "ip_address": ip_address,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._pending.append(log_entry)
        logger.info("Audit: %s on %s %s by user %s", action, resource_type, resource_id or "", user_id or "anonymous")

        if self._db_session_factory:
            try:
                async with self._db_session_factory() as session:
                    audit = AuditLog(
                        id=uuid.UUID(log_entry["id"]),
                        user_id=uuid.UUID(user_id) if user_id else None,
                        action=action,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        details_json=json.dumps(details) if details else None,
                        ip_address=ip_address,
                    )
                    session.add(audit)
                    await session.commit()
            except Exception as e:
                logger.warning("Failed to persist audit log to DB: %s", e)

        return log_entry

    async def log_tool_call(
        self,
        tool_name: str,
        user_id: Optional[str] = None,
        parameters: Optional[dict] = None,
        ip_address: Optional[str] = None,
    ) -> dict:
        return await self.log_action(
            action="tool_call",
            resource_type=tool_name,
            user_id=user_id,
            details={"parameters": parameters},
            ip_address=ip_address,
        )

    async def log_agent_execution(
        self,
        agent_id: str,
        user_id: Optional[str] = None,
        input_summary: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> dict:
        return await self.log_action(
            action="agent_execute",
            resource_type="agent",
            resource_id=agent_id,
            user_id=user_id,
            details={"input_preview": input_summary},
            ip_address=ip_address,
        )

    async def log_model_call(
        self,
        model: str,
        user_id: Optional[str] = None,
        tokens: Optional[int] = None,
        cost: Optional[float] = None,
    ) -> dict:
        return await self.log_action(
            action="model_call",
            resource_type="model",
            resource_id=model,
            user_id=user_id,
            details={"tokens": tokens, "cost": cost},
        )

    async def log_auth_event(
        self,
        action: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        success: bool = True,
    ) -> dict:
        return await self.log_action(
            action=f"auth_{action}",
            resource_type="auth",
            user_id=user_id,
            details={"success": success},
            ip_address=ip_address,
        )

    def get_pending_events(self) -> list[dict]:
        return self._pending

    def clear_pending(self):
        self._pending.clear()


audit_logger = AuditLogger()
