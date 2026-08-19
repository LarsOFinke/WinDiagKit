from os import name as os_name

from ..cli.console import run_visible
from .loader import load_script


def powershell_command(script):
    return [
        "powershell.exe",
        "-NoLogo",
        "-NoProfile",
        "-NonInteractive",
        "-Command",
        script,
    ]


def run_powershell(script_name, replacements, timeout, notice=None):
    """Run one bundled diagnostic through the shared PowerShell boundary."""
    if os_name != "nt":
        print("This function is intended for Windows.")
        return False

    try:
        script = load_script(script_name, replacements)
    except RuntimeError as exc:
        print(exc)
        return False

    if notice:
        print(f"\n{notice}\n")

    return run_visible(
        powershell_command(script),
        timeout=timeout,
        display_command=(
            "powershell.exe -NoProfile -NonInteractive -Command "
            f"<bundled {script_name}>"
        ),
    )
