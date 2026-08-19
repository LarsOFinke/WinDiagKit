import unittest
from unittest.mock import patch

from windiagkit.diagnostics import events


class EventLogTests(unittest.TestCase):
    @patch("windiagkit.diagnostics.events._POWERSHELL_RUNNER.run", return_value=True)
    def test_operational_query_forwards_separate_parameters(self, powershell):
        successful = events.show_operational_log("Example'Log", 10, 25, 12)

        self.assertTrue(successful)
        script_name, parameters, timeout, notice = powershell.call_args.args
        self.assertEqual(script_name, "operational_log.ps1")
        self.assertEqual(parameters["LogName"], "Example'Log")
        self.assertEqual(parameters["Minutes"], 10)
        self.assertEqual(parameters["MaxEvents"], 25)
        self.assertEqual(timeout, 12)
        self.assertEqual(notice, events.EVENT_NOTICE)

    def test_query_limits_are_validated(self):
        with self.assertRaises(TypeError):
            events.show_operational_log("System", "15")
        with self.assertRaises(ValueError):
            events.show_operational_log("System", 0)
        with self.assertRaises(ValueError):
            events.show_system_warnings_errors(max_events=1001)

    @patch("windiagkit.diagnostics.events.show_operational_log", return_value=True)
    def test_named_log_forwards_all_settings(self, show):
        self.assertTrue(events.show_dns_log(5, 20, 8))
        show.assert_called_once_with(events.LOGS["dns"], 5, 20, 8)


if __name__ == "__main__":
    unittest.main()
