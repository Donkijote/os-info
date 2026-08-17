from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from hwscan.domain.models import InventoryReport


def default_schema_path() -> Path:
    return Path(__file__).resolve().parents[4] / "schema" / "inventory-v1.0.0.schema.json"


def validate_report(data: dict[str, Any], schema_path: Path | None = None) -> None:
    selected = schema_path or default_schema_path()
    schema = json.loads(selected.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(data), key=lambda error: list(error.absolute_path))
    if errors:
        details = "; ".join(
            f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
            for error in errors
        )
        raise ValueError(f"report does not match schema: {details}")


def write_json(report: InventoryReport, path: Path, schema_path: Path | None = None) -> None:
    report.validate_basic()
    data = report.as_dict()
    validate_report(data, schema_path)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
