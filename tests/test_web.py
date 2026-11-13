
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from core.models import Base
import web.main
import web.routes


@pytest.fixture
def web_client(tmp_path, monkeypatch):
    """Создаёт тестовый клиент с отдельной SQLite-базой."""

    database_file = tmp_path / "test_web.db"

    database_url = URL.create(
        "sqlite",
        database=str(database_file)
    )

    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False}
    )

    Base.metadata.create_all(bind=engine)

    TestingSession = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False
    )

    # Подменяем подключение к основной базе
    # на временную тестовую базу.
    monkeypatch.setattr(
        web.routes,
        "SessionLocal",
        TestingSession
    )

    # Не запускаем инициализацию основной базы.
    monkeypatch.setattr(
        web.main,
        "init_db",
        lambda: None
    )

    try:
        with TestClient(web.main.app) as client:
            yield client

    finally:
        engine.dispose()


def test_home_page(web_client):
    """Проверка открытия главной страницы."""

    response = web_client.get("/")

    assert response.status_code == 200
    assert "Мои путешествия" in response.text


def test_add_travel_web(web_client):
    """Проверка добавления путешествия через веб."""

    response = web_client.post(
        "/travels",
        data={
            "city": "Rome",
            "country": "Italy",
            "start_date": "2027-07-01",
            "end_date": "2027-07-05",
            "budget": "800",
            "description": "Летний отпуск"
        },
        follow_redirects=False
    )

    assert response.status_code == 303

    page = web_client.get("/")

    assert "Rome" in page.text
    assert "Italy" in page.text


def test_delete_travel_web(web_client):
    """Проверка удаления путешествия через веб."""

    web_client.post(
        "/travels",
        data={
            "city": "Paris",
            "country": "France",
            "start_date": "2027-06-10",
            "end_date": "2027-06-15",
            "budget": "1000",
            "description": ""
        },
        follow_redirects=False
    )

    response = web_client.post(
        "/travels/1/delete",
        follow_redirects=False
    )

    assert response.status_code == 303

    page = web_client.get("/")

    assert "Paris" not in page.text


def test_invalid_travel_web(web_client):
    """Проверка обработки неправильных дат."""

    response = web_client.post(
        "/travels",
        data={
            "city": "Paris",
            "country": "France",
            "start_date": "2027-06-15",
            "end_date": "2027-06-10",
            "budget": "1000",
            "description": ""
        }
    )

    assert response.status_code == 200
    assert "Дата окончания не может быть раньше даты начала." in response.text
