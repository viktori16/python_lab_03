import logging
from pathlib import Path


# Путь к папке логов
PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_DIR / "logs"

# Создаём папку, если её ещё нет
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Файл для хранения логов
LOG_FILE = LOG_DIR / "travel_planner.log"


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ],
    force=True
)

# Создаём объект логгера
logger = logging.getLogger("TravelPlanner")