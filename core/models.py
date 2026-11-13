
from datetime import date
from math import isfinite

from sqlalchemy import (
    CheckConstraint,
    Date,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.exceptions import InvalidTravelDataError


class Base(DeclarativeBase):
    """Базовый класс моделей базы данных."""
    pass


class Travel(Base):
    """Модель путешествия."""

    __tablename__ = "travels"

    __table_args__ = (
        CheckConstraint("budget > 0", name="check_positive_budget"),
        CheckConstraint(
            "end_date >= start_date",
            name="check_dates"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    end_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    budget: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False
    )

    def __init__(
        self,
        city: str,
        country: str,
        start_date: date,
        end_date: date,
        budget: float,
        description: str = ""
    ):
        city = city.strip() if isinstance(city, str) else ""
        country = country.strip() if isinstance(country, str) else ""

        if not city or not country:
            raise InvalidTravelDataError(
                "Город и страна обязательны."
            )

        if not isinstance(start_date, date) or not isinstance(end_date, date):
            raise InvalidTravelDataError("Укажите корректные даты.")

        if start_date > end_date:
            raise InvalidTravelDataError(
                "Дата окончания не может быть раньше даты начала."
            )

        try:
            budget = float(budget)
        except (TypeError, ValueError):
            raise InvalidTravelDataError("Бюджет должен быть числом.")

        if not isfinite(budget) or budget <= 0:
            raise InvalidTravelDataError(
                "Бюджет должен быть больше нуля."
            )

        self.city = city
        self.country = country
        self.start_date = start_date
        self.end_date = end_date
        self.budget = budget
        self.description = str(description or "").strip()

    def duration(self) -> int:
        """Продолжительность путешествия в днях."""
        return (self.end_date - self.start_date).days + 1

    def __repr__(self):
        return (
            f"Travel(city='{self.city}', "
            f"country='{self.country}', "
            f"budget={self.budget})"
        )
