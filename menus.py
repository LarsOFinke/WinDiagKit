from console_utils import APP_NAME, clear_screen, pause
from event_logs import (
    show_dns_log,
    show_network_profile_log,
    show_system_warnings_errors,
    show_wlan_log,
)
from network_tools import ping_test, resolve_addresses, show_ipconfig, traceroute_test
from system_monitor import monitor


DEFAULT_TARGET = "example.com"
DEFAULT_EVENT_WINDOW = 15


def header(title):
    clear_screen()
    print(f"{APP_NAME} - {title}")
    print("=" * 58)


def network_menu():
    target = DEFAULT_TARGET

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
            ping_test(target)
            pause()
        elif choice == "3":
            traceroute_test(target)
            pause()
        elif choice == "4":
            resolve_addresses(target)
            pause()
        elif choice == "5":
            show_ipconfig()
            pause()


def event_log_menu():
    minutes = DEFAULT_EVENT_WINDOW

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
            show_dns_log(minutes)
            pause()
        elif choice == "2":
            show_network_profile_log(minutes)
            pause()
        elif choice == "3":
            show_wlan_log(minutes)
            pause()
        elif choice == "4":
            show_system_warnings_errors(minutes)
            pause()
        elif choice == "5":
            value = input("Minutes [5/15/30/60]: ").strip()
            if value in {"5", "15", "30", "60"}:
                minutes = int(value)


def main_menu():
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
            monitor()
        elif choice == "2":
            network_menu()
        elif choice == "3":
            event_log_menu()
        elif choice == "4":
            show_ipconfig()
            pause()
