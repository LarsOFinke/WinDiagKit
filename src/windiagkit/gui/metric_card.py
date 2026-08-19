"""Reusable live-metric display widget."""

from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout


class MetricCard(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("metricCard")
        layout = QVBoxLayout(self)
        title_label = QLabel(title)
        title_label.setObjectName("muted")
        self.value_label = QLabel("—")
        self.value_label.setObjectName("metricValue")
        layout.addWidget(title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value):
        self.value_label.setText(value)
