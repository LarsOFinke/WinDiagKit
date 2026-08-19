def bounded_integer(name, value, minimum, maximum):
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return value


def network_target(value):
    if not isinstance(value, str):
        raise TypeError("target must be text")
    target = value.strip()
    if not target or len(target) > 253 or any(char.isspace() for char in target):
        raise ValueError("target must be a host name or IP address without spaces")
    return target
