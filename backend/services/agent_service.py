import uuid
import json
import time
from datetime import datetime, timezone

import yaml
from sqlalchemy import select, desc, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import Agent, AgentVersion, Execution
from backend.schemas.agent import AgentCreate, AgentUpdate, AgentExecutionRequest, AgentExecutionResponse


class AgentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_agent(self, body: AgentCreate, user_id: str) -> Agent:
        agent = Agent(
            id=uuid.uuid4(),
            name=body.name,
            description=body.description,
            config_yaml=body.config_yaml,
            status="draft",
            created_by=uuid.UUID(user_id) if user_id else None,
        )
        self.db.add(agent)

        if body.config_yaml:
            parsed = self.parse_agent_config(body.config_yaml)
            agent.version = parsed.get("version", "1.0.0")

        version = AgentVersion(
            id=uuid.uuid4(),
            agent_id=agent.id,
            version_number=agent.version,
            config_yaml=body.config_yaml,
            created_by=agent.created_by,
        )
        self.db.add(version)
        await self.db.commit()
        await self.db.refresh(agent)
        return agent

    async def get_agent(self, agent_id: str) -> Agent | None:
        try:
            result = await self.db.execute(select(Agent).where(Agent.id == uuid.UUID(agent_id)))
            return result.scalar_one_or_none()
        except (ValueError, Exception):
            return None

    async def update_agent(self, agent_id: str, body: AgentUpdate) -> Agent | None:
        agent = await self.get_agent(agent_id)
        if not agent:
            return None

        update_data = body.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(agent, field, value)

        if body.config_yaml is not None:
            parsed = self.parse_agent_config(body.config_yaml)
            version_num = parsed.get("version", "1.0.0")
            agent.version = version_num
            version = AgentVersion(
                id=uuid.uuid4(),
                agent_id=agent.id,
                version_number=version_num,
                config_yaml=body.config_yaml,
                created_by=agent.created_by,
            )
            self.db.add(version)

        agent.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(agent)
        return agent

    async def delete_agent(self, agent_id: str) -> bool:
        agent = await self.get_agent(agent_id)
        if not agent:
            return False
        await self.db.delete(agent)
        await self.db.commit()
        return True

    async def execute_agent(
        self,
        agent_id: str,
        body: AgentExecutionRequest,
        user_id: str,
    ) -> AgentExecutionResponse:
        agent = await self.get_agent(agent_id)
        if not agent:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=404, detail="Agent not found")

        start = time.monotonic()
        try:
            from backend.gateway.model_gateway import ModelGateway

            config = self.parse_agent_config(agent.config_yaml) if agent.config_yaml else {}
            model = config.get("model", "gpt-4o")
            system_prompt = config.get("system_prompt", "")

            gateway = ModelGateway()
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": body.input})

            llm_response = await gateway.chat_completion(model=model, messages=messages)

            output = llm_response.get("content", "")
            tokens_used = llm_response.get("total_tokens", 0)
            cost = llm_response.get("cost", 0.0)
            latency_ms = int((time.monotonic() - start) * 1000)
            status_val = "completed"
            error_val = None
        except Exception as e:
            output = ""
            tokens_used = 0
            cost = 0.0
            latency_ms = int((time.monotonic() - start) * 1000)
            status_val = "failed"
            error_val = str(e)

        execution = Execution(
            id=uuid.uuid4(),
            agent_id=agent.id,
            user_id=uuid.UUID(user_id) if user_id else None,
            input=body.input,
            output=output,
            tokens_used=tokens_used,
            cost=cost,
            latency_ms=latency_ms,
            status=status_val,
            error=error_val,
            trace_id=str(uuid.uuid4()),
        )
        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(execution)

        return AgentExecutionResponse(
            execution_id=str(execution.id),
            agent_id=str(execution.agent_id),
            input=execution.input,
            output=execution.output,
            tokens_used=execution.tokens_used,
            cost=execution.cost,
            latency_ms=execution.latency_ms,
            status=execution.status,
            created_at=execution.created_at,
        )

    async def list_agents(
        self,
        skip: int = 0,
        limit: int = 100,
        status_filter: str | None = None,
    ) -> list[Agent]:
        query = select(Agent).order_by(desc(Agent.created_at)).offset(skip).limit(limit)
        if status_filter:
            query = query.where(Agent.status == status_filter)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def list_versions(self, agent_id: str) -> list[dict]:
        try:
            result = await self.db.execute(
                select(AgentVersion)
                .where(AgentVersion.agent_id == uuid.UUID(agent_id))
                .order_by(desc(AgentVersion.created_at))
            )
            versions = result.scalars().all()
            return [
                {
                    "id": str(v.id),
                    "agent_id": str(v.agent_id),
                    "version_number": v.version_number,
                    "created_by": str(v.created_by) if v.created_by else None,
                    "created_at": v.created_at.isoformat() if v.created_at else None,
                }
                for v in versions
            ]
        except (ValueError, Exception):
            return []

    async def list_executions(
        self,
        agent_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> list[dict]:
        try:
            result = await self.db.execute(
                select(Execution)
                .where(Execution.agent_id == uuid.UUID(agent_id))
                .order_by(desc(Execution.created_at))
                .offset(skip)
                .limit(limit)
            )
            executions = result.scalars().all()
            return [
                {
                    "id": str(e.id),
                    "agent_id": str(e.agent_id) if e.agent_id else None,
                    "input": e.input[:200] if e.input else "",
                    "output": e.output[:500] if e.output else "",
                    "tokens_used": e.tokens_used,
                    "cost": e.cost,
                    "latency_ms": e.latency_ms,
                    "status": e.status,
                    "created_at": e.created_at.isoformat() if e.created_at else None,
                }
                for e in executions
            ]
        except (ValueError, Exception):
            return []

    @staticmethod
    def parse_agent_config(config_yaml: str) -> dict:
        if not config_yaml:
            return {}
        try:
            return yaml.safe_load(config_yaml) or {}
        except yaml.YAMLError:
            return {}
