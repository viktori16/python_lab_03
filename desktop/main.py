
import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from core.database import init_db
from core.exceptions import DatabaseError
from core.logger import logger

from desktop.window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Travel Planner")

    try:
        init_db()

        window = MainWindow()
        window.show()

        logger.info("Приложение Travel Planner запущено.")

        return app.exec()

    except DatabaseError as error:
        logger.exception("Ошибка запуска приложения")

        QMessageBox.critical(
            None,
            "Ошибка базы данных",
            str(error)
        )

        return 1


if __name__ == "__main__":
    sys.exit(main())
