import unittest

from windiagkit.powershell_scripts import (
    load_script,
    powershell_array,
    powershell_literal,
)


class PowerShellScriptTests(unittest.TestCase):
    def test_operational_script_replaces_all_values(self):
        script = load_script(
            "operational_log.ps1",
            {"LOG_NAME": "'System'", "MINUTES": 15, "MAX_EVENTS": 100},
        )

        self.assertIn("$logName = 'System'", script)
        self.assertIn("AddMinutes(-15)", script)
        self.assertIn("Select-Object -First 100", script)
        self.assertNotIn("__LOG_NAME__", script)

    def test_missing_script_reports_a_runtime_error(self):
        with self.assertRaises(RuntimeError):
            load_script("missing.ps1", {})

    def test_script_paths_are_not_accepted(self):
        with self.assertRaisesRegex(RuntimeError, "Invalid PowerShell script name"):
            load_script("../outside.ps1", {})

    def test_unresolved_placeholders_are_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "__MAX_EVENTS__"):
            load_script(
                "operational_log.ps1",
                {"LOG_NAME": "'System'", "MINUTES": 15},
            )

    def test_acpi_script_is_available(self):
        script = load_script("acpi_temperatures.ps1", {})

        self.assertIn("MSAcpi_ThermalZoneTemperature", script)

    def test_load_test_scripts_are_available(self):
        resources = load_script("system_resources.ps1", {})
        configuration = load_script("configuration_health.ps1", {})
        events = load_script("load_test_events.ps1", {"MINUTES": 15, "MAX_EVENTS": 100})
        processes = load_script(
            "process_snapshot.ps1", {"PROCESS_NAMES": "", "TOP_COUNT": 15}
        )

        self.assertIn("Win32_PageFileUsage", resources)
        self.assertIn("Win32_PnPEntity", configuration)
        self.assertIn("WHEA-Logger", events)
        self.assertIn("Get-Process", processes)

    def test_powershell_values_are_escaped(self):
        self.assertEqual(powershell_literal("O'Brien"), "'O''Brien'")
        self.assertEqual(powershell_array(("one", "two")), "'one', 'two'")


if __name__ == "__main__":
    unittest.main()
