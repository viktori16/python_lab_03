
import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session

from core.exceptions import DatabaseError
from core.models import Base


# Корневая папка проекта
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Папка для базы данных
DATA_DIR = PROJECT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Путь к SQLite
DATABASE_PATH = DATA_DIR / "travel.db"

# Настройка подключения
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DATABASE_PATH.as_posix()}"
)

# Параметры подключения
connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Создаём движок базы данных
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

# Создаём фабрику сессий
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)


def init_db():
    """Создание таблиц базы данных."""

    try:
        Base.metadata.create_all(bind=engine)
        print("База данных успешно подключена!")

    except SQLAlchemyError as error:
        raise DatabaseError(
            f"Не удалось подключиться к базе данных: {error}"
        ) from error


def get_session() -> Generator[Session, None, None]:
    """Получение сессии базы данных."""

    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
