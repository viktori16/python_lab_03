
from datetime import date

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QDateEdit,
    QDoubleSpinBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QMessageBox,
    QScrollArea,
)

from core.database import SessionLocal
from core.models import Travel
from core.services import TravelService
from core.exceptions import TravelPlannerError
from core.logger import logger

from desktop.charts import TravelChart


class MainWindow(QMainWindow):
    """Главное окно приложения Travel Planner."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Travel Planner — Планировщик путешествий")
        self.resize(900, 650)
        self.setMinimumSize(700, 450)

        self.create_menu()
        self.create_interface()
        self.refresh_data()

    def create_menu(self):
        """Создаёт меню приложения."""

        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("Файл")

        refresh_action = QAction("Обновить данные", self)
        refresh_action.triggered.connect(self.refresh_data)

        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)

        file_menu.addAction(refresh_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        help_menu = menu_bar.addMenu("Справка")

        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)

        help_menu.addAction(about_action)

    def create_interface(self):
        """Создаёт все элементы интерфейса."""

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной контейнер
        outer_layout = QVBoxLayout(central_widget)
        outer_layout.setContentsMargins(5, 5, 5, 5)

        # Область прокрутки
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        # Контейнер для содержимого
        content_widget = QWidget()
        main_layout = QVBoxLayout(content_widget)
        main_layout.setSpacing(10)

        scroll_area.setWidget(content_widget)
        outer_layout.addWidget(scroll_area)

        # Заголовок
        header_layout = QHBoxLayout()

        title = QLabel("✈ Travel Planner")
        title.setStyleSheet(
            "font-size: 26px; font-weight: bold; color: #2563eb;"
        )

        self.stats_label = QLabel("Путешествий: 0 | Бюджет: 0 €")
        self.stats_label.setStyleSheet(
            "font-size: 14px; font-weight: bold;"
        )

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.stats_label)

        main_layout.addLayout(header_layout)

        # Форма добавления путешествия
        form_group = QGroupBox("Новое путешествие")
        form_layout = QFormLayout(form_group)

        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Например, Париж")

        self.country_input = QLineEdit()
        self.country_input.setPlaceholderText("Например, Франция")

        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDisplayFormat("dd.MM.yyyy")
        self.start_date_input.setDate(QDate.currentDate())

        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDisplayFormat("dd.MM.yyyy")
        self.end_date_input.setDate(QDate.currentDate())

        self.budget_input = QDoubleSpinBox()
        self.budget_input.setRange(0.01, 100000000)
        self.budget_input.setDecimals(2)
        self.budget_input.setValue(1000)
        self.budget_input.setSuffix(" €")

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText(
            "Дополнительная информация"
        )

        form_layout.addRow("Город:", self.city_input)
        form_layout.addRow("Страна:", self.country_input)
        form_layout.addRow("Дата начала:", self.start_date_input)
        form_layout.addRow("Дата окончания:", self.end_date_input)
        form_layout.addRow("Бюджет:", self.budget_input)
        form_layout.addRow("Описание:", self.description_input)

        main_layout.addWidget(form_group)

        # Кнопки
        buttons_layout = QHBoxLayout()

        self.add_button = QPushButton("Добавить путешествие")
        self.add_button.clicked.connect(self.add_travel)

        self.delete_button = QPushButton("Удалить выбранное")
        self.delete_button.clicked.connect(self.delete_travel)

        self.clear_button = QPushButton("Очистить поля")
        self.clear_button.clicked.connect(self.clear_form)

        self.add_button.setStyleSheet(
            "background-color: #2563eb; color: white; "
            "padding: 8px; font-weight: bold;"
        )

        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.clear_button)

        main_layout.addLayout(buttons_layout)

        # Таблица путешествий
        table_title = QLabel("Мои путешествия")
        table_title.setStyleSheet(
            "font-size: 18px; font-weight: bold;"
        )

        main_layout.addWidget(table_title)

        self.table = QTableWidget()

        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Город",
            "Страна",
            "Начало",
            "Окончание",
            "Дней",
            "Бюджет",
            "Описание"
        ])

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setStretchLastSection(True)

        main_layout.addWidget(self.table)

        # График
        chart_title = QLabel("Статистика путешествий")
        chart_title.setStyleSheet(
            "font-size: 18px; font-weight: bold;"
        )

        main_layout.addWidget(chart_title)

        self.chart = TravelChart()
        self.chart.setMinimumHeight(250)

        main_layout.addWidget(self.chart)

        self.statusBar().showMessage("Приложение готово к работе")

    def add_travel(self):
        """Добавляет путешествие в базу данных."""

        try:
            travel = Travel(
                city=self.city_input.text(),
                country=self.country_input.text(),
                start_date=self.start_date_input.date().toPython(),
                end_date=self.end_date_input.date().toPython(),
                budget=self.budget_input.value(),
                description=self.description_input.text()
            )

            with SessionLocal() as session:
                service = TravelService(session)
                service.add_travel(travel)

            self.refresh_data()
            self.clear_form()

            self.statusBar().showMessage(
                "Путешествие успешно добавлено!", 5000
            )

        except TravelPlannerError as error:
            QMessageBox.warning(
                self,
                "Ошибка ввода",
                str(error)
            )

        except Exception as error:
            logger.exception("Ошибка добавления путешествия")

            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось добавить путешествие: {error}"
            )

    def delete_travel(self):
        """Удаляет выбранное путешествие."""

        selected_row = self.table.currentRow()

        if selected_row < 0:
            QMessageBox.warning(
                self,
                "Внимание",
                "Сначала выберите путешествие в таблице."
            )
            return

        travel_id = int(
            self.table.item(selected_row, 0).text()
        )

        answer = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы действительно хотите удалить путешествие?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            with SessionLocal() as session:
                service = TravelService(session)
                service.delete_travel(travel_id)

            self.refresh_data()

            self.statusBar().showMessage(
                "Путешествие удалено.", 5000
            )

        except TravelPlannerError as error:
            QMessageBox.warning(self, "Ошибка", str(error))

        except Exception as error:
            logger.exception("Ошибка удаления путешествия")
            QMessageBox.critical(self, "Ошибка", str(error))

    def refresh_data(self):
        """Обновляет таблицу, статистику и график."""

        try:
            with SessionLocal() as session:
                service = TravelService(session)
                travels = service.get_all_travels()

                # Сохраняем данные для отображения.
                rows = [
                    (
                        travel.id,
                        travel.city,
                        travel.country,
                        travel.start_date,
                        travel.end_date,
                        travel.duration(),
                        travel.budget,
                        travel.description
                    )
                    for travel in travels
                ]

            self.table.setRowCount(len(rows))

            for row_index, row_data in enumerate(rows):
                for column_index, value in enumerate(row_data):

                    if column_index == 6:
                        text = f"{value:.2f} €"

                    elif column_index in (3, 4):
                        text = value.strftime("%d.%m.%Y")

                    else:
                        text = str(value)

                    item = QTableWidgetItem(text)

                    if column_index == 0:
                        item.setTextAlignment(
                            Qt.AlignmentFlag.AlignCenter
                        )

                    self.table.setItem(
                        row_index,
                        column_index,
                        item
                    )

            total_budget = sum(row[6] for row in rows)

            self.stats_label.setText(
                f"Путешествий: {len(rows)} | "
                f"Общий бюджет: {total_budget:.2f} €"
            )

            self.chart.update_chart(travels)

        except Exception as error:
            logger.exception("Ошибка обновления интерфейса")

            QMessageBox.critical(
                self,
                "Ошибка загрузки данных",
                str(error)
            )

    def clear_form(self):
        """Очищает поля формы."""

        self.city_input.clear()
        self.country_input.clear()
        self.description_input.clear()

        self.start_date_input.setDate(QDate.currentDate())
        self.end_date_input.setDate(QDate.currentDate())

        self.budget_input.setValue(1000)

    def show_about(self):
        """Показывает информацию о приложении."""

        QMessageBox.about(
            self,
            "О программе",
            "Travel Planner\n\n"
            "Приложение для планирования путешествий.\n"
            "Лабораторная работа №3.\n"
            "Язык программирования: Python.\n"
            "Интерфейс: PySide6.\n"
            "База данных: SQLite3."
        )
