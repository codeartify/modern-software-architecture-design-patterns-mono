import os
from collections.abc import Generator
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

try:
    from sqlalchemy.orm import DeclarativeBase

    class Base(DeclarativeBase):
        pass
except ImportError:
    from sqlalchemy.orm import declarative_base

    Base: Any = declarative_base()


ROOT_DIR = Path(__file__).resolve().parents[6]
DATABASE_DIR = ROOT_DIR / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_DATABASE_URL = f"sqlite:///{DATABASE_DIR / 'workshop-python.db'}"
DATABASE_URL = os.getenv("WORKSHOP_PYTHON_DATABASE_URL", DEFAULT_DATABASE_URL)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db_session() -> Generator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    from workshop_api.fitness.shared.customer.models import SharedCustomerOrmModel
    from workshop_api.fitness.shared.plan.models import SharedPlanOrmModel

    Base.metadata.create_all(
        bind=engine,
        tables=[
            SharedCustomerOrmModel.__table__,
            SharedPlanOrmModel.__table__,
        ],
    )
