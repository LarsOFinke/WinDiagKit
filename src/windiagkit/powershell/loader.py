from .script_loader import PowerShellScriptLoader

_DEFAULT_LOADER = PowerShellScriptLoader()
SCRIPT_DIRECTORY = _DEFAULT_LOADER.script_directory


def powershell_literal(value):
    return _DEFAULT_LOADER.literal(value)


def powershell_array(values):
    return _DEFAULT_LOADER.array(values)


def load_script(script_name, replacements):
    return _DEFAULT_LOADER.load(script_name, replacements)
