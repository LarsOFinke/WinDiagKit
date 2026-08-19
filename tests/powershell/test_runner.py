import unittest
from unittest.mock import Mock, patch

from windiagkit.powershell.powershell_runner import PowerShellRunner


class PowerShellRunnerTests(unittest.TestCase):
    def test_object_runner_uses_injected_dependencies(self):
        script_loader = Mock()
        script_loader.load.return_value = "Get-Date"
        command_runner = Mock(return_value=True)

        successful = PowerShellRunner(
            script_loader=script_loader,
            command_runner=command_runner,
            operating_system="nt",
        ).run("check.ps1", {"VALUE": 2}, 12)

        self.assertTrue(successful)
        command_runner.assert_called_once()

        script_loader.load.assert_called_once_with("check.ps1", {"VALUE": 2})
        self.assertEqual(command_runner.call_args.args[0][-1], "Get-Date")
        self.assertEqual(command_runner.call_args.kwargs["timeout"], 12)
        self.assertIn(
            "<bundled check.ps1>",
            command_runner.call_args.kwargs["display_command"],
        )

    def test_non_windows_does_not_load_a_script(self):
        script_loader = Mock()
        runner = PowerShellRunner(script_loader=script_loader, operating_system="posix")

        self.assertFalse(runner.run("check.ps1", {}, 12))
        script_loader.load.assert_not_called()

    @patch("builtins.print")
    def test_load_failure_is_reported(self, output):
        script_loader = Mock()
        script_loader.load.side_effect = RuntimeError("missing script")
        runner = PowerShellRunner(script_loader=script_loader, operating_system="nt")

        self.assertFalse(runner.run("missing.ps1", {}, 12))
        output.assert_called_once_with("missing script")


if __name__ == "__main__":
    unittest.main()
