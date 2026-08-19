import unittest
from unittest.mock import call, patch

from windiagkit.diagnostics import network


class NetworkCommandTests(unittest.TestCase):
    @patch("windiagkit.diagnostics.network.run_visible")
    @patch("windiagkit.diagnostics.network.name", "nt")
    def test_ping_has_family_and_time_limits(self, run):
        network.ping_test("host.example", 2, 500, 10)

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

    @patch("windiagkit.diagnostics.network.run_visible")
    @patch("windiagkit.diagnostics.network.name", "nt")
    def test_traceroute_has_hop_and_time_limits(self, run):
        network.traceroute_test("host.example", 12, 750, 20)

        self.assertEqual(run.call_count, 2)
        self.assertEqual(
            run.call_args_list[0],
            call(
                [
                    "tracert",
                    "-4",
                    "-d",
                    "-h",
                    "12",
                    "-w",
                    "750",
                    "host.example",
                ],
                timeout=20,
            ),
        )


if __name__ == "__main__":
    unittest.main()
