import unittest

from windiagkit.powershell.script_loader import PowerShellScriptLoader


class PowerShellScriptTests(unittest.TestCase):
    def setUp(self):
        self.loader = PowerShellScriptLoader()

    def test_object_loader_uses_the_bundled_scripts(self):
        self.assertEqual(self.loader.literal("O'Brien"), "'O''Brien'")
        self.assertIn("Get-CimInstance", self.loader.load("acpi_temperatures.ps1", {}))

    def test_operational_script_replaces_all_values(self):
        script = self.loader.load(
            "operational_log.ps1",
            {"LOG_NAME": "'System'", "MINUTES": 15, "MAX_EVENTS": 100},
        )

        self.assertIn("$logName = 'System'", script)
        self.assertIn("AddMinutes(-15)", script)
        self.assertIn("Select-Object -First 100", script)
        self.assertNotIn("__LOG_NAME__", script)

    def test_missing_script_reports_a_runtime_error(self):
        with self.assertRaises(RuntimeError):
            self.loader.load("missing.ps1", {})

    def test_script_paths_are_not_accepted(self):
        with self.assertRaisesRegex(RuntimeError, "Invalid PowerShell script name"):
            self.loader.load("../outside.ps1", {})

    def test_unresolved_placeholders_are_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "__MAX_EVENTS__"):
            self.loader.load(
                "operational_log.ps1",
                {"LOG_NAME": "'System'", "MINUTES": 15},
            )

    def test_acpi_script_is_available(self):
        script = self.loader.load("acpi_temperatures.ps1", {})

        self.assertIn("MSAcpi_ThermalZoneTemperature", script)

    def test_load_test_scripts_are_available(self):
        resources = self.loader.load("system_resources.ps1", {})
        configuration = self.loader.load("configuration_health.ps1", {})
        events = self.loader.load(
            "load_test_events.ps1", {"MINUTES": 15, "MAX_EVENTS": 100}
        )
        processes = self.loader.load(
            "process_snapshot.ps1", {"PROCESS_NAMES": "", "TOP_COUNT": 15}
        )

        self.assertIn("Win32_PageFileUsage", resources)
        self.assertIn("Win32_PnPEntity", configuration)
        self.assertIn("WHEA-Logger", events)
        self.assertIn("Get-Process", processes)

    def test_dns_resolution_script_is_available(self):
        script = self.loader.load(
            "dns_resolution.ps1",
            {"HOST_NAME": self.loader.literal("example.com")},
        )

        self.assertIn("Resolve-DnsName", script)
        self.assertNotIn("__HOST_NAME__", script)

    def test_powershell_values_are_escaped(self):
        self.assertEqual(self.loader.literal("O'Brien"), "'O''Brien'")
        self.assertEqual(self.loader.array(("one", "two")), "'one', 'two'")


if __name__ == "__main__":
    unittest.main()
