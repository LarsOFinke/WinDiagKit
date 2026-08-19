import unittest
from unittest.mock import patch

from windiagkit.cli.menus import diagnostic_menu, main_menu
from windiagkit.config import Settings


class MenuTests(unittest.TestCase):
    @patch("windiagkit.cli.menus.pause")
    @patch("windiagkit.cli.menus.show_load_test_checkpoint")
    @patch("windiagkit.cli.menus.show_process_snapshot")
    @patch("windiagkit.cli.menus.show_load_test_events")
    @patch("windiagkit.cli.menus.show_configuration_health")
    @patch("windiagkit.cli.menus.show_system_resources")
    @patch("windiagkit.cli.menus.header")
    @patch("builtins.input", side_effect=("1", "2", "3", "4", "5", "0"))
    def test_diagnostic_menu_routes_every_action(
        self,
        user_input,
        header,
        resources,
        configuration,
        events,
        processes,
        checkpoint,
        pause,
    ):
        settings = Settings(
            diagnostic_process_names=("load-app",), top_process_count=10
        )

        diagnostic_menu(settings)

        resources.assert_called_once_with(settings.command_timeout_seconds)
        configuration.assert_called_once_with(settings.command_timeout_seconds)
        events.assert_called_once_with(
            settings.event_window_minutes,
            settings.max_events,
            settings.event_query_timeout_seconds,
        )
        processes.assert_called_once_with(
            ("load-app",), 10, settings.command_timeout_seconds
        )
        checkpoint.assert_called_once_with(settings)
        self.assertEqual(pause.call_count, 5)

    @patch("windiagkit.cli.menus.diagnostic_menu")
    @patch("windiagkit.cli.menus.header")
    @patch("builtins.input", side_effect=("4", "0"))
    def test_main_menu_opens_diagnostics(self, user_input, header, diagnostics):
        settings = Settings()

        main_menu(settings)

        diagnostics.assert_called_once_with(settings)


if __name__ == "__main__":
    unittest.main()
