from pathlib import Path

import pytest

from hwscan.domain.models import CollectionStatus
from hwscan.infrastructure.command_runner import CommandRunner, CommandSpec


def _script(path: Path, body: str) -> Path:
    path.write_text("#!/bin/sh\n" + body, encoding="utf-8")
    path.chmod(0o755)
    return path


def test_requires_absolute_executable() -> None:
    with pytest.raises(ValueError, match="absolute"):
        CommandSpec("bad", ("echo", "hello"))


def test_captures_success_and_nonzero_exit(tmp_path: Path) -> None:
    success = _script(tmp_path / "success", "printf 'hello'")
    result = CommandRunner().run(CommandSpec("test", (str(success),)))
    assert result.status is CollectionStatus.OK
    assert result.stdout == "hello"

    failure = _script(tmp_path / "failure", "printf 'problem' >&2\nexit 7")
    result = CommandRunner().run(CommandSpec("test", (str(failure),)))
    assert result.status is CollectionStatus.NONZERO_EXIT
    assert result.exit_code == 7
    assert result.stderr == "problem"


def test_times_out_and_limits_output(tmp_path: Path) -> None:
    slow = _script(tmp_path / "slow", "sleep 2")
    result = CommandRunner().run(CommandSpec("slow", (str(slow),), timeout_seconds=0.1))
    assert result.status is CollectionStatus.TIMED_OUT
    assert result.timed_out

    noisy = _script(tmp_path / "noisy", "yes x")
    result = CommandRunner().run(CommandSpec("noisy", (str(noisy),), max_output_bytes=1024))
    assert result.status is CollectionStatus.OVERSIZED_OUTPUT


def test_reports_missing_executable(tmp_path: Path) -> None:
    result = CommandRunner().run(CommandSpec("missing", (str(tmp_path / "missing"),)))
    assert result.status is CollectionStatus.MISSING_EXECUTABLE
