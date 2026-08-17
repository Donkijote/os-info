from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from hwscan.domain.models import (
    CollectionStatus,
    Diagnostic,
    InventoryReport,
    ScannerInfo,
    Severity,
    SourceRecord,
    new_report,
)
from hwscan.domain.normalization import clean_identifier, clean_text, integer_or_none, percentage


class FixtureCollectionError(RuntimeError):
    pass


class FixtureCollector:
    """Build a report from scrubbed collector fixtures without requiring Linux."""

    def __init__(self, fixture_dir: Path) -> None:
        self.fixture_dir = fixture_dir

    def collect(self) -> InventoryReport:
        scanner_data = self._required_json("scanner.json")
        report = new_report(
            ScannerInfo(
                app_version=clean_text(scanner_data.get("app_version")) or "development",
                image_build_id=clean_text(scanner_data.get("image_build_id")) or "fixture",
                os=clean_text(scanner_data.get("os")) or "Linux fixture",
                kernel=clean_text(scanner_data.get("kernel")) or "unknown",
                architecture=clean_text(scanner_data.get("architecture")) or "unknown",
            )
        )
        report.sources.append(self._source("scanner.json", "fixture-scanner"))
        self._collect_identity(report)
        self._collect_cpu(report)
        self._collect_storage(report)
        self._collect_graphics(report)
        self._collect_network(report)
        self._collect_battery(report)
        self._collect_boot(report)
        report.validate_basic()
        return report

    def _collect_identity(self, report: InventoryReport) -> None:
        data = self._required_json("dmi.json")
        system = data.get("system", {})
        board = data.get("board", {})
        firmware = data.get("firmware", {})
        report.system = {
            "manufacturer": clean_text(system.get("manufacturer")),
            "product_name": clean_text(system.get("product_name")),
            "version": clean_text(system.get("version")),
            "family": clean_text(system.get("family")),
            "sku": clean_identifier(system.get("sku")),
            "serial_number": clean_identifier(system.get("serial_number")),
            "uuid": clean_identifier(system.get("uuid")),
            "asset_tag": clean_identifier(system.get("asset_tag")),
            "board": {
                "manufacturer": clean_text(board.get("manufacturer")),
                "product": clean_text(board.get("product")),
                "version": clean_text(board.get("version")),
                "serial_number": clean_identifier(board.get("serial_number")),
            },
            "firmware": {
                "vendor": clean_text(firmware.get("vendor")),
                "version": clean_text(firmware.get("version")),
                "release_date": clean_text(firmware.get("release_date")),
            },
        }
        memory = data.get("memory", {})
        modules = []
        for module in memory.get("modules", []):
            modules.append(
                {
                    "locator": clean_text(module.get("locator")),
                    "bank_locator": clean_text(module.get("bank_locator")),
                    "size_bytes": integer_or_none(module.get("size_bytes")),
                    "memory_type": clean_text(module.get("memory_type")),
                    "form_factor": clean_text(module.get("form_factor")),
                    "configured_speed_mt_s": integer_or_none(module.get("configured_speed_mt_s")),
                    "manufacturer": clean_text(module.get("manufacturer")),
                    "part_number": clean_identifier(module.get("part_number")),
                    "serial_number": clean_identifier(module.get("serial_number")),
                    "status": clean_text(module.get("status")) or "unknown",
                }
            )
        report.memory = {
            "installed_bytes": integer_or_none(memory.get("installed_bytes")),
            "usable_bytes": integer_or_none(memory.get("usable_bytes")),
            "slots_total": integer_or_none(memory.get("slots_total")),
            "slots_populated": sum(1 for module in modules if module.get("size_bytes")),
            "modules": modules,
        }
        report.sources.append(self._source("dmi.json", "fixture-dmi"))

    def _collect_cpu(self, report: InventoryReport) -> None:
        data = self._required_json("lscpu.json")
        fields = {
            str(item.get("field", "")).rstrip(":"): item.get("data")
            for item in data.get("lscpu", [])
        }
        logical = integer_or_none(fields.get("CPU(s)"))
        cores_per_socket = integer_or_none(fields.get("Core(s) per socket"))
        sockets = integer_or_none(fields.get("Socket(s)"))
        physical = cores_per_socket * sockets if cores_per_socket and sockets else None
        report.cpus = [
            {
                "model_name": clean_text(fields.get("Model name")),
                "architecture": clean_text(fields.get("Architecture")),
                "sockets": sockets,
                "physical_cores": physical,
                "logical_cpus": logical,
                "threads_per_core": integer_or_none(fields.get("Thread(s) per core")),
                "max_mhz": _float_or_none(fields.get("CPU max MHz")),
                "min_mhz": _float_or_none(fields.get("CPU min MHz")),
                "virtualization": clean_text(fields.get("Virtualization")),
            }
        ]
        report.sources.append(self._source("lscpu.json", "fixture-lscpu"))

    def _collect_storage(self, report: InventoryReport) -> None:
        data = self._required_json("lsblk.json")
        health = self._optional_json("smartctl.json") or {"devices": {}}
        for index, device in enumerate(data.get("blockdevices", []), start=1):
            if device.get("type") != "disk":
                continue
            path = clean_text(device.get("path")) or f"/dev/{device.get('name', 'unknown')}"
            smart = health.get("devices", {}).get(path, {})
            percentage_used = integer_or_none(smart.get("nvme_percentage_used"))
            remaining = None
            if percentage_used is not None:
                remaining = max(0, min(100, 100 - percentage_used))
            report.storage.append(
                {
                    "id": f"storage-{index}",
                    "path": path,
                    "device_type": "disk",
                    "transport": clean_text(device.get("tran")),
                    "removable": bool(device.get("rm", False)),
                    "vendor": clean_text(device.get("vendor")),
                    "model": clean_text(device.get("model")),
                    "serial_number": clean_identifier(device.get("serial")),
                    "firmware_version": clean_text(smart.get("firmware_version")),
                    "wwn": clean_identifier(device.get("wwn")),
                    "capacity_bytes": integer_or_none(device.get("size")),
                    "rotational": bool(device.get("rota", False)),
                    "smart_available": bool(smart),
                    "smart_overall": clean_text(smart.get("smart_overall")) or "unknown",
                    "temperature_c": integer_or_none(smart.get("temperature_c")),
                    "power_on_hours": integer_or_none(smart.get("power_on_hours")),
                    "power_cycles": integer_or_none(smart.get("power_cycles")),
                    "unsafe_shutdowns": integer_or_none(smart.get("unsafe_shutdowns")),
                    "nvme_percentage_used": percentage_used,
                    "nvme_available_spare_percent": integer_or_none(
                        smart.get("nvme_available_spare_percent")
                    ),
                    "estimated_life_remaining_percent": remaining,
                    "collection_status": "ok" if smart else "unknown",
                }
            )
            if not smart:
                report.diagnostics.append(
                    Diagnostic(
                        severity=Severity.WARNING,
                        domain="storage",
                        code="HEALTH_DATA_UNAVAILABLE",
                        message=f"Health data was not supplied for {path}.",
                        device_ref=f"storage-{index}",
                    )
                )
        report.sources.append(self._source("lsblk.json", "fixture-lsblk"))
        if (self.fixture_dir / "smartctl.json").exists():
            report.sources.append(self._source("smartctl.json", "fixture-smartctl"))

    def _collect_graphics(self, report: InventoryReport) -> None:
        data = self._optional_json("graphics.json") or {"devices": []}
        report.graphics = [dict(item) for item in data.get("devices", [])]
        if (self.fixture_dir / "graphics.json").exists():
            report.sources.append(self._source("graphics.json", "fixture-graphics"))

    def _collect_network(self, report: InventoryReport) -> None:
        data = self._optional_json("ip-link.json") or []
        for item in data:
            interface = clean_text(item.get("ifname"))
            if interface == "lo":
                continue
            report.network.append(
                {
                    "interface": interface,
                    "mac_address": clean_identifier(item.get("address")),
                    "permanent_mac": clean_identifier(item.get("permaddr")),
                    "link_state": clean_text(item.get("operstate")),
                    "type": clean_text(item.get("link_type")),
                }
            )
        if (self.fixture_dir / "ip-link.json").exists():
            report.sources.append(self._source("ip-link.json", "fixture-ip-link"))

    def _collect_battery(self, report: InventoryReport) -> None:
        data = self._optional_json("battery.json") or {"batteries": []}
        for item in data.get("batteries", []):
            design = integer_or_none(item.get("design_energy_mwh"))
            full = integer_or_none(item.get("full_energy_mwh"))
            report.batteries.append(
                {
                    "manufacturer": clean_text(item.get("manufacturer")),
                    "model": clean_text(item.get("model")),
                    "serial_number": clean_identifier(item.get("serial_number")),
                    "technology": clean_text(item.get("technology")),
                    "design_energy_mwh": design,
                    "full_energy_mwh": full,
                    "cycle_count": integer_or_none(item.get("cycle_count")),
                    "health_percent": percentage(full, design),
                }
            )
        if (self.fixture_dir / "battery.json").exists():
            report.sources.append(self._source("battery.json", "fixture-battery"))

    def _collect_boot(self, report: InventoryReport) -> None:
        data = self._optional_json("boot.json") or {}
        report.boot = {
            "mode": clean_text(data.get("mode")) or "unknown",
            "secure_boot": clean_text(data.get("secure_boot")) or "unknown",
            "live_medium_device": clean_text(data.get("live_medium_device")),
            "reports_partition_device": clean_text(data.get("reports_partition_device")),
        }
        report.security = {"tpm_present": data.get("tpm_present")}
        if (self.fixture_dir / "boot.json").exists():
            report.sources.append(self._source("boot.json", "fixture-boot"))

    def _required_json(self, filename: str) -> dict[str, Any]:
        data = self._load_json(filename)
        if not isinstance(data, dict):
            raise FixtureCollectionError(f"{filename} must contain a JSON object")
        return data

    def _optional_json(self, filename: str) -> Any:
        path = self.fixture_dir / filename
        return self._load_json(filename) if path.exists() else None

    def _load_json(self, filename: str) -> Any:
        path = self.fixture_dir / filename
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise FixtureCollectionError(f"required fixture is missing: {filename}") from error
        except json.JSONDecodeError as error:
            raise FixtureCollectionError(f"invalid JSON fixture {filename}: {error}") from error

    def _source(self, filename: str, source_id: str) -> SourceRecord:
        path = self.fixture_dir / filename
        raw = path.read_bytes()
        created_at = datetime.fromtimestamp(path.stat().st_mtime, UTC).replace(microsecond=0)
        return SourceRecord(
            id=source_id,
            collector="fixture",
            tool=filename,
            tool_version=None,
            status=CollectionStatus.OK,
            exit_code=0,
            duration_ms=0,
            started_at=created_at.isoformat().replace("+00:00", "Z"),
            raw_sha256=hashlib.sha256(raw).hexdigest(),
        )


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError, OverflowError):
        return None
