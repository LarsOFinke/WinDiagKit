import unittest

from windiagkit.powershell.script_loader import PowerShellScriptLoader


class PowerShellScriptTests(unittest.TestCase):
    def setUp(self):
        self.loader = PowerShellScriptLoader()

    def test_resolves_a_bundled_script(self):
        script_path = self.loader.resolve("acpi_temperatures.ps1")

        self.assertTrue(script_path.is_file())
        self.assertIn("MSAcpi_ThermalZoneTemperature", script_path.read_text("utf-8"))

    def test_all_bundled_scripts_are_static_and_placeholder_free(self):
        scripts = tuple(self.loader.script_directory.glob("*.ps1"))

        self.assertGreaterEqual(len(scripts), 7)
        for script_path in scripts:
            with self.subTest(script=script_path.name):
                script = script_path.read_text(encoding="utf-8")
                self.assertNotRegex(script, r"__[A-Z][A-Z0-9_]*__")

    def test_missing_script_reports_a_runtime_error(self):
        with self.assertRaisesRegex(RuntimeError, "not found"):
            self.loader.resolve("missing.ps1")

    def test_script_paths_are_not_accepted(self):
        for script_name in ("../outside.ps1", r"..\outside.ps1", "outside.txt"):
            with (
                self.subTest(script_name=script_name),
                self.assertRaisesRegex(RuntimeError, "Invalid PowerShell script name"),
            ):
                self.loader.resolve(script_name)


if __name__ == "__main__":
    unittest.main()
