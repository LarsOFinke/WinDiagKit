from . import __version__
from .console_utils import APP_NAME, clear_screen, pause
from .event_logs import (
    show_dns_log,
    show_network_profile_log,
    show_system_warnings_errors,
    show_wlan_log,
)
from .network_tools import ping_test, resolve_addresses, show_ipconfig, traceroute_test
from .system_monitor import monitor


def header(title):
    clear_screen()
    print(f"{APP_NAME} {__version__} - {title}")
    print("=" * 58)


def network_menu(settings):
    target = settings.default_target

    while True:
        header("Network Troubleshooting")
        print(f"Current target: {target}\n")
        print("[1] Change target")
        print("[2] IPv4 / IPv6 ping")
        print("[3] IPv4 / IPv6 traceroute")
        print("[4] DNS A / AAAA resolution")
        print("[5] Show ipconfig /all")
        print("\n[0] Back")

        choice = input("\nSelect: ").strip()

        if choice == "0":
            return
        if choice == "1":
            value = input(f"Target [{target}]: ").strip()
            if value:
                target = value
        elif choice == "2":
            ping_test(
                target,
                count=settings.ping_count,
                timeout_ms=settings.ping_timeout_ms,
                command_timeout=settings.command_timeout_seconds,
            )
            pause()
        elif choice == "3":
            traceroute_test(
                target,
                max_hops=settings.traceroute_max_hops,
                timeout_ms=settings.traceroute_timeout_ms,
                command_timeout=settings.command_timeout_seconds,
            )
            pause()
        elif choice == "4":
            resolve_addresses(target)
            pause()
        elif choice == "5":
            show_ipconfig(settings.command_timeout_seconds)
            pause()


def event_log_menu(settings):
    minutes = settings.event_window_minutes

    while True:
        header("Windows Event Logs")
        print(f"Time window: last {minutes} minute(s)")
        print("Read-only: logs are displayed only; nothing is exported.\n")
        print("[1] DNS Client / Operational")
        print("[2] NetworkProfile / Operational")
        print("[3] WLAN AutoConfig / Operational")
        print("[4] System warnings / errors")
        print("[5] Change time window")
        print("\n[0] Back")

        choice = input("\nSelect: ").strip()

        if choice == "0":
            return
        if choice == "1":
            show_dns_log(
                minutes, settings.max_events, settings.event_query_timeout_seconds
            )
            pause()
        elif choice == "2":
            show_network_profile_log(
                minutes, settings.max_events, settings.event_query_timeout_seconds
            )
            pause()
        elif choice == "3":
            show_wlan_log(
                minutes, settings.max_events, settings.event_query_timeout_seconds
            )
            pause()
        elif choice == "4":
            show_system_warnings_errors(
                minutes, settings.max_events, settings.event_query_timeout_seconds
            )
            pause()
        elif choice == "5":
            choices = "/".join(str(value) for value in settings.event_window_choices)
            value = input(f"Minutes [{choices}]: ").strip()
            if value in {str(item) for item in settings.event_window_choices}:
                minutes = int(value)


def main_menu(settings):
    while True:
        header("Main Menu")
        print("Read-only troubleshooting helper")
        print("No diagnostic data is saved by WinDiagKit.\n")
        print("[1] Live system monitor")
        print("[2] Network troubleshooting")
        print("[3] Windows Event Logs")
        print("[4] Show ipconfig /all")
        print("\n[0] Exit")

        choice = input("\nSelect: ").strip()

        if choice == "0":
            return
        if choice == "1":
            monitor(settings)
        elif choice == "2":
            network_menu(settings)
        elif choice == "3":
            event_log_menu(settings)
        elif choice == "4":
            show_ipconfig(settings.command_timeout_seconds)
            pause()
