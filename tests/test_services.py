
import pytest

from datetime import date

from core.models import Travel
from core.services import TravelService
from core.exceptions import TravelNotFoundError


def create_test_travel():
    """Создаёт тестовое путешествие."""

    return Travel(
        city="Paris",
        country="France",
        start_date=date(2027, 6, 10),
        end_date=date(2027, 6, 15),
        budget=1000
    )


def test_add_travel(db_session):
    """Проверка добавления путешествия."""

    service = TravelService(db_session)

    travel = create_test_travel()
    service.add_travel(travel)

    assert travel.id is not None

    travels = service.get_all_travels()

    assert len(travels) == 1
    assert travels[0].city == "Paris"


def test_get_all_travels(db_session):
    """Проверка получения списка путешествий."""

    service = TravelService(db_session)

    service.add_travel(create_test_travel())

    second_travel = Travel(
        city="Rome",
        country="Italy",
        start_date=date(2027, 7, 1),
        end_date=date(2027, 7, 5),
        budget=800
    )

    service.add_travel(second_travel)

    travels = service.get_all_travels()

    assert len(travels) == 2


def test_delete_travel(db_session):
    """Проверка удаления путешествия."""

    service = TravelService(db_session)

    travel = create_test_travel()
    service.add_travel(travel)

    travel_id = travel.id

    service.delete_travel(travel_id)

    assert len(service.get_all_travels()) == 0


def test_get_travel_by_id(db_session):
    """Проверка поиска путешествия по ID."""

    service = TravelService(db_session)

    travel = create_test_travel()
    service.add_travel(travel)

    result = service.get_travel_by_id(travel.id)

    assert result.city == "Paris"


def test_travel_not_found(db_session):
    """Проверка обработки отсутствующего путешествия."""

    service = TravelService(db_session)

    with pytest.raises(TravelNotFoundError):
        service.get_travel_by_id(999)
