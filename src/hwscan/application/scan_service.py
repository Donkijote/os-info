from __future__ import annotations

from pathlib import Path

from hwscan.domain.models import InventoryReport
from hwscan.infrastructure.collectors.fixture import FixtureCollector


class ScanService:
    def collect_fixtures(self, fixture_dir: Path) -> InventoryReport:
        return FixtureCollector(fixture_dir).collect()
