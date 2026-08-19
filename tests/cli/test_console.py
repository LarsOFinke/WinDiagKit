import subprocess
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from windiagkit.cli.console import hidden_output, run_visible


class RunVisibleTests(unittest.TestCase):
    @patch("windiagkit.cli.console.run")
    def test_success(self, run):
        run.return_value = subprocess.CompletedProcess(["tool"], 0)

        self.assertTrue(run_visible(["tool"], timeout=2))
        run.assert_called_once_with(["tool"], check=False, timeout=2)

    @patch("windiagkit.cli.console.run")
    def test_safe_display_label_does_not_change_execution(self, run):
        run.return_value = subprocess.CompletedProcess(["tool", "secret"], 0)
        output = StringIO()

        with redirect_stdout(output):
            self.assertTrue(
                run_visible(
                    ["tool", "secret"], display_command="tool <validated input>"
                )
            )

        self.assertIn("tool <validated input>", output.getvalue())
        self.assertNotIn("secret", output.getvalue())
        run.assert_called_once_with(["tool", "secret"], check=False, timeout=None)

    @patch("windiagkit.cli.console.run", side_effect=FileNotFoundError)
    def test_missing_command_is_reported(self, run):
        output = StringIO()

        with redirect_stdout(output):
            successful = run_visible(["missing"])

        self.assertFalse(successful)
        self.assertIn("Command not found", output.getvalue())

    @patch("windiagkit.cli.console.run")
    def test_nonzero_exit_is_reported(self, run):
        run.return_value = subprocess.CompletedProcess(["tool"], 5)
        output = StringIO()

        with redirect_stdout(output):
            successful = run_visible(["tool"])

        self.assertFalse(successful)
        self.assertIn("status 5", output.getvalue())

    @patch("windiagkit.cli.console.run", side_effect=KeyboardInterrupt)
    def test_keyboard_interrupt_returns_to_application(self, run):
        output = StringIO()

        with redirect_stdout(output):
            successful = run_visible(["tool"])

        self.assertFalse(successful)
        self.assertIn("interrupted", output.getvalue())

    @patch("windiagkit.cli.console.run")
    def test_hidden_output_returns_stdout(self, run):
        run.return_value = subprocess.CompletedProcess(["tool"], 0, " value \n", "")

        self.assertEqual(hidden_output(["tool"]), "value")


if __name__ == "__main__":
    unittest.main()
