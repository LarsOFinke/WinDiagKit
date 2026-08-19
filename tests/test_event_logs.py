import unittest
from unittest.mock import patch

from windiagkit import event_logs


class EventLogTests(unittest.TestCase):
    @patch("windiagkit.event_logs._powershell", return_value=True)
    def test_operational_query_reports_empty_results_and_escapes_name(self, powershell):
        successful = event_logs.show_operational_log("Example'Log", 10, 25, 12)

        self.assertTrue(successful)
        script, timeout = powershell.call_args.args
        self.assertIn("$logName = 'Example''Log'", script)
        self.assertIn("No matching events found.", script)
        self.assertIn("Select-Object -First 25", script)
        self.assertEqual(timeout, 12)

    def test_query_limits_are_validated(self):
        with self.assertRaises(TypeError):
            event_logs.show_operational_log("System", "15")
        with self.assertRaises(ValueError):
            event_logs.show_operational_log("System", 0)
        with self.assertRaises(ValueError):
            event_logs.show_system_warnings_errors(max_events=1001)

    @patch("windiagkit.event_logs.show_operational_log", return_value=True)
    def test_named_log_forwards_all_settings(self, show):
        self.assertTrue(event_logs.show_dns_log(5, 20, 8))
        show.assert_called_once_with(event_logs.LOGS["dns"], 5, 20, 8)


if __name__ == "__main__":
    unittest.main()
