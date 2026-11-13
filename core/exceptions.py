class TravelPlannerError(Exception):
    """Базовое исключение приложения."""
    pass


class InvalidTravelDataError(TravelPlannerError):
    """Ошибка при вводе данных путешествия."""
    pass


class TravelNotFoundError(TravelPlannerError):
    """Путешествие не найдено."""
    pass


class DatabaseError(TravelPlannerError):
    """Ошибка работы с базой данных."""
    pass