# Production backend image (docs/deployment/DEPLOYMENT_SPEC.md: "Docker-compatible
# Python host/VPS"). Build from the REPO ROOT so this Dockerfile can reach the
# shared root requirements.txt and the sibling ml/ and data/ directories that
# app/services/intent/service.py and app/services/ingestion/config.py load at
# runtime (see backend/app/services/intent/service.py's REPO_ROOT sys.path insert):
#
#   docker build -f backend/Dockerfile -t ai-customer-support-backend .
#
# Local development does NOT use this image (docs/TECH_STACK.md scopes
# docker-compose.yml to PostgreSQL/pgvector only); this image is for the
# production/VPS path and for docker-compose.prod.yml.

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Backend application code (routes, schemas, services, providers, alembic).
COPY backend/ ./backend/

# Sibling packages the backend imports at runtime, per app/services/intent/service.py
# and app/services/ingestion/config.py -- not the full ml/ tree (training code,
# datasets, and test suites are not needed to serve requests).
COPY ml/data/__init__.py ./ml/data/__init__.py
COPY ml/data/config.py ./ml/data/config.py
COPY ml/distilbert/ ./ml/distilbert/

# Seed knowledge base content (docs/rag/KNOWLEDGE_BASE_SPEC.md). Uploaded
# documents are written under this same path at runtime; mount a volume over
# it in production so uploads survive container restarts/redeploys (see
# docker-compose.prod.yml's knowledge_base_data volume).
COPY data/knowledge_base/ ./data/knowledge_base/

RUN chmod +x ./backend/docker-entrypoint.sh

EXPOSE 8000

# docs/deployment/DEPLOYMENT_SPEC.md: "Expose /health" -- actual route is
# /api/v1/health per docs/api/API_SPEC.md's `/api/v1` base path.
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD python -c "import os,urllib.request as u; u.urlopen('http://127.0.0.1:' + os.environ.get('PORT','8000') + '/api/v1/health', timeout=3)"

ENTRYPOINT ["./backend/docker-entrypoint.sh"]
