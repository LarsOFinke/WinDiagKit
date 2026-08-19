import os
import socket

from console_utils import run_visible


def _windows_only():
    if os.name == "nt":
        return True
    print("This function is intended for Windows.")
    return False


def show_ipconfig():
    if _windows_only():
        run_visible(["ipconfig", "/all"])


def resolve_addresses(host):
    print(f"\nDNS resolution for: {host}")
    print("A/AAAA results do not prove which IP family reached the DNS resolver.\n")

    for family, label in ((socket.AF_INET, "IPv4 / A"), (socket.AF_INET6, "IPv6 / AAAA")):
        try:
            entries = socket.getaddrinfo(host, None, family, socket.SOCK_STREAM)
            addresses = sorted({entry[4][0] for entry in entries})
            print(f"{label}:")
            for address in addresses:
                print(f"  {address}")
        except socket.gaierror as exc:
            print(f"{label}: resolution failed ({exc})")


def ping_test(host):
    if not _windows_only():
        return

    print(f"\nIPv4 connectivity: {host}")
    run_visible(["ping", "-4", "-n", "4", host])

    print(f"\nIPv6 connectivity: {host}")
    run_visible(["ping", "-6", "-n", "4", host])


def traceroute_test(host):
    if not _windows_only():
        return

    print(f"\nIPv4 route trace: {host}")
    run_visible(["tracert", "-4", "-d", host])

    print(f"\nIPv6 route trace: {host}")
    run_visible(["tracert", "-6", "-d", host])
