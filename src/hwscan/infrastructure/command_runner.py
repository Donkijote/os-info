from __future__ import annotations

import hashlib
import os
import selectors
import signal
import subprocess
import time
from collections.abc import Mapping
from contextlib import suppress
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from hwscan.domain.models import CollectionStatus, SourceRecord


@dataclass(frozen=True, slots=True)
class CommandSpec:
    name: str
    argv: tuple[str, ...]
    timeout_seconds: float = 15.0
    max_output_bytes: int = 4 * 1024 * 1024

    def __post_init__(self) -> None:
        if not self.argv:
            raise ValueError("argv must not be empty")
        if not Path(self.argv[0]).is_absolute():
            raise ValueError("executable path must be absolute")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.max_output_bytes <= 0:
            raise ValueError("max_output_bytes must be positive")


@dataclass(frozen=True, slots=True)
class CommandResult:
    spec: CommandSpec
    status: CollectionStatus
    stdout: str
    stderr: str
    exit_code: int | None
    duration_ms: int
    started_at: str
    timed_out: bool = False

    def source_record(self, *, source_id: str, tool_version: str | None = None) -> SourceRecord:
        digest = hashlib.sha256(self.stdout.encode("utf-8")).hexdigest() if self.stdout else None
        return SourceRecord(
            id=source_id,
            collector=self.spec.name,
            tool=Path(self.spec.argv[0]).name,
            tool_version=tool_version,
            status=self.status,
            exit_code=self.exit_code,
            duration_ms=self.duration_ms,
            started_at=self.started_at,
            timed_out=self.timed_out,
            stderr_excerpt=self.stderr[:2048] or None,
            raw_sha256=digest,
        )


class CommandRunner:
    def __init__(self, *, path: str = "/usr/sbin:/usr/bin:/sbin:/bin") -> None:
        self._environment: Mapping[str, str] = {
            "LC_ALL": "C",
            "LANG": "C",
            "PATH": path,
        }

    def run(self, spec: CommandSpec) -> CommandResult:
        started = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        started_monotonic = time.monotonic()
        try:
            process = subprocess.Popen(
                spec.argv,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=dict(self._environment),
                cwd="/",
                start_new_session=True,
            )
        except FileNotFoundError:
            return self._failure(
                spec, CollectionStatus.MISSING_EXECUTABLE, started, started_monotonic
            )
        except PermissionError:
            return self._failure(
                spec, CollectionStatus.PERMISSION_DENIED, started, started_monotonic
            )

        assert process.stdout is not None
        assert process.stderr is not None
        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ, "stdout")
        selector.register(process.stderr, selectors.EVENT_READ, "stderr")
        output = {"stdout": bytearray(), "stderr": bytearray()}
        deadline = started_monotonic + spec.timeout_seconds
        timed_out = False
        oversized = False

        try:
            while selector.get_map():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    timed_out = True
                    self._terminate(process)
                    break
                events = selector.select(timeout=min(0.1, remaining))
                if not events and process.poll() is not None:
                    events = [(key, selectors.EVENT_READ) for key in selector.get_map().values()]
                for key, _ in events:
                    chunk = os.read(key.fd, 65536)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    output[key.data].extend(chunk)
                    if sum(len(value) for value in output.values()) > spec.max_output_bytes:
                        oversized = True
                        self._terminate(process)
                        break
                if oversized:
                    break
        finally:
            selector.close()
            process.stdout.close()
            process.stderr.close()

        if process.poll() is None:
            self._terminate(process)
        exit_code = process.wait()
        duration_ms = round((time.monotonic() - started_monotonic) * 1000)
        stdout = bytes(output["stdout"][: spec.max_output_bytes]).decode("utf-8", errors="replace")
        stderr = bytes(output["stderr"][: spec.max_output_bytes]).decode("utf-8", errors="replace")
        if timed_out:
            status = CollectionStatus.TIMED_OUT
        elif oversized:
            status = CollectionStatus.OVERSIZED_OUTPUT
        elif exit_code == 0:
            status = CollectionStatus.OK
        else:
            status = CollectionStatus.NONZERO_EXIT
        return CommandResult(
            spec=spec,
            status=status,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            duration_ms=duration_ms,
            started_at=started,
            timed_out=timed_out,
        )

    @staticmethod
    def _terminate(process: subprocess.Popen[bytes]) -> None:
        if process.poll() is not None:
            return
        try:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=0.5)
        except (ProcessLookupError, subprocess.TimeoutExpired):
            with suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGKILL)

    @staticmethod
    def _failure(
        spec: CommandSpec,
        status: CollectionStatus,
        started_at: str,
        started_monotonic: float,
    ) -> CommandResult:
        return CommandResult(
            spec=spec,
            status=status,
            stdout="",
            stderr="",
            exit_code=None,
            duration_ms=round((time.monotonic() - started_monotonic) * 1000),
            started_at=started_at,
        )
