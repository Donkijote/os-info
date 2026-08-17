from pathlib import Path

from hwscan.application.export_service import ExportService
from hwscan.application.scan_service import ScanService
from hwscan.ui.view_model import ScanViewModel, ViewState

FIXTURE = Path("tests/fixtures/dell/latitude-7420")


def test_scan_edit_and_export_workflow(tmp_path: Path) -> None:
    view_model = ScanViewModel(ScanService(), ExportService())
    report = view_model.scan_fixtures(FIXTURE)
    assert view_model.state is ViewState.COMPLETED
    view_model.set_operator_input(asset_tag="ASSET-001", operator="Test Operator")
    result = view_model.export(tmp_path)
    assert report.operator_input.asset_tag == "ASSET-001"
    assert result.excel_path.exists()
    assert view_model.state is ViewState.EXPORTED
