# Changelog

All notable changes to MetaAI Platform are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Fixed
- Frontend API paths corrected across all 9 pages to match backend endpoints (dashboard, evaluations, governance, RAG, tools, observability, agent studio)
- Dashboard stats, cost trends, token usage, and model usage now query PostgreSQL via SQLAlchemy instead of returning hardcoded values

### Added
- Database auto-initialization on startup (tables created via `Base.metadata.create_all`)
- Alembic migration scaffolding (env.py, script.py.mako, alembic.ini)
- `backend/seed.py` — seed script with admin user, 3 agents (Wealth Advisor, Research, Compliance), 5 tools (market_data, portfolio_analysis, crm, research, news), 1 sample knowledge base

## [1.0.0] - 2025-06-20

### Added
- Initial platform scaffold with FastAPI backend and Streamlit frontend
- LangGraph agent runtime with planner-executor-reviewer state graph
- LiteLLM model gateway with complexity-based routing
- Qdrant RAG pipeline (chunking, embeddings, hybrid retrieval, reranking)
- Redis for agent memory and caching
- JWT authentication with RBAC
- Docker Compose with 5 services (backend, frontend, postgres, redis, qdrant)
- CI/CD pipeline with GitHub Actions

[Unreleased]: https://github.com/sam1064max/MetaAIPlatform/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/sam1064max/MetaAIPlatform/releases/tag/v1.0.0
