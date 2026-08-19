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

    def command(self, script_name, parameters=None):
        script_path = self.script_loader.resolve(script_name)
        command = [
            "powershell.exe",
            "-NoLogo",
            "-NoProfile",
            "-NonInteractive",
            "-File",
            str(script_path),
        ]
        for name, value in (parameters or {}).items():
            if not name.isidentifier() or not isinstance(value, (str, int, float)):
                raise RuntimeError(f"Invalid PowerShell parameter: {name}")
            command.extend((f"-{name}", str(value)))
        return command

    def run(self, script_name, parameters, timeout, notice=None):
        if self.operating_system != "nt":
            print("This function is intended for Windows.")
            return False
        try:
            command = self.command(script_name, parameters)
        except RuntimeError as exc:
            print(str(exc))
            return False

        if notice:
            print(f"\n{notice}\n")
        return self.command_runner(
            command,
            timeout=timeout,
            display_command=(
                "powershell.exe -NoProfile -NonInteractive -File "
                f"<bundled {script_name}>"
            ),
        )
