from pathlib import Path


SCRIPT_DIRECTORY = Path(__file__).resolve().with_name("powershell")


def load_script(script_name, replacements):
    script_path = SCRIPT_DIRECTORY / script_name
    try:
        script = script_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"Could not load PowerShell script {script_name}: {exc}") from exc

    for name, value in replacements.items():
        script = script.replace(f"__{name}__", str(value))
    return script
