
FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем зависимости веб-приложения
COPY requirements-web.txt .

RUN pip install --no-cache-dir -r requirements-web.txt

# Копируем программный код
COPY core ./core
COPY web ./web

# Создаём папки для базы данных и логов
RUN mkdir -p /app/data /app/logs

# Путь к SQLite внутри контейнера
ENV DATABASE_URL=sqlite:////app/data/travel.db

EXPOSE 8000

# Запускаем веб-сервер
CMD ["uvicorn", "web.main:app", "--host", "0.0.0.0", "--port", "8000"]
