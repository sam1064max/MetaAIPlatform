from datetime import datetime, timezone, timedelta
import random

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_db
from backend.security.auth import get_current_user

router = APIRouter()


def _mock_cost_trends(days: int) -> list[dict]:
    start = datetime.now(timezone.utc) - timedelta(days=days)
    trends = []
    for i in range(days):
        day = start + timedelta(days=i)
        trends.append({
            "date": day.strftime("%Y-%m-%d"),
            "total_cost": round(random.uniform(5.0, 150.0), 2),
            "gpt4o_cost": round(random.uniform(2.0, 60.0), 2),
            "claude_cost": round(random.uniform(1.0, 40.0), 2),
            "deepseek_cost": round(random.uniform(0.5, 30.0), 2),
            "total_tokens": random.randint(50000, 2000000),
        })
    return trends


def _mock_token_usage(days: int) -> list[dict]:
    start = datetime.now(timezone.utc) - timedelta(days=days)
    usage = []
    for i in range(days):
        day = start + timedelta(days=i)
        usage.append({
            "date": day.strftime("%Y-%m-%d"),
            "input_tokens": random.randint(30000, 1200000),
            "output_tokens": random.randint(10000, 800000),
            "total_tokens": random.randint(40000, 2000000),
        })
    return usage


@router.get("/dashboard/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return {
        "platform": "MetaAI Platform",
        "total_agents": 47,
        "active_agents": 32,
        "total_executions": 15832,
        "executions_today": 342,
        "total_tokens_used": 45231890,
        "total_cost_usd": 12458.73,
        "avg_latency_ms": 1842,
        "success_rate_pct": 96.7,
        "active_users": 128,
        "registered_tools": 56,
        "knowledge_bases": 23,
        "evaluations_run": 892,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/dashboard/cost-trends")
async def get_cost_trends(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return {"trends": _mock_cost_trends(days), "currency": "USD", "period_days": days}


@router.get("/dashboard/token-usage")
async def get_token_usage(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return {"usage": _mock_token_usage(days), "period_days": days}


@router.get("/dashboard/agent-activity")
async def get_agent_activity(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    start = datetime.now(timezone.utc) - timedelta(days=days)
    activity = []
    for i in range(days):
        day = start + timedelta(days=i)
        activity.append({
            "date": day.strftime("%Y-%m-%d"),
            "executions": random.randint(50, 400),
            "successful": random.randint(45, 390),
            "failed": random.randint(0, 20),
            "unique_agents": random.randint(10, 35),
        })
    return {"activity": activity, "period_days": days}


@router.get("/dashboard/model-usage")
async def get_model_usage(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return {
        "models": [
            {"model": "gpt-4o", "calls": 8421, "tokens": 18520000, "cost": 4820.50, "percentage": 42.5},
            {"model": "claude-sonnet-4", "calls": 4231, "tokens": 10340000, "cost": 2890.30, "percentage": 21.4},
            {"model": "deepseek-v3", "calls": 3610, "tokens": 8910000, "cost": 892.40, "percentage": 18.2},
            {"model": "gemini-2", "calls": 2105, "tokens": 4520000, "cost": 452.10, "percentage": 10.6},
            {"model": "gpt-5", "calls": 892, "tokens": 2180000, "cost": 1450.80, "percentage": 4.5},
            {"model": "ollama", "calls": 573, "tokens": 720000, "cost": 0.00, "percentage": 2.8},
        ],
        "total_calls": 19832,
        "total_tokens": 45220000,
        "total_cost": 10506.10,
    }
