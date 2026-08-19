import unittest
from pathlib import Path

from windiagkit import __version__


class BuildScriptTests(unittest.TestCase):
    def setUp(self):
        self.project_root = Path(__file__).resolve().parents[1]

    def _read_script(self, architecture):
        return (self.project_root / "scripts" / f"build_{architecture}.bat").read_text(
            encoding="utf-8"
        )

    def test_x64_build_requires_64_bit_python_and_x64_dependencies(self):
        script = self._read_script("x64")

        self.assertIn("struct.calcsize('P') * 8 == 64", script)
        self.assertIn('pip install ".[build]"', script)

    def test_x86_build_requires_32_bit_python_and_x86_dependencies(self):
        script = self._read_script("x86")

        self.assertIn("struct.calcsize('P') * 8 == 32", script)
        self.assertIn("requirements-x86.txt", script)

    def test_both_builds_bundle_the_gui_and_powershell_scripts(self):
        for architecture in ("x64", "x86"):
            with self.subTest(architecture=architecture):
                script = self._read_script(architecture)
                self.assertIn("--windowed", script)
                self.assertIn("--onefile", script)
                self.assertNotIn("--onedir", script)
                self.assertIn("--noupx", script)
                self.assertIn(
                    '--version-file "scripts\\windows_version_info.txt"', script
                )
                self.assertIn("src\\gui_main.py", script)
                self.assertIn("windiagkit\\powershell\\scripts", script)

    def test_both_builds_offer_optional_authenticode_signing(self):
        for architecture in ("x64", "x86"):
            with self.subTest(architecture=architecture):
                script = self._read_script(architecture)
                self.assertIn("WINDIAGKIT_SIGN_CERT_SHA1", script)
                self.assertIn("sign_release.bat", script)

        signing_script = (self.project_root / "scripts" / "sign_release.bat").read_text(
            encoding="utf-8"
        )
        self.assertIn("signtool.exe sign", signing_script)
        self.assertIn("signtool.exe verify /pa /v", signing_script)

    def test_pyproject_defines_installable_commands_and_script_resources(self):
        pyproject = (self.project_root / "pyproject.toml").read_text(encoding="utf-8")

        self.assertIn('windiagkit = "windiagkit.cli.app:main"', pyproject)
        self.assertIn('windiagkit-gui = "windiagkit.gui.app:main"', pyproject)
        self.assertIn('"PyQt5-Qt5>=5.15.2,<5.16"', pyproject)
        self.assertIn('"windiagkit.powershell" = ["scripts/*.ps1"]', pyproject)

    def test_windows_metadata_matches_the_package_version(self):
        version_info = (
            self.project_root / "scripts" / "windows_version_info.txt"
        ).read_text(encoding="utf-8")

        self.assertIn(f'StringStruct("ProductVersion", "{__version__}")', version_info)
        self.assertIn(f'StringStruct("FileVersion", "{__version__}")', version_info)


if __name__ == "__main__":
    unittest.main()
