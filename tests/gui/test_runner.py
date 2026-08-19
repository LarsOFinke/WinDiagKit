import os
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtCore import QEventLoop, QTimer
from PyQt5.QtWidgets import QApplication

from windiagkit.diagnostics.catalog import CommandSpec
from windiagkit.gui.job_runner import JobRunner


class JobRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def test_runs_commands_in_sequence_and_captures_output(self):
        runner = JobRunner()
        output = []
        result = []
        loop = QEventLoop()
        runner.output_ready.connect(output.append)
        runner.finished.connect(result.append)
        runner.finished.connect(loop.quit)
        QTimer.singleShot(5000, loop.quit)

        commands = tuple(
            CommandSpec(
                f"step {value}",
                (sys.executable, "-c", f"print('value {value}')"),
                3,
                f"python step {value}",
            )
            for value in (1, 2)
        )
        runner.start(commands)
        loop.exec_()

        text = "".join(output)
        self.assertEqual(result, [True])
        self.assertIn("value 1", text)
        self.assertIn("value 2", text)
        self.assertFalse(runner.busy)

    def test_failed_start_is_reported_without_hanging(self):
        runner = JobRunner()
        output = []
        result = []
        loop = QEventLoop()
        runner.output_ready.connect(output.append)
        runner.finished.connect(result.append)
        runner.finished.connect(loop.quit)
        QTimer.singleShot(5000, loop.quit)

        runner.start(
            (CommandSpec("missing", ("missing-windiagkit-command",), 3, "missing"),)
        )
        loop.exec_()

        self.assertEqual(result, [False])
        self.assertIn("Could not start", "".join(output))

    def test_running_command_can_be_cancelled(self):
        runner = JobRunner()
        result = []
        loop = QEventLoop()
        runner.finished.connect(result.append)
        runner.finished.connect(loop.quit)
        QTimer.singleShot(100, runner.cancel)
        QTimer.singleShot(5000, loop.quit)

        runner.start(
            (
                CommandSpec(
                    "long command",
                    (sys.executable, "-c", "import time; time.sleep(10)"),
                    15,
                    "long command",
                ),
            )
        )
        loop.exec_()

        self.assertEqual(result, [False])
        self.assertFalse(runner.busy)


if __name__ == "__main__":
    unittest.main()
