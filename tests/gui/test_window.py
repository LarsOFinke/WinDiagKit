import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication

from windiagkit.gui.event_windows import (
    DEFAULT_EVENT_WINDOW_MINUTES,
    EVENT_WINDOW_OPTIONS,
)
from windiagkit.gui.main_window import MainWindow
from windiagkit.settings import Settings


class GuiSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = MainWindow(Settings())

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()
        self.application.processEvents()

    def test_window_exposes_every_job_and_defaults_to_checkpoint(self):
        self.assertEqual(len(self.window._job_items), len(self.window.job_catalog.jobs))
        self.assertEqual(self.window._selected_job_key(), "checkpoint")
        self.assertTrue(self.window.window_combo.isEnabled())
        self.assertFalse(self.window.target_input.isEnabled())

    def test_event_window_uses_gui_presets_not_ini_choices(self):
        window = MainWindow(
            Settings(event_window_minutes=5, event_window_choices=(5, 10))
        )
        self.addCleanup(window.close)
        self.addCleanup(window.deleteLater)

        self.assertEqual(
            tuple(
                (
                    window.window_combo.itemText(index),
                    window.window_combo.itemData(index),
                )
                for index in range(window.window_combo.count())
            ),
            EVENT_WINDOW_OPTIONS,
        )
        self.assertEqual(
            window.window_combo.currentData(), DEFAULT_EVENT_WINDOW_MINUTES
        )

    def test_context_controls_follow_job_requirements(self):
        self.window._select_job("ping")
        self.assertTrue(self.window.target_input.isEnabled())
        self.assertFalse(self.window.window_combo.isEnabled())

        self.window._select_job("system_events")
        self.assertFalse(self.window.target_input.isEnabled())
        self.assertTrue(self.window.window_combo.isEnabled())

    def test_output_is_searchable_and_clearable(self):
        self.window._append_output("[WARNING] sample diagnostic text\n")
        self.window.search_input.setText("diagnostic")
        self.window._find_next()
        self.assertTrue(self.window.output.textCursor().hasSelection())

        self.window.clear_button.click()
        self.assertEqual(self.window.output.toPlainText(), "")


if __name__ == "__main__":
    unittest.main()
