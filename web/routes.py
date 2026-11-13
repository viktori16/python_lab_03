
from collections import Counter
from pathlib import Path

from datetime import date

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from core.database import SessionLocal
from core.models import Travel
from core.services import TravelService
from core.exceptions import TravelPlannerError
from core.logger import logger


BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(
    directory=str(BASE_DIR / "web" / "templates")
)

router = APIRouter()


def render_index(
    request: Request,
    error: str | None = None
):
    """Формирует главную страницу со списком путешествий."""

    with SessionLocal() as session:
        service = TravelService(session)
        travels = service.get_all_travels()

        # Общая статистика
        total_budget = sum(travel.budget for travel in travels)

        # Данные для графика
        months = Counter(
            travel.start_date.strftime("%m.%Y")
            for travel in travels
        )

        chart_data = [
            {"month": month, "count": count}
            for month, count in sorted(months.items())
        ]

    max_count = max(
        (item["count"] for item in chart_data),
        default=1
    )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "travels": travels,
            "total_budget": total_budget,
            "total_count": len(travels),
            "chart_data": chart_data,
            "max_count": max_count,
            "error": error
        }
    )


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    """Главная страница."""

    return render_index(request)


@router.post("/travels")
def add_travel(
    request: Request,
    city: str = Form(...),
    country: str = Form(...),
    start_date: date = Form(...),
    end_date: date = Form(...),
    budget: float = Form(...),
    description: str = Form("")
):
    """Добавление нового путешествия."""

    try:
        travel = Travel(
            city=city,
            country=country,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            description=description
        )

        with SessionLocal() as session:
            service = TravelService(session)
            service.add_travel(travel)

        logger.info(
            "Веб-версия: добавлено путешествие %s, %s",
            city,
            country
        )

        return RedirectResponse(
            url="/",
            status_code=303
        )

    except TravelPlannerError as error:
        return render_index(request, str(error))

    except Exception:
        logger.exception("Ошибка добавления путешествия через веб")
        return render_index(
            request,
            "Произошла ошибка при добавлении путешествия."
        )


@router.post("/travels/{travel_id}/delete")
def delete_travel(travel_id: int):
    """Удаление путешествия."""

    try:
        with SessionLocal() as session:
            service = TravelService(session)
            service.delete_travel(travel_id)

        logger.info(
            "Веб-версия: удалено путешествие ID=%s",
            travel_id
        )

    except TravelPlannerError:
        logger.exception(
            "Не удалось удалить путешествие ID=%s",
            travel_id
        )

    return RedirectResponse(
        url="/",
        status_code=303
    )
