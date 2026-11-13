
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from core.models import Travel
from core.exceptions import DatabaseError, TravelNotFoundError
from core.logger import logger


class TravelService:
    """Сервис управления путешествиями."""

    def __init__(self, session: Session):
        self.session = session

    def add_travel(self, travel: Travel) -> Travel:
        """Добавляет новое путешествие."""

        try:
            self.session.add(travel)
            self.session.commit()
            self.session.refresh(travel)

            logger.info(
                "Добавлено путешествие: %s, %s",
                travel.city,
                travel.country
            )

            return travel

        except SQLAlchemyError as error:
            self.session.rollback()
            logger.exception("Ошибка добавления путешествия")

            raise DatabaseError(
                "Не удалось добавить путешествие."
            ) from error

    def get_all_travels(self) -> list[Travel]:
        """Возвращает все путешествия."""

        try:
            query = select(Travel).order_by(Travel.start_date)
            return list(self.session.scalars(query).all())

        except SQLAlchemyError as error:
            raise DatabaseError(
                "Не удалось получить список путешествий."
            ) from error

    def get_travel_by_id(self, travel_id: int) -> Travel:
        """Находит путешествие по идентификатору."""

        travel = self.session.get(Travel, travel_id)

        if travel is None:
            raise TravelNotFoundError(
                f"Путешествие с ID {travel_id} не найдено."
            )

        return travel

    def delete_travel(self, travel_id: int) -> None:
        """Удаляет путешествие."""

        try:
            travel = self.get_travel_by_id(travel_id)

            self.session.delete(travel)
            self.session.commit()

            logger.info(
                "Удалено путешествие: %s, %s",
                travel.city,
                travel.country
            )

        except SQLAlchemyError as error:
            self.session.rollback()
            logger.exception("Ошибка удаления путешествия")

            raise DatabaseError(
                "Не удалось удалить путешествие."
            ) from error
