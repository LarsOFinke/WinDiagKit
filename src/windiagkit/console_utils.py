from os import name
from subprocess import SubprocessError, TimeoutExpired, list2cmdline, run


APP_NAME = "WinDiagKit"


def clear_screen():
    # ANSI terminal control sequences avoid launching a shell just to redraw UI.
    print("\033[2J\033[H", end="")


def pause(message="Press Enter to continue..."):
    input(f"\n{message}")


def run_visible(command, timeout=None):
    """Run a command in the current console. Output is not captured or saved."""
    print("\n> " + list2cmdline(command))
    try:
        result = run(command, check=False, timeout=timeout)
    except FileNotFoundError:
        print(f"Command not found: {command[0]}")
        return False
    except OSError as exc:
        print(f"Could not start {command[0]}: {exc}")
        return False
    except TimeoutExpired:
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
    if name == "nt":
        from subprocess import CREATE_NO_WINDOW

        flags = CREATE_NO_WINDOW
    else:
        flags = 0
    try:
        result = run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            creationflags=flags,
        )
        return result.stdout.strip()
    except (OSError, SubprocessError):
        return ""
