import unittest

from windiagkit.diagnostics.job_catalog import JobCatalog
from windiagkit.settings import Settings


class GuiJobTests(unittest.TestCase):
    def setUp(self):
        self.settings = Settings(
            diagnostic_process_names=("Load App", "O'Brien"), top_process_count=10
        )
        self.catalog = JobCatalog()

    def test_job_keys_are_unique(self):
        keys = [job.key for job in self.catalog.jobs]
        self.assertEqual(len(keys), len(set(keys)))

    def test_object_catalog_exposes_and_builds_jobs(self):
        self.assertEqual(self.catalog.get("ping").title, "IPv4 and IPv6 ping")
        self.assertEqual(len(self.catalog.build_commands("ipconfig", self.settings)), 1)

    def test_every_catalog_job_builds_commands(self):
        for job in self.catalog.jobs:
            with self.subTest(job=job.key):
                commands = self.catalog.build_commands(
                    job.key,
                    self.settings,
                    target="host.example",
                    minutes=15,
                )
                self.assertTrue(commands)
                self.assertTrue(
                    all(command.timeout_seconds > 0 for command in commands)
                )

    def test_checkpoint_contains_four_focused_commands(self):
        commands = self.catalog.build_commands("checkpoint", self.settings, minutes=30)

        self.assertEqual(len(commands), 4)
        self.assertEqual(commands[0].display, "PowerShell · system_resources.ps1")
        self.assertEqual(commands[-1].display, "PowerShell · load_test_events.ps1")
        self.assertNotIn("Get-WinEvent", commands[-1].display)

    def test_process_targets_are_separate_arguments(self):
        command = self.catalog.build_commands("process_snapshot", self.settings)[0]

        names_index = command.command.index("-ProcessNamesCsv")
        count_index = command.command.index("-TopCount")
        self.assertEqual(command.command[names_index + 1], "Load App,O'Brien")
        self.assertEqual(command.command[count_index + 1], "10")
        self.assertIn("-File", command.command)
        self.assertNotIn("-Command", command.command)

    def test_operational_log_uses_known_log_name(self):
        command = self.catalog.build_commands("dns_events", self.settings, minutes=15)[
            0
        ]

        log_index = command.command.index("-LogName")
        self.assertEqual(
            command.command[log_index + 1],
            "Microsoft-Windows-DNS-Client/Operational",
        )

    def test_ping_is_an_argument_list_for_both_families(self):
        commands = self.catalog.build_commands(
            "ping", self.settings, target="host.example"
        )

        self.assertEqual(commands[0].command[0:3], ("ping", "-4", "-n"))
        self.assertEqual(commands[1].command[0:3], ("ping", "-6", "-n"))
        self.assertEqual(commands[0].command[-1], "host.example")

    def test_invalid_target_and_job_are_rejected(self):
        with self.assertRaises(ValueError):
            self.catalog.build_commands("ping", self.settings, target="invalid target")
        with self.assertRaises(ValueError):
            self.catalog.build_commands("unknown", self.settings)


if __name__ == "__main__":
    unittest.main()
