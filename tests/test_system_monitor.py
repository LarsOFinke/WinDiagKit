import unittest
from unittest.mock import patch

from windiagkit.system_monitor import human_bytes, read_nvidia_gpu


class SystemMonitorTests(unittest.TestCase):
    def test_human_bytes(self):
        self.assertEqual(human_bytes(0), "  0.0 B")
        self.assertEqual(human_bytes(1024), "  1.0 KB")
        self.assertEqual(human_bytes(1024 * 1024), "  1.0 MB")

    @patch("windiagkit.system_monitor.hidden_output")
    def test_parses_multiple_nvidia_gpus(self, hidden):
        hidden.return_value = (
            "GPU One, 25, 50, 100, 1000\n"
            "malformed\n"
            "GPU Two, 5, 40, 200, 2000"
        )

        result = read_nvidia_gpu("nvidia-smi", timeout=7)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], "GPU One")
        self.assertEqual(result[1][3], "200")
        self.assertEqual(hidden.call_args.kwargs["timeout"], 7)


if __name__ == "__main__":
    unittest.main()
