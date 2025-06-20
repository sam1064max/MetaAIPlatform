# Changelog

All notable changes to MetaAI Platform are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Agent Studio with live YAML editing and validation
- Agent Marketplace for publishing and discovering agents
- Tool Registry with MCP-compatible tool definitions
- RAG Studio with Qdrant vector store and hybrid search
- Evaluation Center with DeepEval metrics integration
- Observability dashboard with OpenTelemetry tracing
- Governance engine with RBAC and audit logging
- Nginx reverse proxy with HTTPS, gzip, and security headers
- Subdomain-based routing (metaai.sushantdev.com, metaai-api.sushantdev.com, metaai-observability.sushantdev.com)
- CI/CD pipeline with Ruff, Black, MyPy, Pytest, Bandit, Docker build validation
- Staging environment (staging-metaai.sushantdev.com, staging-metaai-api.sushantdev.com)
- Automated release workflow with changelog generation
- GitHub Project board with Backlog, Ready, In Progress, Code Review, QA, UAT, Done columns

### Improved
- Switched from Traefik to Nginx for reverse proxy
- Per-service Docker images in GHCR (metaai-backend, metaai-frontend, metaai-nginx)
- Image-based deployment (no git pull on VPS)
- Production uvicorn with 4 workers (no reload)
- Cloudflare DNS configuration with Full (Strict) SSL

### Fixed
- Streamlit subpath configuration for subdomain-based routing
- Removed ssh-keyscan from deploy step (uses webfactory/ssh-agent only)
- Production readiness checklist gating before deployment

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
