"""Object-oriented access to diagnostic job metadata and commands."""

from .catalog import JOBS, build_job_commands


class JobCatalog:
    def __init__(self):
        self._jobs = JOBS
        self._jobs_by_key = {job.key: job for job in self._jobs}

    @property
    def jobs(self):
        return self._jobs

    def get(self, key):
        return self._jobs_by_key.get(key)

    def build_commands(self, key, settings, target=None, minutes=None):
        if key not in self._jobs_by_key:
            raise ValueError(f"Unknown diagnostic job: {key}")
        return build_job_commands(key, settings, target=target, minutes=minutes)
