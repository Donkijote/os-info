from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from hwscan.domain.models import InventoryReport
from hwscan.domain.normalization import safe_filename_component
from hwscan.infrastructure.exporters.excel_exporter import validate_workbook, write_excel
from hwscan.infrastructure.exporters.json_exporter import validate_report, write_json


@dataclass(frozen=True, slots=True)
class ExportResult:
    json_path: Path
    excel_path: Path
    manifest_path: Path


class ExportService:
    def export(self, report: InventoryReport, destination: Path) -> ExportResult:
        destination.mkdir(parents=True, exist_ok=True)
        stem = self._stem(report)
        final_json = destination / f"{stem}.json"
        final_excel = destination / f"{stem}.xlsx"
        final_manifest = destination / f"{stem}.manifest.json"
        temporary: list[Path] = []
        try:
            temp_json = self._temporary(destination, ".json")
            temp_excel = self._temporary(destination, ".xlsx")
            temporary.extend([temp_json, temp_excel])
            write_json(report, temp_json)
            write_excel(report, temp_excel)
            validate_report(json.loads(temp_json.read_text(encoding="utf-8")))
            validate_workbook(temp_excel)
            self._sync_file(temp_json)
            self._sync_file(temp_excel)
            os.replace(temp_json, final_json)
            os.replace(temp_excel, final_excel)
            manifest = {
                "report_id": report.report_id,
                "created_at": report.created_at,
                "files": [self._file_record(final_json), self._file_record(final_excel)],
            }
            temp_manifest = self._temporary(destination, ".json")
            temporary.append(temp_manifest)
            temp_manifest.write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            self._sync_file(temp_manifest)
            os.replace(temp_manifest, final_manifest)
            self._sync_directory(destination)
            return ExportResult(final_json, final_excel, final_manifest)
        finally:
            for path in temporary:
                path.unlink(missing_ok=True)

    @staticmethod
    def _stem(report: InventoryReport) -> str:
        timestamp = report.created_at.replace(":", "").replace("-", "")
        model = safe_filename_component(report.system.get("product_name"))
        serial = safe_filename_component(report.system.get("serial_number"))
        return f"{timestamp}_{model}_{serial}_{report.report_id[:8]}"

    @staticmethod
    def _temporary(destination: Path, suffix: str) -> Path:
        with tempfile.NamedTemporaryFile(
            prefix=".hwscan-part-", suffix=suffix, dir=destination, delete=False
        ) as handle:
            path = Path(handle.name)
        return path

    @staticmethod
    def _sync_file(path: Path) -> None:
        with path.open("rb") as handle:
            os.fsync(handle.fileno())

    @staticmethod
    def _sync_directory(path: Path) -> None:
        descriptor = os.open(path, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

    @staticmethod
    def _file_record(path: Path) -> dict[str, str | int]:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        return {"name": path.name, "bytes": path.stat().st_size, "sha256": digest}
