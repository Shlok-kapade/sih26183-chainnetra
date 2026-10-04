import os

base_dir = "/home/finex/Desktop/projects/uncompleted/chainnetra-sih26138"
os.chdir(base_dir)

os.makedirs("backend/app/core", exist_ok=True)
os.makedirs("backend/app/db", exist_ok=True)
os.makedirs("backend/app/api", exist_ok=True)
os.makedirs("backend/tests", exist_ok=True)
os.makedirs("backend/alembic/versions", exist_ok=True)
os.makedirs("config", exist_ok=True)

# Write files
def write_file(path, content):
    with open(path, "w") as f:
        f.write(content)

write_file("backend/pyproject.toml", """\
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "chainnetra-backend"
version = "0.1.0"
description = "ChainNetra Backend"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.103.0",
    "uvicorn>=0.23.2",
    "SQLAlchemy[asyncio]>=2.0.20",
    "asyncpg>=0.28.0",
    "alembic>=1.11.3",
    "pydantic>=2.3.0",
    "pydantic-settings>=2.0.3",
    "httpx>=0.24.1",
    "tenacity>=8.2.3",
    "python-jose[cryptography]>=3.3.0",
    "passlib[argon2]>=1.7.4",
    "networkx>=3.1",
    "shap>=0.42.1",
    "lightgbm>=4.0.0",
    "joblib>=1.3.2",
    "reportlab>=4.0.4"
]

[project.optional-dependencies]
dev = [
    "ruff>=0.0.285",
    "mypy>=1.5.1",
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.1",
    "hypothesis>=6.82.0",
    "aiosqlite>=0.19.0",
    "httpx>=0.24.1"
]

[tool.ruff]
select = ["E", "F", "I", "N", "W"]
target-version = "py312"
line-length = 88

[tool.mypy]
strict = true
plugins = ["pydantic.mypy"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
""")

write_file("backend/app/__init__.py", "")

write_file("backend/app/core/__init__.py", "")
write_file("backend/app/core/config.py", """\
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"
    SECRET_KEY: str = "changeme"
    LIVE_MODE: bool = False
    TRONGRID_API_KEY: str = ""
    ETHERSCAN_API_KEY: str = ""
    VERSION: str = "0.1.0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
""")

write_file("backend/app/core/logging.py", """\
import logging

def setup_logging() -> None:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("chainnetra")
    logger.setLevel(logging.INFO)
""")

write_file("backend/app/core/errors.py", """\
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class APIError(Exception):
    def __init__(self, type_: str, title: str, status: int, detail: str):
        self.type = type_
        self.title = title
        self.status = status
        self.detail = detail

def setup_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status,
            content={
                "type": exc.type,
                "title": exc.title,
                "status": exc.status,
                "detail": exc.detail
            },
            headers={"Content-Type": "application/problem+json"}
        )
""")

write_file("backend/app/db/__init__.py", "")

write_file("backend/app/db/session.py", """\
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings
from typing import AsyncGenerator

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
""")

write_file("backend/app/db/base.py", """\
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
""")

write_file("backend/app/db/models.py", """\
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class Complaint(Base):
    __tablename__ = "complaints"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    details: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class Case(Base):
    __tablename__ = "cases"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.id"))
    status: Mapped[str] = mapped_column(String, default="open")

class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    status: Mapped[str] = mapped_column(String, default="pending")

class RawResponse(Base):
    __tablename__ = "raw_responses"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    data: Mapped[Dict[str, Any]] = mapped_column(JSON)

class Transfer(Base):
    __tablename__ = "transfers"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tx_hash: Mapped[str] = mapped_column(String, unique=True, index=True)
    amount: Mapped[float] = mapped_column(Float)

class Address(Base):
    __tablename__ = "addresses"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    address: Mapped[str] = mapped_column(String, unique=True, index=True)

class Edge(Base):
    __tablename__ = "edges"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    from_address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"))
    to_address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"))

class Label(Base):
    __tablename__ = "labels"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"))
    label: Mapped[str] = mapped_column(String)

class Attribution(Base):
    __tablename__ = "attributions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"))

class Pattern(Base):
    __tablename__ = "patterns"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    description: Mapped[str] = mapped_column(String)

class Exit(Base):
    __tablename__ = "exits"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tx_hash: Mapped[str] = mapped_column(String)

class Risk(Base):
    __tablename__ = "risks"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"))
    score: Mapped[float] = mapped_column(Float)

class Triage(Base):
    __tablename__ = "triages"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    priority: Mapped[int] = mapped_column(Integer)

class Report(Base):
    __tablename__ = "reports"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    content: Mapped[str] = mapped_column(String)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    action: Mapped[str] = mapped_column(String)

class ModelRegistry(Base):
    __tablename__ = "model_registry"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    model_name: Mapped[str] = mapped_column(String)
""")

write_file("backend/app/api/__init__.py", "")

write_file("backend/app/api/health.py", """\
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.config import settings

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    mode: str
    version: str

@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    mode = "live" if settings.LIVE_MODE else "fixture"
    return HealthResponse(status="ok", mode=mode, version=settings.VERSION)

@router.get("/version", response_model=HealthResponse)
async def version() -> HealthResponse:
    mode = "live" if settings.LIVE_MODE else "fixture"
    return HealthResponse(status="ok", mode=mode, version=settings.VERSION)
""")

write_file("backend/app/main.py", """\
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import AsyncGenerator, Any

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.errors import setup_error_handlers
from app.api.health import router as health_router

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    # Startup
    yield
    # Shutdown

app = FastAPI(title="ChainNetra API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_error_handlers(app)
app.include_router(health_router, tags=["health"])
""")

write_file("backend/tests/__init__.py", "")

write_file("backend/tests/conftest.py", """\
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db.session import engine, Base

@pytest.fixture(autouse=True)
async def setup_db() -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
""")

write_file("backend/tests/test_health.py", """\
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health(async_client: AsyncClient) -> None:
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["mode"] in ["live", "fixture"]
    assert "version" in data
""")

write_file("backend/alembic.ini", """\
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
""")

write_file("backend/alembic/env.py", """\
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from app.db.base import Base
from app.core.config import settings

# Import models to register with Base
import app.db.models

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.DATABASE_URL
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
""")

write_file("docker-compose.yml", """\
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: chainnetra
      POSTGRES_PASSWORD: password
      POSTGRES_DB: chainnetra
    ports:
      - "5432:5432"

  api:
    build:
      context: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db

  worker:
    build:
      context: ./backend
    command: python -m app.worker.main
    env_file:
      - .env
    depends_on:
      - db
      - api

  web:
    image: nginx:alpine
    ports:
      - "80:80"
""")

write_file("backend/Dockerfile", """\
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"

COPY . .
""")

write_file(".env.example", """\
DATABASE_URL=postgresql+asyncpg://chainnetra:password@db:5432/chainnetra
SECRET_KEY=changeme
LIVE_MODE=False
TRONGRID_API_KEY=
ETHERSCAN_API_KEY=
""")

write_file(".gitignore", """\
.venv/
__pycache__/
*.pyc
.env
.pytest_cache/
.ruff_cache/
.mypy_cache/
""")

write_file("config/trace.yaml", "default_depth: 3\\n")
write_file("config/risk_weights.yaml", "mixer: 0.8\\n")
write_file("config/providers.yaml", "etherscan: true\\n")

write_file("Makefile", """\
.PHONY: dev test lint fixtures train-m1 train-m3 eval demo report migrate

VENV = backend/.venv/bin

dev:
\t$(VENV)/uvicorn app.main:app --reload

test:
\tcd backend && .venv/bin/pytest

lint:
\tcd backend && .venv/bin/ruff check app tests
\tcd backend && .venv/bin/mypy app

fixtures:
\techo "Generating fixtures..."

train-m1:
\techo "Training M1..."

train-m3:
\techo "Training M3..."

eval:
\techo "Evaluating..."

demo:
\techo "Running demo..."

report:
\techo "Generating report..."

migrate:
\tcd backend && .venv/bin/alembic upgrade head
""")

print("Setup completed successfully.")
