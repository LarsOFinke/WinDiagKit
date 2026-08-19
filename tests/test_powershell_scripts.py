import unittest

from windiagkit.powershell_scripts import load_script


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

    def test_acpi_script_is_available(self):
        script = load_script("acpi_temperatures.ps1", {})

        self.assertIn("MSAcpi_ThermalZoneTemperature", script)


if __name__ == "__main__":
    unittest.main()
