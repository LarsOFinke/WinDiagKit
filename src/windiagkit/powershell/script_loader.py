"""Loads and safely parameterizes bundled PowerShell scripts."""

from pathlib import Path
from re import findall


class PowerShellScriptLoader:
    def __init__(self, script_directory=None):
        self.script_directory = script_directory or Path(__file__).resolve().with_name(
            "scripts"
        )

    def literal(self, value):
        return "'" + str(value).replace("'", "''") + "'"

    def array(self, values):
        return ", ".join(self.literal(value) for value in values)

    def load(self, script_name, replacements):
        if (
            not script_name.lower().endswith(".ps1")
            or "/" in script_name
            or "\\" in script_name
        ):
            raise RuntimeError(f"Invalid PowerShell script name: {script_name}")

        script_path = self.script_directory / script_name
        try:
            script = script_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise RuntimeError(
                f"Could not load PowerShell script {script_name}: {exc}"
            ) from exc

        for name, value in replacements.items():
            script = script.replace(f"__{name}__", str(value))
        unresolved = findall(r"__[A-Z][A-Z0-9_]*__", script)
        if unresolved:
            names = ", ".join(sorted(set(unresolved)))
            raise RuntimeError(f"Unresolved placeholders in {script_name}: {names}")
        return script
