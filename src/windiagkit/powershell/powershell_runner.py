"""Read-only PowerShell process boundary."""

from os import name as os_name

from ..cli.console import run_visible
from .script_loader import PowerShellScriptLoader


class PowerShellRunner:
    def __init__(
        self, script_loader=None, command_runner=run_visible, operating_system=os_name
    ):
        self.script_loader = script_loader or PowerShellScriptLoader()
        self.command_runner = command_runner
        self.operating_system = operating_system

    def command(self, script):
        return [
            "powershell.exe",
            "-NoLogo",
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            script,
        ]

    def run(self, script_name, replacements, timeout, notice=None):
        if self.operating_system != "nt":
            print("This function is intended for Windows.")
            return False
        try:
            script = self.script_loader.load(script_name, replacements)
        except RuntimeError as exc:
            print(str(exc))
            return False

        if notice:
            print(f"\n{notice}\n")
        return self.command_runner(
            self.command(script),
            timeout=timeout,
            display_command=(
                "powershell.exe -NoProfile -NonInteractive -Command "
                f"<bundled {script_name}>"
            ),
        )
