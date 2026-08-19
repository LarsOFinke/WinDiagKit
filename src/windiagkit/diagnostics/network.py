from os import name
from socket import AF_INET, AF_INET6, SOCK_STREAM, gaierror, getaddrinfo

from ..cli.console import run_visible


def _windows_only():
    if name == "nt":
        return True
    print("This function is intended for Windows.")
    return False


def show_ipconfig(command_timeout=30.0):
    if _windows_only():
        run_visible(["ipconfig", "/all"], timeout=command_timeout)


def resolve_addresses(host):
    print(f"\nDNS resolution for: {host}")
    print("A/AAAA results do not prove which IP family reached the DNS resolver.\n")

    for family, label in ((AF_INET, "IPv4 / A"), (AF_INET6, "IPv6 / AAAA")):
        try:
            entries = getaddrinfo(host, None, family, SOCK_STREAM)
            addresses = sorted({entry[4][0] for entry in entries})
            print(f"{label}:")
            for address in addresses:
                print(f"  {address}")
        except gaierror as exc:
            print(f"{label}: resolution failed ({exc})")


def ping_test(host, count=4, timeout_ms=2000, command_timeout=30.0):
    if not _windows_only():
        return

    print(f"\nIPv4 connectivity: {host}")
    run_visible(
        ["ping", "-4", "-n", str(count), "-w", str(timeout_ms), host],
        timeout=command_timeout,
    )

    print(f"\nIPv6 connectivity: {host}")
    run_visible(
        ["ping", "-6", "-n", str(count), "-w", str(timeout_ms), host],
        timeout=command_timeout,
    )


def traceroute_test(host, max_hops=20, timeout_ms=1000, command_timeout=30.0):
    if not _windows_only():
        return

    print(f"\nIPv4 route trace: {host}")
    run_visible(
        ["tracert", "-4", "-d", "-h", str(max_hops), "-w", str(timeout_ms), host],
        timeout=command_timeout,
    )

    print(f"\nIPv6 route trace: {host}")
    run_visible(
        ["tracert", "-6", "-d", "-h", str(max_hops), "-w", str(timeout_ms), host],
        timeout=command_timeout,
    )
