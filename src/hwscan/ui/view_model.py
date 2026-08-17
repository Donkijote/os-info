from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from hwscan.application.export_service import ExportResult, ExportService
from hwscan.application.scan_service import ScanService
from hwscan.domain.models import InventoryReport, OperatorInput


class ViewState(StrEnum):
    READY = "ready"
    SCANNING = "scanning"
    COMPLETED = "completed"
    COMPLETED_WITH_WARNINGS = "completed_with_warnings"
    FAILED = "failed"
    EXPORTED = "exported"


@dataclass(slots=True)
class ScanViewModel:
    scan_service: ScanService
    export_service: ExportService
    state: ViewState = ViewState.READY
    report: InventoryReport | None = None
    error_message: str | None = None
    last_export: ExportResult | None = None

    def scan_fixtures(self, fixture_dir: Path) -> InventoryReport:
        self.state = ViewState.SCANNING
        self.error_message = None
        try:
            report = self.scan_service.collect_fixtures(fixture_dir)
        except Exception as error:
            self.state = ViewState.FAILED
            self.error_message = str(error)
            raise
        self.report = report
        self.state = (
            ViewState.COMPLETED_WITH_WARNINGS if report.diagnostics else ViewState.COMPLETED
        )
        return report

    def set_operator_input(
        self,
        *,
        asset_tag: str | None = None,
        operator: str | None = None,
        location: str | None = None,
        notes: str | None = None,
    ) -> None:
        if self.report is None:
            raise RuntimeError("scan before setting operator input")
        self.report.operator_input = OperatorInput(asset_tag, operator, location, notes)

    def export(self, destination: Path) -> ExportResult:
        if self.report is None:
            raise RuntimeError("scan before exporting")
        self.last_export = self.export_service.export(self.report, destination)
        self.state = ViewState.EXPORTED
        return self.last_export
