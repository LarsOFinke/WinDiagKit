import os
import subprocess


APP_NAME = "WinDiagKit"


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def pause(message="Press Enter to continue..."):
    input(f"\n{message}")


def run_visible(command):
    """Run a command in the current console. Output is not captured or saved."""
    print("\n> " + subprocess.list2cmdline(command))
    subprocess.run(command, check=False)


def hidden_output(command, timeout=3):
    """Run a helper command and keep stdout only in RAM."""
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            creationflags=flags,
        )
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""
