import unittest
from unittest.mock import patch

from windiagkit.diagnostics.load_test import (
    DIAGNOSTIC_NOTICE,
    show_configuration_health,
    show_load_test_checkpoint,
    show_load_test_events,
    show_process_snapshot,
    show_system_resources,
)
from windiagkit.settings import Settings


class DiagnosticTests(unittest.TestCase):
    @patch("windiagkit.diagnostics.load_test.run_powershell", return_value=True)
    def test_focused_health_checks_use_separate_scripts(self, run_powershell):
        self.assertTrue(show_system_resources(timeout=12))
        self.assertTrue(show_configuration_health(timeout=13))

        self.assertEqual(
            run_powershell.call_args_list[0].args,
            ("system_resources.ps1", {}, 12, DIAGNOSTIC_NOTICE),
        )
        self.assertEqual(
            run_powershell.call_args_list[1].args,
            ("configuration_health.ps1", {}, 13, DIAGNOSTIC_NOTICE),
        )

    @patch("windiagkit.diagnostics.load_test.run_powershell", return_value=True)
    def test_event_triage_replaces_bounded_values(self, run_powershell):
        self.assertTrue(show_load_test_events(20, 30, 10))

        run_powershell.assert_called_once_with(
            "load_test_events.ps1",
            {"MINUTES": 20, "MAX_EVENTS": 30},
            10,
            DIAGNOSTIC_NOTICE,
        )

    @patch("windiagkit.diagnostics.load_test.run_powershell", return_value=True)
    def test_process_names_are_encoded_as_literals(self, run_powershell):
        self.assertTrue(show_process_snapshot(("Load App", "O'Brien"), 10, 9))

        replacements = run_powershell.call_args.args[1]
        self.assertEqual(replacements["PROCESS_NAMES"], "'Load App', 'O''Brien'")
        self.assertEqual(replacements["TOP_COUNT"], 10)

    @patch("windiagkit.diagnostics.load_test.show_load_test_events", return_value=True)
    @patch("windiagkit.diagnostics.load_test.show_process_snapshot", return_value=True)
    @patch(
        "windiagkit.diagnostics.load_test.show_configuration_health", return_value=True
    )
    @patch("windiagkit.diagnostics.load_test.show_system_resources", return_value=True)
    def test_checkpoint_runs_all_diagnostics(
        self, resources, configuration, processes, events
    ):
        settings = Settings(
            diagnostic_process_names=("problem-app",), top_process_count=12
        )

        self.assertTrue(show_load_test_checkpoint(settings))

        resources.assert_called_once_with(settings.command_timeout_seconds)
        configuration.assert_called_once_with(settings.command_timeout_seconds)
        processes.assert_called_once_with(
            ("problem-app",), 12, settings.command_timeout_seconds
        )
        events.assert_called_once_with(
            settings.event_window_minutes,
            settings.max_events,
            settings.event_query_timeout_seconds,
        )


if __name__ == "__main__":
    unittest.main()
