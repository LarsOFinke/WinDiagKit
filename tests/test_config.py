import tempfile
import unittest
from pathlib import Path

from windiagkit.config import Settings, load_settings


class SettingsTests(unittest.TestCase):
    def test_missing_file_uses_defaults(self):
        warnings = []

        settings = load_settings(warn=warnings.append)

        self.assertEqual(settings, Settings())
        self.assertEqual(warnings, [])

    def test_blank_process_list_is_valid(self):
        content = "[diagnostics]\nprocess_names =\n"
        warnings = []
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "winddiagkit.ini")
            path.write_text(content, encoding="utf-8")

            settings = load_settings(path, warn=warnings.append)

        self.assertEqual(settings.diagnostic_process_names, ())
        self.assertEqual(warnings, [])

    def test_loads_configured_values(self):
        content = """
[network]
default_target = internal.example
ping_count = 2
ping_timeout_ms = 500
traceroute_max_hops = 12
traceroute_timeout_ms = 750
command_timeout_seconds = 20

[events]
default_window_minutes = 10
window_choices = 10, 20
max_events = 25
query_timeout_seconds = 15

[monitor]
sample_seconds = 2
acpi_refresh_seconds = 8
helper_timeout_seconds = 3

[diagnostics]
process_names = LoadApp.exe, helper, loadapp
top_process_count = 20
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "winddiagkit.ini")
            path.write_text(content, encoding="utf-8")

            settings = load_settings(path)

        self.assertEqual(settings.default_target, "internal.example")
        self.assertEqual(settings.event_window_choices, (10, 20))
        self.assertEqual(settings.max_events, 25)
        self.assertEqual(settings.traceroute_max_hops, 12)
        self.assertEqual(settings.sample_seconds, 2.0)
        self.assertEqual(settings.diagnostic_process_names, ("LoadApp", "helper"))
        self.assertEqual(settings.top_process_count, 20)

    def test_invalid_values_warn_and_fall_back(self):
        content = """
[network]
default_target = invalid target
ping_count = 0

[events]
default_window_minutes = 7
window_choices = 5, 15
max_events = many

[diagnostics]
process_names = valid, C:\\not-allowed\\program.exe
top_process_count = 100
"""
        warnings = []
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "winddiagkit.ini")
            path.write_text(content, encoding="utf-8")

            settings = load_settings(path, warn=warnings.append)

        self.assertEqual(settings.default_target, "example.com")
        self.assertEqual(settings.ping_count, 4)
        self.assertEqual(settings.event_window_minutes, 5)
        self.assertEqual(settings.max_events, 100)
        self.assertEqual(settings.diagnostic_process_names, ())
        self.assertEqual(settings.top_process_count, 15)
        self.assertGreaterEqual(len(warnings), 6)


if __name__ == "__main__":
    unittest.main()
