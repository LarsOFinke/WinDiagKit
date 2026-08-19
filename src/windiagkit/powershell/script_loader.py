"""Locates bundled PowerShell scripts without generating code at runtime."""

from pathlib import Path


class PowerShellScriptLoader:
    def __init__(self, script_directory=None):
        self.script_directory = script_directory or Path(__file__).resolve().with_name(
            "scripts"
        )

    def resolve(self, script_name):
        if (
            not script_name.lower().endswith(".ps1")
            or "/" in script_name
            or "\\" in script_name
        ):
            raise RuntimeError(f"Invalid PowerShell script name: {script_name}")

        script_path = self.script_directory / script_name
        if not script_path.is_file():
            raise RuntimeError(f"PowerShell script not found: {script_name}")
        return script_path
