from pathlib import Path
from re import findall

SCRIPT_DIRECTORY = Path(__file__).resolve().with_name("powershell")


def powershell_literal(value):
    return "'" + str(value).replace("'", "''") + "'"


def powershell_array(values):
    return ", ".join(powershell_literal(value) for value in values)


def load_script(script_name, replacements):
    if (
        not script_name.lower().endswith(".ps1")
        or "/" in script_name
        or "\\" in script_name
    ):
        raise RuntimeError(f"Invalid PowerShell script name: {script_name}")

    script_path = SCRIPT_DIRECTORY / script_name
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
