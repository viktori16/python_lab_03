
from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.database import init_db
from core.logger import logger
from web.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Действия при запуске и остановке приложения."""

    init_db()
    logger.info("Веб-приложение Travel Planner запущено.")

    yield

    logger.info("Веб-приложение Travel Planner остановлено.")


app = FastAPI(
    title="Travel Planner",
    description="Веб-приложение для планирования путешествий",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)
