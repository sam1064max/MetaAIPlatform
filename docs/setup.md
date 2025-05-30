# Setup Guide

## Prerequisites
- Docker and Docker Compose
- Python 3.12+
- Git

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/sushantdev/MetaAIPlatform.git
cd MetaAIPlatform
```

### 2. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Start Platform
```bash
docker compose up -d
```

### 4. Access Platform
- Frontend: http://localhost:8501
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Development

### Local Setup
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\Activate
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### Run Backend
```bash
uvicorn backend.main:app --reload --port 8000
```

### Run Frontend
```bash
streamlit run frontend/app.py --server.port=8501
```

### Run Tests
```bash
pytest backend/tests/ -v
```

## Deployment

See deployment/scripts/deploy.sh for production deployment.
