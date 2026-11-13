
import pytest

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from core.models import Base


@pytest.fixture
def db_session(tmp_path):
    """Создаёт временную базу данных для тестирования."""

    database_file = tmp_path / "test_travel.db"

    database_url = URL.create(
        "sqlite",
        database=str(database_file)
    )

    engine = create_engine(database_url)

    Base.metadata.create_all(bind=engine)

    TestingSession = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False
    )

    with TestingSession() as session:
        yield session

    Base.metadata.drop_all(bind=engine)
    engine.dispose()
