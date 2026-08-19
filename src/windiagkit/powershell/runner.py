from os import name as os_name

from ..cli.console import run_visible
from .loader import load_script
from .powershell_runner import PowerShellRunner


def powershell_command(script):
    return PowerShellRunner().command(script)


def run_powershell(script_name, replacements, timeout, notice=None):
    """Run one bundled diagnostic through the shared PowerShell boundary."""
    runner = PowerShellRunner(command_runner=run_visible, operating_system=os_name)
    runner.script_loader.load = load_script
    return runner.run(script_name, replacements, timeout, notice)
