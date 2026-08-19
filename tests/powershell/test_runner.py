import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from windiagkit.powershell.powershell_runner import PowerShellRunner


class PowerShellRunnerTests(unittest.TestCase):
    def test_runner_uses_file_and_separate_parameter_arguments(self):
        script_loader = Mock()
        script_loader.resolve.return_value = Path("bundled/check.ps1")
        command_runner = Mock(return_value=True)

        successful = PowerShellRunner(
            script_loader=script_loader,
            command_runner=command_runner,
            operating_system="nt",
        ).run("check.ps1", {"Value": "O'Brien", "Count": 2}, 12)

        self.assertTrue(successful)
        script_loader.resolve.assert_called_once_with("check.ps1")
        command = command_runner.call_args.args[0]
        self.assertEqual(
            command,
            [
                "powershell.exe",
                "-NoLogo",
                "-NoProfile",
                "-NonInteractive",
                "-File",
                "bundled/check.ps1",
                "-Value",
                "O'Brien",
                "-Count",
                "2",
            ],
        )
        self.assertNotIn("-Command", command)
        self.assertNotIn("-ExecutionPolicy", command)
        self.assertEqual(command_runner.call_args.kwargs["timeout"], 12)

    def test_non_windows_does_not_resolve_a_script(self):
        script_loader = Mock()
        runner = PowerShellRunner(script_loader=script_loader, operating_system="posix")

        self.assertFalse(runner.run("check.ps1", {}, 12))
        script_loader.resolve.assert_not_called()

    @patch("builtins.print")
    def test_resolution_failure_is_reported(self, output):
        script_loader = Mock()
        script_loader.resolve.side_effect = RuntimeError("missing script")
        runner = PowerShellRunner(script_loader=script_loader, operating_system="nt")

        self.assertFalse(runner.run("missing.ps1", {}, 12))
        output.assert_called_once_with("missing script")

    def test_invalid_parameter_is_rejected(self):
        script_loader = Mock()
        script_loader.resolve.return_value = Path("bundled/check.ps1")
        runner = PowerShellRunner(script_loader=script_loader)

        with self.assertRaisesRegex(RuntimeError, "Invalid PowerShell parameter"):
            runner.command("check.ps1", {"Bad-Name": "value"})


if __name__ == "__main__":
    unittest.main()
