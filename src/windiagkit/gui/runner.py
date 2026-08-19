from locale import getpreferredencoding

from PyQt5.QtCore import QObject, QProcess, QTimer, pyqtSignal


class JobRunner(QObject):
    output_ready = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    busy_changed = pyqtSignal(bool)
    finished = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._commands = []
        self._index = 0
        self._issues = 0
        self._cancelled = False
        self._completing = False
        self._current_issue = False

        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.MergedChannels)
        self._process.readyReadStandardOutput.connect(self._read_output)
        self._process.finished.connect(self._process_finished)
        self._process.errorOccurred.connect(self._process_error)

        self._timeout = QTimer(self)
        self._timeout.setSingleShot(True)
        self._timeout.timeout.connect(self._timed_out)

    @property
    def busy(self):
        return bool(self._commands)

    def start(self, commands):
        if self.busy:
            raise RuntimeError("A diagnostic job is already running")
        if not commands:
            raise ValueError("A diagnostic job must contain at least one command")

        self._commands = list(commands)
        self._index = 0
        self._issues = 0
        self._cancelled = False
        self.busy_changed.emit(True)
        self._start_current()

    def cancel(self):
        if not self.busy:
            return
        self._cancelled = True
        self.status_changed.emit("Cancelling…")
        self.output_ready.emit("\n[WARNING] Cancellation requested.\n")
        self._process.terminate()
        QTimer.singleShot(1500, self._kill_if_running)

    def shutdown(self):
        if not self.busy:
            return
        self._cancelled = True
        self._timeout.stop()
        if self._process.state() != QProcess.NotRunning:
            self._process.kill()
            self._process.waitForFinished(1000)
        self._finish(False, "Cancelled")

    def _start_current(self):
        if self._cancelled:
            self._finish(False, "Cancelled")
            return
        command = self._commands[self._index]
        self._current_issue = False
        self._completing = False
        self.status_changed.emit(
            f"Running {self._index + 1} of {len(self._commands)}: {command.title}"
        )
        self.output_ready.emit(
            f"\n{'=' * 72}\n{command.title}\n> {command.display}\n{'=' * 72}\n"
        )
        self._process.setProgram(command.command[0])
        self._process.setArguments(list(command.command[1:]))
        self._timeout.start(max(1, int(command.timeout_seconds * 1000)))
        self._process.start()

    def _read_output(self):
        data = bytes(self._process.readAllStandardOutput())
        if data:
            encoding = getpreferredencoding(False) or "utf-8"
            self.output_ready.emit(data.decode(encoding, errors="replace"))

    def _process_finished(self, exit_code, exit_status):
        self._read_output()
        failed = exit_status == QProcess.CrashExit or exit_code != 0
        self._complete_current(failed)

    def _process_error(self, error):
        if error != QProcess.FailedToStart or self._completing:
            return
        self.output_ready.emit(
            f"[ERROR] Could not start {self._process.program()}: "
            f"{self._process.errorString()}\n"
        )
        QTimer.singleShot(0, lambda: self._complete_current(True))

    def _timed_out(self):
        self._current_issue = True
        self.output_ready.emit("\n[ERROR] Command timed out; stopping it safely.\n")
        self._process.terminate()
        QTimer.singleShot(1500, self._kill_if_running)

    def _kill_if_running(self):
        if self._process.state() != QProcess.NotRunning:
            self._process.kill()

    def _complete_current(self, failed):
        if self._completing or not self.busy:
            return
        self._completing = True
        self._timeout.stop()

        if self._cancelled:
            self.output_ready.emit("[WARNING] Command cancelled.\n")
            self._finish(False, "Cancelled")
            return

        if failed or self._current_issue:
            self._issues += 1
            self.output_ready.emit("[WARNING] This command completed with an issue.\n")
        else:
            self.output_ready.emit("[OK] Command completed.\n")

        self._index += 1
        if self._index < len(self._commands):
            QTimer.singleShot(0, self._start_current)
            return

        successful = self._issues == 0
        status = (
            "Completed" if successful else f"Completed with {self._issues} issue(s)"
        )
        self._finish(successful, status)

    def _finish(self, successful, status):
        if not self.busy:
            return
        self._timeout.stop()
        self._commands = []
        self.status_changed.emit(status)
        self.busy_changed.emit(False)
        self.finished.emit(successful)
