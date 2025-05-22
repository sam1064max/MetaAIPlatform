import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock

from backend.schemas.agent import AgentCreate, AgentUpdate, AgentExecutionRequest


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def agent_service(mock_db):
    from backend.services.agent_service import AgentService
    return AgentService(mock_db)


@pytest.mark.asyncio
async def test_create_agent(agent_service, mock_db):
    body = AgentCreate(name="Test Agent", description="Test", config_yaml="version: 1.0.0\nmodel: gpt-4o")
    user_id = str(uuid.uuid4())

    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    agent = await agent_service.create_agent(body, user_id)

    assert agent.name == "Test Agent"
    assert agent.status == "draft"
    assert mock_db.add.called
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_get_agent_found(agent_service, mock_db):
    from backend.db.models import Agent
    agent_id = str(uuid.uuid4())
    expected_agent = Agent(id=uuid.UUID(agent_id), name="Found Agent")

    result_mock = MagicMock()
    result_mock.scalar_one_or_none = MagicMock(return_value=expected_agent)
    mock_db.execute = AsyncMock(return_value=result_mock)

    agent = await agent_service.get_agent(agent_id)
    assert agent is not None
    assert agent.name == "Found Agent"


@pytest.mark.asyncio
async def test_get_agent_not_found(agent_service, mock_db):
    result_mock = MagicMock()
    result_mock.scalar_one_or_none = MagicMock(return_value=None)
    mock_db.execute = AsyncMock(return_value=result_mock)

    agent = await agent_service.get_agent(str(uuid.uuid4()))
    assert agent is None


@pytest.mark.asyncio
async def test_delete_agent(agent_service, mock_db):
    from backend.db.models import Agent
    agent_id = str(uuid.uuid4())
    agent = Agent(id=uuid.UUID(agent_id), name="To Delete")

    result_mock = MagicMock()
    result_mock.scalar_one_or_none = MagicMock(return_value=agent)
    mock_db.execute = AsyncMock(return_value=result_mock)
    mock_db.delete = AsyncMock()
    mock_db.commit = AsyncMock()

    result = await agent_service.delete_agent(agent_id)
    assert result is True
    assert mock_db.delete.called


@pytest.mark.asyncio
async def test_list_agents(agent_service, mock_db):
    from backend.db.models import Agent
    agents = [Agent(id=uuid.uuid4(), name=f"Agent {i}") for i in range(3)]

    result_mock = MagicMock()
    result_mock.scalars.return_value.all = MagicMock(return_value=agents)
    mock_db.execute = AsyncMock(return_value=result_mock)

    result = await agent_service.list_agents()
    assert len(result) == 3


@pytest.mark.asyncio
async def test_parse_agent_config(agent_service):
    config = "version: 2.0.0\nmodel: claude-sonnet-4\ntemperature: 0.5"
    parsed = agent_service.parse_agent_config(config)
    assert parsed["version"] == "2.0.0"
    assert parsed["model"] == "claude-sonnet-4"
    assert parsed["temperature"] == 0.5


@pytest.mark.asyncio
async def test_parse_agent_config_empty(agent_service):
    parsed = agent_service.parse_agent_config("")
    assert parsed == {}


@pytest.mark.asyncio
async def test_execute_agent_not_found(agent_service, mock_db):
    result_mock = MagicMock()
    result_mock.scalar_one_or_none = MagicMock(return_value=None)
    mock_db.execute = AsyncMock(return_value=result_mock)

    body = AgentExecutionRequest(input="test input")
    from fastapi import HTTPException
    with pytest.raises(HTTPException):
        await agent_service.execute_agent(str(uuid.uuid4()), body, str(uuid.uuid4()))


@pytest.mark.asyncio
async def test_list_versions(agent_service, mock_db):
    from backend.db.models import AgentVersion
    versions = [
        AgentVersion(id=uuid.uuid4(), agent_id=uuid.uuid4(), version_number="1.0.0"),
        AgentVersion(id=uuid.uuid4(), agent_id=uuid.uuid4(), version_number="1.1.0"),
    ]
    result_mock = MagicMock()
    result_mock.scalars.return_value.all = MagicMock(return_value=versions)
    mock_db.execute = AsyncMock(return_value=result_mock)

    result = await agent_service.list_versions(str(uuid.uuid4()))
    assert len(result) == 2
    assert result[0]["version_number"] == "1.0.0"
