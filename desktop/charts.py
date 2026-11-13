
from collections import Counter

from PySide6.QtWidgets import QWidget, QVBoxLayout

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class TravelChart(QWidget):
    """График активности путешествий."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.figure = Figure(figsize=(7, 3))
        self.canvas = FigureCanvasQTAgg(self.figure)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        self.update_chart([])

    def update_chart(self, travels):
        """Обновляет график на основе списка путешествий."""

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if not travels:
            ax.text(
                0.5, 0.5,
                "Пока нет путешествий",
                ha="center",
                va="center",
                fontsize=14
            )
            ax.axis("off")

        else:
            months = Counter(
                travel.start_date.strftime("%m.%Y")
                for travel in travels
            )

            labels = sorted(
                months,
                key=lambda x: (
                    int(x.split(".")[1]),
                    int(x.split(".")[0])
                )
            )

            values = [months[month] for month in labels]

            ax.bar(labels, values)

            ax.set_title("Активность путешествий по месяцам")
            ax.set_xlabel("Месяц начала путешествия")
            ax.set_ylabel("Количество путешествий")

            ax.grid(axis="y", alpha=0.3)
            ax.set_axisbelow(True)

        self.figure.tight_layout()
        self.canvas.draw_idle()
