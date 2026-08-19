import unittest
from unittest.mock import patch

from windiagkit.powershell.runner import run_powershell


class PowerShellRunnerTests(unittest.TestCase):
    @patch("windiagkit.powershell.runner.os_name", "nt")
    @patch("windiagkit.powershell.runner.run_visible", return_value=True)
    @patch("windiagkit.powershell.runner.load_script", return_value="script body")
    def test_runs_a_bundled_script(self, load_script, run_visible):
        self.assertTrue(run_powershell("check.ps1", {"VALUE": 2}, 12, "Notice"))

        load_script.assert_called_once_with("check.ps1", {"VALUE": 2})
        self.assertEqual(run_visible.call_args.args[0][-1], "script body")
        self.assertEqual(run_visible.call_args.kwargs["timeout"], 12)
        self.assertIn(
            "<bundled check.ps1>", run_visible.call_args.kwargs["display_command"]
        )

    @patch("windiagkit.powershell.runner.load_script")
    def test_non_windows_does_not_load_a_script(self, load_script):
        self.assertFalse(run_powershell("check.ps1", {}, 12))
        load_script.assert_not_called()

    @patch("windiagkit.powershell.runner.os_name", "nt")
    @patch(
        "windiagkit.powershell.runner.load_script",
        side_effect=RuntimeError("missing script"),
    )
    def test_load_failure_is_reported(self, load_script):
        self.assertFalse(run_powershell("missing.ps1", {}, 12))


if __name__ == "__main__":
    unittest.main()
