import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import pytest  # noqa: E402
import sqlalchemy as sa  # noqa: E402
from alembic.config import Config  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from alembic import command  # noqa: E402
from app.core.config import get_settings  # noqa: E402

settings = get_settings()


def _alembic_config(url: str) -> Config:
    os.environ["ALEMBIC_DATABASE_URL"] = url
    cfg = Config(str(BACKEND_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_ROOT / "alembic"))
    return cfg


@pytest.fixture(scope="session")
def test_db_url() -> str:
    return settings.TEST_DATABASE_URL


@pytest.fixture(scope="session")
def test_engine(test_db_url):
    url = sa.engine.url.make_url(test_db_url)
    maintenance_url = url.set(database="postgres")
    maintenance_engine = sa.create_engine(maintenance_url, isolation_level="AUTOCOMMIT")
    try:
        with maintenance_engine.connect() as conn:
            exists = conn.execute(
                sa.text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": url.database},
            ).scalar()
            if not exists:
                conn.execute(sa.text(f'CREATE DATABASE "{url.database}"'))
    except sa.exc.OperationalError as exc:
        pytest.skip(f"PostgreSQL is not reachable for database tests: {exc}")
    finally:
        maintenance_engine.dispose()

    alembic_cfg = _alembic_config(test_db_url)
    command.upgrade(alembic_cfg, "head")

    engine = sa.create_engine(test_db_url, future=True)
    yield engine
    engine.dispose()

    command.downgrade(alembic_cfg, "base")


@pytest.fixture()
def db_session(test_engine) -> Session:
    connection = test_engine.connect()
    transaction = connection.begin()
    # create_savepoint: an inner rollback (e.g. from a caught IntegrityError)
    # reopens a SAVEPOINT instead of deassociating from `connection`, so the
    # outer `transaction` stays valid for the final rollback below.
    session = Session(bind=connection, future=True, join_transaction_mode="create_savepoint")

    yield session

    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()
