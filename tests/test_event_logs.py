import unittest
from unittest.mock import patch

from windiagkit import event_logs


class EventLogTests(unittest.TestCase):
    @patch("windiagkit.event_logs.run_powershell", return_value=True)
    def test_operational_query_escapes_name_and_forwards_limits(self, powershell):
        successful = event_logs.show_operational_log("Example'Log", 10, 25, 12)

        self.assertTrue(successful)
        script_name, replacements, timeout, notice = powershell.call_args.args
        self.assertEqual(script_name, "operational_log.ps1")
        self.assertEqual(replacements["LOG_NAME"], "'Example''Log'")
        self.assertEqual(replacements["MINUTES"], 10)
        self.assertEqual(replacements["MAX_EVENTS"], 25)
        self.assertEqual(timeout, 12)
        self.assertEqual(notice, event_logs.EVENT_NOTICE)

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
