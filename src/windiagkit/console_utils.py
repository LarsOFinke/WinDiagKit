import os
import subprocess


APP_NAME = "WinDiagKit"


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def pause(message="Press Enter to continue..."):
    input(f"\n{message}")


def run_visible(command, timeout=None):
    """Run a command in the current console. Output is not captured or saved."""
    print("\n> " + subprocess.list2cmdline(command))
    try:
        result = subprocess.run(command, check=False, timeout=timeout)
    except FileNotFoundError:
        print(f"Command not found: {command[0]}")
        return False
    except OSError as exc:
        print(f"Could not start {command[0]}: {exc}")
        return False
    except subprocess.TimeoutExpired:
        print(f"Command timed out after {timeout:g} seconds.")
        return False
    except KeyboardInterrupt:
        print("Command interrupted.")
        return False

    if result.returncode != 0:
        print(f"Command exited with status {result.returncode}.")
        return False
    return True


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
