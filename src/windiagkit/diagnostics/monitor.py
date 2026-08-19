from contextlib import suppress
from os import name as os_name
from os import path
from shutil import which
from time import monotonic, sleep, strftime

from psutil import cpu_freq, cpu_percent, net_io_counters, virtual_memory

from ..cli.console import APP_NAME, clear_screen, hidden_output
from ..powershell.powershell_runner import PowerShellRunner

_POWERSHELL_RUNNER = PowerShellRunner()


def human_bytes(value):
    value = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(value) < 1024.0:
            return f"{value:5.1f} {unit}"
        value /= 1024.0
    return f"{value:.1f} PB"


def find_nvidia_smi():
    nvidia_path = which("nvidia-smi")
    if nvidia_path:
        return nvidia_path

    for candidate in (
        r"C:\Windows\System32\nvidia-smi.exe",
        r"C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe",
    ):
        if path.exists(candidate):
            return candidate
    return None


def read_nvidia_gpu(nvidia_smi, timeout=3.0):
    if not nvidia_smi:
        return []

    output = hidden_output(
        [
            nvidia_smi,
            "--query-gpu=name,utilization.gpu,temperature.gpu,memory.used,memory.total",
            "--format=csv,noheader,nounits",
        ],
        timeout=timeout,
    )

    gpus = []
    for line in output.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 5:
            continue
        name, util, temp, mem_used, mem_total = parts
        gpus.append((name, util, temp, mem_used, mem_total))
    return gpus


def read_acpi_temperatures(timeout=4.0):
    """Best-effort ACPI thermal zones; these are not guaranteed CPU package temps."""
    if os_name != "nt":
        return []

    try:
        script = _POWERSHELL_RUNNER.script_loader.load("acpi_temperatures.ps1", {})
    except RuntimeError:
        return []

    output = hidden_output(_POWERSHELL_RUNNER.command(script), timeout=timeout)

    values = []
    for line in output.splitlines():
        with suppress(ValueError):
            values.append(float(line.strip().replace(",", ".")))
    return values


def _stop_requested():
    if os_name != "nt":
        return False

    import msvcrt

    while msvcrt.kbhit():
        key = msvcrt.getch()
        if key in (b"q", b"Q", b"\x1b"):
            return True
    return False


def monitor(settings):
    nvidia_smi = find_nvidia_smi()
    previous_net = net_io_counters()
    previous_time = monotonic()

    cpu_percent(interval=None)
    sleep(settings.sample_seconds)

    acpi_temps = []
    next_acpi_refresh = 0.0

    try:
        while True:
            loop_started = monotonic()
            now = loop_started

            cpu = cpu_percent(interval=None)
            memory = virtual_memory()
            net = net_io_counters()

            elapsed = max(now - previous_time, 0.001)
            rx_rate = (net.bytes_recv - previous_net.bytes_recv) / elapsed
            tx_rate = (net.bytes_sent - previous_net.bytes_sent) / elapsed
            previous_net = net
            previous_time = now

            if now >= next_acpi_refresh:
                acpi_temps = read_acpi_temperatures(settings.helper_timeout_seconds)
                next_acpi_refresh = now + settings.acpi_refresh_seconds

            clear_screen()
            print(f"{APP_NAME} | Live System Monitor")
            print(strftime("%Y-%m-%d %H:%M:%S"))
            print("=" * 72)
            print(f"CPU : {cpu:5.1f} %")

            freq = cpu_freq()
            if freq and freq.current:
                print(f"Clock: {freq.current:7.0f} MHz")

            print(
                f"RAM : {memory.percent:5.1f} %  "
                f"({human_bytes(memory.used)} / {human_bytes(memory.total)})"
            )
            print(f"NET : RX {human_bytes(rx_rate)}/s   TX {human_bytes(tx_rate)}/s")

            if acpi_temps:
                print("TEMP: ACPI " + ", ".join(f"{temp:.1f} C" for temp in acpi_temps))
            else:
                print("TEMP: ACPI thermal zones unavailable")

            gpus = read_nvidia_gpu(nvidia_smi, settings.helper_timeout_seconds)
            if gpus:
                for index, (gpu_name, util, temp, used, total) in enumerate(gpus):
                    print(
                        f"GPU{index}: {util:>3} %  {temp:>3} C  "
                        f"VRAM {used}/{total} MiB  {gpu_name}"
                    )
            else:
                print("GPU : NVIDIA metrics unavailable")

            print("=" * 72)
            if os_name == "nt":
                print(
                    "Q / Esc: return to main menu | Read-only | No diagnostic logging"
                )
            else:
                print("Ctrl+C: return to main menu | Read-only | No diagnostic logging")

            end_at = loop_started + settings.sample_seconds
            while monotonic() < end_at:
                if _stop_requested():
                    return
                sleep(0.05)

    except KeyboardInterrupt:
        return
