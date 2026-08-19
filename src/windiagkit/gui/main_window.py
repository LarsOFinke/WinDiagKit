from os import name as os_name
from time import monotonic, strftime

from psutil import Error as PsutilError
from psutil import cpu_percent, net_io_counters, virtual_memory
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .. import __version__
from ..cli.console import APP_NAME
from ..diagnostics.job_catalog import JobCatalog
from ..diagnostics.monitor import human_bytes
from .job_runner import JobRunner
from .log_highlighter import LogHighlighter
from .metric_card import MetricCard

STYLE = """
QMainWindow, QWidget { background: #111827; color: #e5e7eb; }
QFrame#metricCard, QFrame#panel { background: #1f2937; border: 1px solid #374151; border-radius: 8px; }
QFrame#metricCard QLabel, QFrame#panel QLabel { background: transparent; }
QLabel#appTitle { font-size: 24px; font-weight: 700; color: #f9fafb; }
QLabel#sectionTitle { font-size: 18px; font-weight: 600; color: #f9fafb; }
QLabel#metricValue { font-size: 22px; font-weight: 700; color: #60a5fa; }
QLabel#muted { color: #9ca3af; }
QTreeWidget, QPlainTextEdit, QLineEdit, QComboBox {
    background: #0f172a; color: #e5e7eb; border: 1px solid #374151; border-radius: 5px; padding: 6px;
}
QLineEdit:disabled, QComboBox:disabled { color: #6b7280; }
QTreeWidget::item { padding: 6px; }
QTreeWidget::item:selected { background: #1d4ed8; color: white; }
QPushButton { background: #374151; border: 1px solid #4b5563; border-radius: 5px; padding: 8px 14px; }
QPushButton:hover { background: #4b5563; }
QPushButton:disabled { color: #6b7280; background: #1f2937; }
QPushButton#primary { background: #2563eb; border-color: #3b82f6; font-weight: 600; }
QPushButton#primary:hover { background: #1d4ed8; }
QPushButton#danger { background: #991b1b; border-color: #b91c1c; }
QPushButton#danger:disabled { background: #1f2937; border-color: #374151; }
QProgressBar { border: 1px solid #374151; border-radius: 3px; text-align: center; }
QProgressBar::chunk { background: #2563eb; }
"""


class MainWindow(QMainWindow):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.job_catalog = JobCatalog()
        self.runner = JobRunner(self)
        self._job_items = {}
        self._previous_net = net_io_counters()
        self._previous_time = monotonic()

        self.setWindowTitle(f"{APP_NAME} {__version__}")
        self.setMinimumSize(1050, 700)
        self.resize(1280, 820)
        self.setStyleSheet(STYLE)
        self._build_ui()
        self._connect_signals()
        self._populate_jobs()
        self._select_job("checkpoint")
        self._start_metrics()
        if os_name != "nt":
            self.status_label.setText(
                "Development mode: diagnostic jobs target Windows"
            )

    def _build_ui(self):
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(12)

        title = QLabel(APP_NAME)
        title.setObjectName("appTitle")
        subtitle = QLabel(
            "Read-only Windows diagnostics · results remain in memory unless you copy them"
        )
        subtitle.setObjectName("muted")
        root.addWidget(title)
        root.addWidget(subtitle)

        metrics = QHBoxLayout()
        self.cpu_card = MetricCard("CPU")
        self.memory_card = MetricCard("Memory")
        self.rx_card = MetricCard("Network receive")
        self.tx_card = MetricCard("Network send")
        for card in (self.cpu_card, self.memory_card, self.rx_card, self.tx_card):
            metrics.addWidget(card)
        root.addLayout(metrics)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._build_job_panel())
        splitter.addWidget(self._build_output_panel())
        splitter.setSizes((390, 790))
        root.addWidget(splitter, 1)

        self.setCentralWidget(central)

    def _build_job_panel(self):
        panel = QFrame()
        panel.setObjectName("panel")
        layout = QVBoxLayout(panel)
        heading = QLabel("Diagnostic jobs")
        heading.setObjectName("sectionTitle")
        layout.addWidget(heading)

        self.job_tree = QTreeWidget()
        self.job_tree.setHeaderHidden(True)
        self.job_tree.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.job_tree, 1)

        form = QFormLayout()
        self.target_input = QLineEdit(self.settings.default_target)
        self.target_input.setPlaceholderText("Host name or IP address")
        self.window_combo = QComboBox()
        for value in self.settings.event_window_choices:
            self.window_combo.addItem(f"Last {value} minutes", value)
        default_index = self.window_combo.findData(self.settings.event_window_minutes)
        self.window_combo.setCurrentIndex(max(0, default_index))
        form.addRow("Network target", self.target_input)
        form.addRow("Event window", self.window_combo)
        layout.addLayout(form)

        targets = ", ".join(self.settings.diagnostic_process_names) or "Not configured"
        self.targets_label = QLabel(f"Process targets: {targets}")
        self.targets_label.setObjectName("muted")
        self.targets_label.setWordWrap(True)
        layout.addWidget(self.targets_label)

        self.run_button = QPushButton("Run selected job")
        self.run_button.setObjectName("primary")
        self.checkpoint_button = QPushButton("Run complete checkpoint")
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("danger")
        self.cancel_button.setEnabled(False)
        layout.addWidget(self.run_button)
        layout.addWidget(self.checkpoint_button)
        layout.addWidget(self.cancel_button)
        return panel

    def _build_output_panel(self):
        panel = QFrame()
        panel.setObjectName("panel")
        layout = QVBoxLayout(panel)
        self.job_title = QLabel("Select a diagnostic job")
        self.job_title.setObjectName("sectionTitle")
        self.job_description = QLabel()
        self.job_description.setObjectName("muted")
        self.job_description.setWordWrap(True)
        layout.addWidget(self.job_title)
        layout.addWidget(self.job_description)

        toolbar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Find in output…")
        self.find_button = QPushButton("Find next")
        self.copy_button = QPushButton("Copy all")
        self.clear_button = QPushButton("Clear")
        toolbar.addWidget(self.search_input, 1)
        toolbar.addWidget(self.find_button)
        toolbar.addWidget(self.copy_button)
        toolbar.addWidget(self.clear_button)
        layout.addLayout(toolbar)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.output.setMaximumBlockCount(20000)
        font = QFont("Consolas")
        font.setStyleHint(QFont.Monospace)
        self.output.setFont(font)
        self.highlighter = LogHighlighter(self.output.document())
        layout.addWidget(self.output, 1)

        footer = QHBoxLayout()
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("muted")
        self.progress = QProgressBar()
        self.progress.setMaximumWidth(220)
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        self.progress.setTextVisible(False)
        self.progress.setVisible(False)
        footer.addWidget(self.status_label, 1)
        footer.addWidget(self.progress)
        layout.addLayout(footer)
        return panel

    def _connect_signals(self):
        self.job_tree.itemSelectionChanged.connect(self._job_selected)
        self.run_button.clicked.connect(self.run_selected_job)
        self.checkpoint_button.clicked.connect(lambda: self.run_job("checkpoint"))
        self.cancel_button.clicked.connect(self.runner.cancel)
        self.clear_button.clicked.connect(self.output.clear)
        self.copy_button.clicked.connect(self._copy_output)
        self.find_button.clicked.connect(self._find_next)
        self.search_input.returnPressed.connect(self._find_next)
        self.runner.output_ready.connect(self._append_output)
        self.runner.status_changed.connect(self.status_label.setText)
        self.runner.busy_changed.connect(self._busy_changed)

    def _populate_jobs(self):
        categories = {}
        for job in self.job_catalog.jobs:
            parent = categories.get(job.category)
            if parent is None:
                parent = QTreeWidgetItem((job.category,))
                parent.setFlags(parent.flags() & ~Qt.ItemIsSelectable)
                categories[job.category] = parent
                self.job_tree.addTopLevelItem(parent)
            item = QTreeWidgetItem((job.title,))
            item.setData(0, Qt.UserRole, job.key)
            item.setToolTip(0, f"{job.title}\n\n{job.description}")
            parent.addChild(item)
            self._job_items[job.key] = item
        self.job_tree.expandAll()

    def _select_job(self, job_key):
        self.job_tree.setCurrentItem(self._job_items[job_key])

    def _selected_job_key(self):
        item = self.job_tree.currentItem()
        return item.data(0, Qt.UserRole) if item else None

    def _job_selected(self):
        job_key = self._selected_job_key()
        if not job_key:
            return
        job = self.job_catalog.get(job_key)
        self.job_title.setText(job.title)
        self.job_description.setText(job.description)
        self.target_input.setEnabled(job.needs_target and not self.runner.busy)
        self.window_combo.setEnabled(job.uses_event_window and not self.runner.busy)

    def run_selected_job(self):
        job_key = self._selected_job_key()
        if job_key:
            self.run_job(job_key)

    def run_job(self, job_key):
        if self.runner.busy:
            return
        try:
            commands = self.job_catalog.build_commands(
                job_key,
                self.settings,
                target=self.target_input.text(),
                minutes=self.window_combo.currentData(),
            )
        except (RuntimeError, TypeError, ValueError) as exc:
            QMessageBox.warning(self, "Cannot run diagnostic", str(exc))
            return

        self._select_job(job_key)
        timestamp = strftime("%Y-%m-%d %H:%M:%S")
        self._append_output(
            f"\n\n### {self.job_catalog.get(job_key).title} · {timestamp} ###\n"
            "Read-only run; output is displayed in memory only.\n"
        )
        self.runner.start(commands)

    def _append_output(self, text):
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.output.setTextCursor(cursor)
        self.output.ensureCursorVisible()

    def _copy_output(self):
        self.output.selectAll()
        self.output.copy()
        cursor = self.output.textCursor()
        cursor.clearSelection()
        self.output.setTextCursor(cursor)
        self.status_label.setText("Output copied to clipboard")

    def _find_next(self):
        text = self.search_input.text()
        if not text:
            return
        if not self.output.find(text):
            cursor = self.output.textCursor()
            cursor.movePosition(QTextCursor.Start)
            self.output.setTextCursor(cursor)
            self.output.find(text)

    def _busy_changed(self, busy):
        self.run_button.setEnabled(not busy)
        self.checkpoint_button.setEnabled(not busy)
        self.cancel_button.setEnabled(busy)
        self.job_tree.setEnabled(not busy)
        selected_job = self.job_catalog.get(self._selected_job_key())
        self.target_input.setEnabled(
            bool(selected_job and selected_job.needs_target and not busy)
        )
        self.window_combo.setEnabled(
            bool(selected_job and selected_job.uses_event_window and not busy)
        )
        self.progress.setRange(0, 0 if busy else 1)
        self.progress.setVisible(busy)
        if not busy:
            self.progress.setValue(1)

    def _start_metrics(self):
        cpu_percent(interval=None)
        self.metric_timer = QTimer(self)
        self.metric_timer.timeout.connect(self._update_metrics)
        self.metric_timer.start(1000)
        self._update_metrics()

    def _update_metrics(self):
        try:
            cpu = cpu_percent(interval=None)
            memory = virtual_memory()
            current_net = net_io_counters()
        except PsutilError:
            return

        now = monotonic()
        elapsed = max(0.001, now - self._previous_time)
        rx = (current_net.bytes_recv - self._previous_net.bytes_recv) / elapsed
        tx = (current_net.bytes_sent - self._previous_net.bytes_sent) / elapsed
        self._previous_net = current_net
        self._previous_time = now

        self.cpu_card.set_value(f"{cpu:.1f}%")
        self.memory_card.set_value(f"{memory.percent:.1f}%")
        self.rx_card.set_value(f"{human_bytes(rx).strip()}/s")
        self.tx_card.set_value(f"{human_bytes(tx).strip()}/s")

    def closeEvent(self, event):
        if not self.runner.busy:
            event.accept()
            return
        answer = QMessageBox.question(
            self,
            "Diagnostic still running",
            "Cancel the current diagnostic and close WinDiagKit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            self.runner.shutdown()
            event.accept()
        else:
            event.ignore()
