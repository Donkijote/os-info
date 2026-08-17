from __future__ import annotations

import argparse
import json
from pathlib import Path

from hwscan.application.export_service import ExportService
from hwscan.application.scan_service import ScanService
from hwscan.infrastructure.exporters.json_exporter import write_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hwscan", description="HWScan USB development CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    collect = subparsers.add_parser("collect", help="Create normalized JSON from fixtures")
    collect.add_argument("--fixture-dir", type=Path, required=True)
    collect.add_argument("--output", type=Path, required=True)

    export = subparsers.add_parser("export", help="Create JSON and Excel reports from fixtures")
    export.add_argument("--fixture-dir", type=Path, required=True)
    export.add_argument("--destination", type=Path, required=True)

    ui = subparsers.add_parser("ui", help="Open the development UI with fixture data")
    ui.add_argument("--fixture-dir", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "ui":
        from hwscan.ui.app import run

        run(args.fixture_dir)
        return 0

    report = ScanService().collect_fixtures(args.fixture_dir)
    if args.command == "collect":
        args.output.parent.mkdir(parents=True, exist_ok=True)
        write_json(report, args.output)
        print(json.dumps({"report_id": report.report_id, "output": str(args.output)}))
        return 0
    result = ExportService().export(report, args.destination)
    print(
        json.dumps(
            {
                "report_id": report.report_id,
                "json": str(result.json_path),
                "excel": str(result.excel_path),
                "manifest": str(result.manifest_path),
            }
        )
    )
    return 0
