
import pytest

from datetime import date

from core.models import Travel
from core.exceptions import InvalidTravelDataError


def test_create_travel():
    """Проверка создания путешествия."""

    travel = Travel(
        city="Paris",
        country="France",
        start_date=date(2027, 6, 10),
        end_date=date(2027, 6, 15),
        budget=1000
    )

    assert travel.city == "Paris"
    assert travel.country == "France"
    assert travel.budget == 1000


def test_travel_duration():
    """Проверка продолжительности путешествия."""

    travel = Travel(
        city="Rome",
        country="Italy",
        start_date=date(2027, 7, 1),
        end_date=date(2027, 7, 5),
        budget=800
    )

    assert travel.duration() == 5


def test_empty_city():
    """Проверка ошибки при пустом городе."""

    with pytest.raises(InvalidTravelDataError):
        Travel(
            city="",
            country="France",
            start_date=date(2027, 6, 10),
            end_date=date(2027, 6, 15),
            budget=1000
        )


def test_invalid_dates():
    """Проверка неправильных дат."""

    with pytest.raises(InvalidTravelDataError):
        Travel(
            city="Paris",
            country="France",
            start_date=date(2027, 6, 15),
            end_date=date(2027, 6, 10),
            budget=1000
        )


def test_invalid_budget():
    """Проверка отрицательного бюджета."""

    with pytest.raises(InvalidTravelDataError):
        Travel(
            city="Paris",
            country="France",
            start_date=date(2027, 6, 10),
            end_date=date(2027, 6, 15),
            budget=-100
        )


def test_non_numeric_budget():
    """Проверка бюджета, который не является числом."""

    with pytest.raises(InvalidTravelDataError):
        Travel(
            city="Paris",
            country="France",
            start_date=date(2027, 6, 10),
            end_date=date(2027, 6, 15),
            budget="abc"
        )
