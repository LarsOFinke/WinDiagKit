import unittest
from types import SimpleNamespace
from unittest.mock import patch

from windiagkit.diagnostics.monitor import (
    human_bytes,
    monitor,
    read_acpi_temperatures,
    read_nvidia_gpu,
)
from windiagkit.settings import Settings


class SystemMonitorTests(unittest.TestCase):
    def test_human_bytes(self):
        self.assertEqual(human_bytes(0), "  0.0 B")
        self.assertEqual(human_bytes(1024), "  1.0 KB")
        self.assertEqual(human_bytes(1024 * 1024), "  1.0 MB")

    @patch("windiagkit.diagnostics.monitor.hidden_output")
    def test_parses_multiple_nvidia_gpus(self, hidden):
        hidden.return_value = (
            "GPU One, 25, 50, 100, 1000\nmalformed\nGPU Two, 5, 40, 200, 2000"
        )

        result = read_nvidia_gpu("nvidia-smi", timeout=7)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], "GPU One")
        self.assertEqual(result[1][3], "200")
        self.assertEqual(hidden.call_args.kwargs["timeout"], 7)

    @patch("windiagkit.diagnostics.monitor.os_name", "nt")
    @patch(
        "windiagkit.diagnostics.monitor._POWERSHELL_RUNNER.script_loader.load",
        return_value="ACPI query",
    )
    @patch("windiagkit.diagnostics.monitor.hidden_output", return_value="42.5\n38,0")
    def test_acpi_query_loads_script_on_windows(self, hidden, load_script):
        temperatures = read_acpi_temperatures(timeout=6)

        self.assertEqual(temperatures, [42.5, 38.0])
        load_script.assert_called_once_with("acpi_temperatures.ps1", {})
        self.assertEqual(hidden.call_args.args[0][-1], "ACPI query")
        self.assertEqual(hidden.call_args.kwargs["timeout"], 6)

    @patch("windiagkit.diagnostics.monitor.os_name", "nt")
    @patch(
        "windiagkit.diagnostics.monitor._POWERSHELL_RUNNER.script_loader.load",
        side_effect=RuntimeError,
    )
    def test_acpi_query_tolerates_missing_script(self, load_script):
        self.assertEqual(read_acpi_temperatures(), [])

    @patch("windiagkit.diagnostics.monitor.print")
    @patch("windiagkit.diagnostics.monitor.clear_screen")
    @patch("windiagkit.diagnostics.monitor.read_nvidia_gpu", return_value=[])
    @patch("windiagkit.diagnostics.monitor.read_acpi_temperatures", return_value=[])
    @patch("windiagkit.diagnostics.monitor.cpu_freq", return_value=None)
    @patch("windiagkit.diagnostics.monitor.virtual_memory")
    @patch("windiagkit.diagnostics.monitor.cpu_percent", return_value=10.0)
    @patch("windiagkit.diagnostics.monitor.net_io_counters")
    @patch("windiagkit.diagnostics.monitor.sleep")
    @patch("windiagkit.diagnostics.monitor.monotonic")
    def test_monitor_handles_unavailable_gpu_metrics(
        self,
        monotonic,
        sleep,
        net_io_counters,
        cpu_percent,
        virtual_memory,
        cpu_freq,
        read_acpi,
        read_gpu,
        clear_screen,
        output,
    ):
        monotonic.side_effect = [0.0, 1.0, 2.0, KeyboardInterrupt]
        net_io_counters.side_effect = [
            SimpleNamespace(bytes_recv=100, bytes_sent=50),
            SimpleNamespace(bytes_recv=200, bytes_sent=100),
        ]
        virtual_memory.return_value = SimpleNamespace(
            percent=50.0, used=1024, total=2048
        )

        monitor(Settings())

        read_gpu.assert_called_once_with(None, 4.0)
        self.assertTrue(
            any(
                call.args == ("GPU : NVIDIA metrics unavailable",)
                for call in output.call_args_list
            )
        )


if __name__ == "__main__":
    unittest.main()
