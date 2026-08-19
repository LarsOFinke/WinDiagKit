import unittest
from unittest.mock import call, patch

from windiagkit import network_tools


class NetworkCommandTests(unittest.TestCase):
    @patch("windiagkit.network_tools.run_visible")
    @patch("windiagkit.network_tools.name", "nt")
    def test_ping_has_family_and_time_limits(self, run):
        network_tools.ping_test("host.example", 2, 500, 10)

        self.assertEqual(
            run.call_args_list,
            [
                call(
                    ["ping", "-4", "-n", "2", "-w", "500", "host.example"],
                    timeout=10,
                ),
                call(
                    ["ping", "-6", "-n", "2", "-w", "500", "host.example"],
                    timeout=10,
                ),
            ],
        )

    @patch("windiagkit.network_tools.run_visible")
    @patch("windiagkit.network_tools.name", "nt")
    def test_traceroute_has_hop_and_time_limits(self, run):
        network_tools.traceroute_test("host.example", 12, 750, 20)

        self.assertEqual(run.call_count, 2)
        self.assertEqual(
            run.call_args_list[0],
            call(
                [
                    "tracert", "-4", "-d", "-h", "12", "-w", "750",
                    "host.example",
                ],
                timeout=20,
            ),
        )


if __name__ == "__main__":
    unittest.main()
