import asyncio
import uuid

from backend.db import async_session, init_db
from backend.db.models import User, Tool, Agent, AgentVersion, KnowledgeBase


ADMIN_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


SAMPLE_AGENTS = [
    {
        "name": "Wealth Advisor Agent",
        "description": "Personalized wealth management and portfolio advisory. Analyzes market trends, assesses risk tolerance, and provides tailored investment strategies.",
        "config_yaml": """agent:
  name: WealthAdvisor
  version: 1.0.0
  system_prompt: You are a senior wealth advisor. Analyze portfolios, assess risk, and recommend investment strategies.
  model:
    provider: openai
    name: gpt-4o
    temperature: 0.3
  memory:
    type: redis
  workflow:
    pattern: plan-and-execute
  tools:
    - market_data
    - portfolio_analysis
""",
    },
    {
        "name": "Research Agent",
        "description": "Automated financial research and report generation. Synthesizes earnings calls, SEC filings, and market data into comprehensive research reports.",
        "config_yaml": """agent:
  name: ResearchAgent
  version: 1.0.0
  system_prompt: You are a financial research analyst. Synthesize data from multiple sources into actionable research reports.
  model:
    provider: anthropic
    name: claude-sonnet-4
    temperature: 0.2
  memory:
    type: redis
  workflow:
    pattern: supervisor
  tools:
    - research
    - news
""",
    },
    {
        "name": "Compliance Agent",
        "description": "Regulatory compliance checking and monitoring. Scans transactions and communications for regulatory breaches.",
        "config_yaml": """agent:
  name: ComplianceAgent
  version: 1.0.0
  system_prompt: You are a compliance officer. Monitor transactions and communications for regulatory breaches.
  model:
    provider: openai
    name: gpt-4o
    temperature: 0.1
  memory:
    type: redis
  workflow:
    pattern: react
  tools:
    - crm
    - research
""",
    },
]


SAMPLE_TOOLS = [
    {"name": "market_data", "description": "Real-time market data and quotes from multiple exchanges", "mcp_server": "market-data-server", "tool_type": "api", "parameters_json": '{"symbol": {"type": "string", "required": true}, "exchange": {"type": "string", "default": "NYSE"}}'},
    {"name": "portfolio_analysis", "description": "Portfolio performance analytics with returns, volatility, and Sharpe ratio", "mcp_server": "portfolio-server", "tool_type": "function", "parameters_json": '{"portfolio_id": {"type": "string", "required": true}, "benchmark": {"type": "string", "default": "S&P500"}}'},
    {"name": "crm", "description": "Customer relationship data with transaction history and interaction logs", "mcp_server": "crm-server", "tool_type": "database", "parameters_json": '{"customer_id": {"type": "string", "required": true}}'},
    {"name": "research", "description": "Financial research reports, SEC filings, earnings transcripts", "mcp_server": "research-server", "tool_type": "api", "parameters_json": '{"query": {"type": "string", "required": true}, "max_results": {"type": "integer", "default": 10}}'},
    {"name": "news", "description": "Real-time financial news with sentiment analysis", "mcp_server": "news-server", "tool_type": "api", "parameters_json": '{"topics": {"type": "array", "required": true}, "timeframe": {"type": "string", "default": "24h"}}'},
]


async def seed():
    await init_db()
    async with async_session() as db:
        existing = await db.execute(__import__("sqlalchemy").select(User).where(User.id == ADMIN_ID))
        if existing.scalar_one_or_none():
            print("Seed data already exists, skipping")
            return

        admin = User(
            id=ADMIN_ID,
            username="admin",
            email="admin@meta-ai.com",
            hashed_password="$2b$12$LJ3m4ys3Lk0TSwHnbfOMqOX5eZmE5xJ7GxKzJfYy0Qy0Qy0Qy0Qy0",
            role="admin",
            is_active=True,
        )
        db.add(admin)

        for t in SAMPLE_TOOLS:
            tool = Tool(
                id=uuid.uuid4(),
                name=t["name"],
                description=t["description"],
                mcp_server=t["mcp_server"],
                tool_type=t["tool_type"],
                parameters_json=t["parameters_json"],
                status="published",
                created_by=ADMIN_ID,
            )
            db.add(tool)

        for a in SAMPLE_AGENTS:
            agent = Agent(
                id=uuid.uuid4(),
                name=a["name"],
                description=a["description"],
                version="1.0.0",
                config_yaml=a["config_yaml"],
                status="active",
                created_by=ADMIN_ID,
            )
            db.add(agent)
            version = AgentVersion(
                id=uuid.uuid4(),
                agent_id=agent.id,
                version_number="1.0.0",
                config_yaml=a["config_yaml"],
                created_by=ADMIN_ID,
            )
            db.add(version)

        kb = KnowledgeBase(
            id=uuid.uuid4(),
            name="Financial Documents",
            description="Sample financial documents and reports for RAG demonstrations",
            document_count=0,
            chunk_count=0,
            embedding_model="text-embedding-3-large",
            status="active",
            created_by=ADMIN_ID,
        )
        db.add(kb)

        await db.commit()
        print("Seed data created: admin user, 5 tools, 3 agents, 1 knowledge base")


if __name__ == "__main__":
    asyncio.run(seed())
