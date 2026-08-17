from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, cast
from uuid import UUID, uuid4


class CollectionStatus(StrEnum):
    OK = "ok"
    UNKNOWN = "unknown"
    UNSUPPORTED = "unsupported"
    MISSING_EXECUTABLE = "missing_executable"
    PERMISSION_DENIED = "permission_denied"
    TIMED_OUT = "timed_out"
    OVERSIZED_OUTPUT = "oversized_output"
    NONZERO_EXIT = "nonzero_exit"
    PARSE_ERROR = "parse_error"


class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(slots=True)
class ScannerInfo:
    app_version: str
    image_build_id: str
    os: str
    kernel: str
    architecture: str


@dataclass(slots=True)
class OperatorInput:
    asset_tag: str | None = None
    operator: str | None = None
    location: str | None = None
    notes: str | None = None


@dataclass(slots=True)
class Diagnostic:
    severity: Severity
    domain: str
    code: str
    message: str
    device_ref: str | None = None
    source_ref: str | None = None


@dataclass(slots=True)
class SourceRecord:
    id: str
    collector: str
    tool: str
    tool_version: str | None
    status: CollectionStatus
    exit_code: int | None
    duration_ms: int
    started_at: str
    timed_out: bool = False
    stderr_excerpt: str | None = None
    raw_sha256: str | None = None


@dataclass(slots=True)
class InventoryReport:
    schema_version: str
    report_id: str
    created_at: str
    scanner: ScannerInfo
    operator_input: OperatorInput = field(default_factory=OperatorInput)
    boot: dict[str, Any] = field(default_factory=dict)
    system: dict[str, Any] = field(default_factory=dict)
    cpus: list[dict[str, Any]] = field(default_factory=list)
    memory: dict[str, Any] = field(default_factory=dict)
    storage: list[dict[str, Any]] = field(default_factory=list)
    graphics: list[dict[str, Any]] = field(default_factory=list)
    network: list[dict[str, Any]] = field(default_factory=list)
    batteries: list[dict[str, Any]] = field(default_factory=list)
    displays: list[dict[str, Any]] = field(default_factory=list)
    audio: list[dict[str, Any]] = field(default_factory=list)
    usb_devices: list[dict[str, Any]] = field(default_factory=list)
    security: dict[str, Any] = field(default_factory=dict)
    sensors: list[dict[str, Any]] = field(default_factory=list)
    diagnostics: list[Diagnostic] = field(default_factory=list)
    sources: list[SourceRecord] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return cast(dict[str, Any], _json_value(asdict(self)))

    def validate_basic(self) -> None:
        UUID(self.report_id)
        parsed = datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("created_at must include a timezone")
        if not self.schema_version:
            raise ValueError("schema_version is required")


def new_report(scanner: ScannerInfo, *, schema_version: str = "1.0.0") -> InventoryReport:
    created_at = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return InventoryReport(
        schema_version=schema_version,
        report_id=str(uuid4()),
        created_at=created_at,
        scanner=scanner,
    )


def _json_value(value: Any) -> Any:
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    return value
