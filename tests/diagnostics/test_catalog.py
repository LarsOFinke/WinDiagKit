import unittest

from windiagkit.diagnostics.catalog import JOBS, build_job_commands
from windiagkit.diagnostics.job_catalog import JobCatalog
from windiagkit.settings import Settings


class GuiJobTests(unittest.TestCase):
    def setUp(self):
        self.settings = Settings(
            diagnostic_process_names=("Load App", "O'Brien"), top_process_count=10
        )

    def test_job_keys_are_unique(self):
        keys = [job.key for job in JOBS]
        self.assertEqual(len(keys), len(set(keys)))

    def test_object_catalog_exposes_and_builds_jobs(self):
        catalog = JobCatalog()

        self.assertEqual(catalog.get("ping").title, "IPv4 and IPv6 ping")
        self.assertEqual(len(catalog.jobs), len(JOBS))
        self.assertEqual(len(catalog.build_commands("ipconfig", self.settings)), 1)

    def test_every_catalog_job_builds_commands(self):
        for job in JOBS:
            with self.subTest(job=job.key):
                commands = build_job_commands(
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
        commands = build_job_commands("checkpoint", self.settings, minutes=30)

        self.assertEqual(len(commands), 4)
        self.assertEqual(commands[0].display, "PowerShell · system_resources.ps1")
        self.assertEqual(commands[-1].display, "PowerShell · load_test_events.ps1")
        self.assertNotIn("Get-WinEvent", commands[-1].display)

    def test_process_targets_are_safely_encoded(self):
        command = build_job_commands("process_snapshot", self.settings)[0]
        script = command.command[-1]

        self.assertIn("@('Load App', 'O''Brien')", script)
        self.assertIn("$topCount = 10", script)

    def test_operational_log_uses_known_log_name(self):
        command = build_job_commands("dns_events", self.settings, minutes=15)[0]

        self.assertIn("Microsoft-Windows-DNS-Client/Operational", command.command[-1])
        self.assertNotIn("__LOG_NAME__", command.command[-1])

    def test_ping_is_an_argument_list_for_both_families(self):
        commands = build_job_commands("ping", self.settings, target="host.example")

        self.assertEqual(commands[0].command[0:3], ("ping", "-4", "-n"))
        self.assertEqual(commands[1].command[0:3], ("ping", "-6", "-n"))
        self.assertEqual(commands[0].command[-1], "host.example")

    def test_invalid_target_and_job_are_rejected(self):
        with self.assertRaises(ValueError):
            build_job_commands("ping", self.settings, target="invalid target")
        with self.assertRaises(ValueError):
            build_job_commands("unknown", self.settings)


if __name__ == "__main__":
    unittest.main()
